import pandas as pd
import numpy as np
import cvxpy as cp
import datetime
from typing import List, Dict, Set, Callable, Optional
from dataclasses import replace

from config import INITIAL_CASH, TOP_N_STOCKS, WASH_SALE_DAYS, HARVEST_THRESHOLD
from portfolio import Portfolio
from tax_lot import TaxLot
import scenarios

class BacktestEngine:
    def __init__(self, tickers: List[str], data: pd.DataFrame):
        self.tickers = tickers
        self.data = data
        self.portfolio = Portfolio()
        self.wash_sale_log: Dict[str, datetime.date] = {} # ticker -> date of last loss sale

    def _get_restricted_tickers(self, current_date: datetime.date) -> Set[str]:
        """Returns set of tickers currently under wash sale restriction."""
        restricted = set()
        for ticker, loss_date in list(self.wash_sale_log.items()):
            days_passed = (current_date - loss_date).days
            if days_passed <= WASH_SALE_DAYS:
                restricted.add(ticker)
            else:
                # Clean up old entries
                del self.wash_sale_log[ticker]
        return restricted

    def _rebalance_portfolio(self, weights: Dict[str, float], current_prices: Dict[str, float], date: datetime.date):
        """
        Rebalances portfolio to match target weights.
        Sells overweight positions (HIFO) and buys underweight positions.
        """
        total_value = self.portfolio.get_total_value(current_prices)
        
        # 1. Sell Overweight
        for ticker in list(self.portfolio.holdings.keys()):
            current_price = current_prices.get(ticker, 0)
            if current_price == 0: continue
            
            target_w = weights.get(ticker, 0.0)
            target_val = total_value * target_w
            
            current_lots = self.portfolio.holdings[ticker]
            current_shares = sum(l.shares for l in current_lots)
            current_val = current_shares * current_price
            
            if current_val > target_val:
                # Sell excess
                excess_val = current_val - target_val
                shares_to_sell = excess_val / current_price
                self.portfolio.hifo_liquidation(ticker, shares_to_sell, current_price)

        # 2. Buy Underweight
        for ticker, weight in weights.items():
            current_price = current_prices.get(ticker, 0)
            if current_price == 0: continue
            
            target_val = total_value * weight
            
            current_lots = self.portfolio.holdings.get(ticker, [])
            current_shares = sum(l.shares for l in current_lots)
            current_val = current_shares * current_price
            
            if current_val < target_val:
                needed_val = target_val - current_val
                # Allow small tolerance or cap at cash
                if needed_val > self.portfolio.cash:
                    needed_val = self.portfolio.cash
                
                if needed_val > 1.0: # Minimum trade size $1
                    shares_to_buy = needed_val / current_price
                    new_lot = TaxLot(ticker, date, shares_to_buy, current_price)
                    self.portfolio.add_lot(new_lot)
                    self.portfolio.cash -= needed_val

    def _rebalance_naive(self, current_prices: Dict[str, float], date: datetime.date, restricted_tickers: Set[str] = set()):
        """
        Rebalances to Equal Weight (1/N) for all non-restricted tickers.
        Restricted tickers get 0 weight.
        """
        eligible = [t for t in self.tickers if t not in restricted_tickers and t in current_prices]
        if not eligible:
            return

        target_weight = 1.0 / len(eligible)
        weights = {t: target_weight for t in eligible}
        
        self._rebalance_portfolio(weights, current_prices, date)

    def _calculate_tracking_error(self, portfolio_values: List[float], benchmark_values: List[float]) -> float:
        """
        Calculates annualized tracking error of returns.
        TE = Stdev(Rp - Rb)
        """
        if not portfolio_values or not benchmark_values:
            return 0.0
        
        p_returns = pd.Series(portfolio_values).pct_change().dropna()
        b_returns = pd.Series(benchmark_values).pct_change().dropna()
        
        # Align
        common_idx = p_returns.index.intersection(b_returns.index)
        if len(common_idx) < 2:
            return 0.0
            
        diff = p_returns[common_idx] - b_returns[common_idx]
        te = diff.std() * np.sqrt(252) # Annualized
        return te

    def _run_loop(self, strategy_name: str, scenario_func: Optional[Callable] = None) -> Dict:
        """
        Common loop for simulation.
        """
        self.portfolio = Portfolio() # Reset
        self.wash_sale_log = {}
        dates = self.data.index
        
        # Benchmark tracking (Equal Weight of Universe)
        # We assume benchmark starts at INITIAL_CASH and rebalances daily/monthly?
        # Simplified: Just track returns of equal weight index of these 50 stocks.
        benchmark_value = INITIAL_CASH
        benchmark_values = []
        portfolio_values = []
        
        # Pre-calculate benchmark returns (Equal Weight)
        # Daily return of EW portfolio = mean(daily returns of stocks)
        daily_returns = self.data.pct_change().mean(axis=1).fillna(0)
        
        loss_carryforward = 0.0
        cumulative_realized_losses = 0.0

        for i, date in enumerate(dates):
            current_date = date.date()
            current_prices = self.data.loc[date].to_dict()
            
            # --- STRATEGY SPECIFIC LOGIC START ---
            if strategy_name == 'baseline':
                 # No harvesting
                 # Just Monthly Rebalance
                if i == 0 or (i > 0 and date.month != dates[i-1].month):
                    self._rebalance_naive(current_prices, current_date)

            elif strategy_name == 'greedy_no_wash':
                sold = self.portfolio.harvest_losses(current_prices, threshold=HARVEST_THRESHOLD, use_tax_credit=True)
                # Immediate repurchase
                for ticker, qty in sold.items():
                    price = current_prices[ticker]
                    cost = qty * price
                    if self.portfolio.cash >= cost:
                        new_lot = TaxLot(ticker, current_date, qty, price)
                        self.portfolio.add_lot(new_lot)
                        self.portfolio.cash -= cost
                
                # Monthly Rebalance
                if i == 0 or (i > 0 and date.month != dates[i-1].month):
                    self._rebalance_naive(current_prices, current_date)

            elif strategy_name == 'greedy_with_wash':
                sold = self.portfolio.harvest_losses(current_prices, threshold=HARVEST_THRESHOLD, use_tax_credit=True)
                for ticker in sold:
                    self.wash_sale_log[ticker] = current_date
                
                if i == 0 or (i > 0 and date.month != dates[i-1].month):
                    restricted = self._get_restricted_tickers(current_date)
                    self._rebalance_naive(current_prices, current_date, restricted)

            elif strategy_name == 'optimized':
                sold = self.portfolio.harvest_losses(current_prices, threshold=HARVEST_THRESHOLD, use_tax_credit=True)
                for ticker in sold:
                    self.wash_sale_log[ticker] = current_date
                
                if i == 0 or (i > 0 and date.month != dates[i-1].month):
                    restricted = self._get_restricted_tickers(current_date)
                    self._run_optimization(i, current_prices, current_date, restricted)
            
            # --- STRATEGY SPECIFIC LOGIC END ---

            # Benchmark update
            if i > 0:
                benchmark_value *= (1 + daily_returns.iloc[i])
            benchmark_values.append(benchmark_value)
            
            portfolio_val = self.portfolio.get_total_value(current_prices)
            portfolio_values.append(portfolio_val)
            
            # Year End Processing
            is_year_end = False
            if i < len(dates) - 1:
                 if date.year != dates[i+1].year:
                     is_year_end = True
            elif i == len(dates) - 1:
                 is_year_end = True
            
            if is_year_end:
                # 1. Scenarios
                if scenario_func:
                    scenario_func(self.portfolio, current_prices, date.year)
                    if scenario_func.__name__ == 'apply_charitable_giving' and i == len(dates) - 1:
                        scenarios.liquidate_for_donation(self.portfolio, current_prices)
                
                # 2. Tax Calculation
                net_pl = self.portfolio.realized_gains - self.portfolio.realized_losses - loss_carryforward
                
                # Update cumulative losses
                cumulative_realized_losses += self.portfolio.realized_losses
                
                if net_pl > 0:
                    tax_due = net_pl * 0.20
                    self.portfolio.total_tax_paid += tax_due
                    self.portfolio.cash -= tax_due 
                    loss_carryforward = 0.0
                else:
                    loss_carryforward = abs(net_pl)
                
                # Reset annual counters
                self.portfolio.realized_gains = 0.0
                self.portfolio.realized_losses = 0.0

        # Metrics
        final_wealth = self.portfolio.get_total_value(self.data.iloc[-1].to_dict())
        te = self._calculate_tracking_error(portfolio_values, benchmark_values)
        
        # Create Series for history
        history_series = pd.Series(portfolio_values, index=dates)

        return {
            "Final Wealth": final_wealth,
            "Total Taxes Paid": self.portfolio.total_tax_paid,
            "Total Realized Losses": cumulative_realized_losses,
            "Tracking Error": te,
            "History": history_series
        }

    def _run_optimization(self, i, current_prices, current_date, restricted):
        # Optimization logic extracted from previous thought
        window_start = max(0, i - 252*2)
        hist_data = self.data.iloc[window_start:i+1]
        if len(hist_data) < 30:
            self._rebalance_naive(current_prices, current_date, restricted)
            return

        returns = hist_data.pct_change().dropna()
        if returns.empty:
            self._rebalance_naive(current_prices, current_date, restricted)
            return
            
        cov_matrix = returns.cov().values
        w_bench = np.array([1.0/len(self.tickers)] * len(self.tickers))
        
        n = len(self.tickers)
        w = cp.Variable(n)
        diff = w - w_bench
        objective = cp.Minimize(cp.quad_form(diff, cov_matrix))
        
        constraints = [cp.sum(w) == 1, w >= 0]
        for idx, ticker in enumerate(self.tickers):
            if ticker in restricted:
                constraints.append(w[idx] == 0)
        
        prob = cp.Problem(objective, constraints)
        try:
            prob.solve()
            if w.value is None:
                self._rebalance_naive(current_prices, current_date, restricted)
            else:
                opt_weights = {self.tickers[j]: float(v) for j, v in enumerate(w.value) if v > 1e-5}
                self._rebalance_portfolio(opt_weights, current_prices, current_date)
        except:
            self._rebalance_naive(current_prices, current_date, restricted)

    def run_baseline(self, scenario_func=None):
        return self._run_loop('baseline', scenario_func)

    def run_greedy_no_wash(self, scenario_func=None):
        return self._run_loop('greedy_no_wash', scenario_func)

    def run_greedy_with_wash(self, scenario_func=None):
        return self._run_loop('greedy_with_wash', scenario_func)

    def run_optimized_tax_aware(self, scenario_func=None):
        return self._run_loop('optimized', scenario_func)
