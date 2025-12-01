from typing import Dict, List, Tuple
from tax_lot import TaxLot
from config import TAX_RATE, INITIAL_CASH

class Portfolio:
    def __init__(self):
        self.cash = INITIAL_CASH
        self.holdings: Dict[str, List[TaxLot]] = {}
        self.realized_gains = 0.0
        self.realized_losses = 0.0
        self.total_tax_paid = 0.0

    @property
    def tax_bill_ytd(self) -> float:
        """
        Calculates estimated tax bill based on net realized P&L.
        Tax is 20% on net gains. Losses offset gains.
        """
        net_pl = self.realized_gains - self.realized_losses
        if net_pl > 0:
            return net_pl * TAX_RATE
        return 0.0

    def add_lot(self, lot: TaxLot):
        if lot.ticker not in self.holdings:
            self.holdings[lot.ticker] = []
        self.holdings[lot.ticker].append(lot)

    def hifo_liquidation(self, ticker: str, quantity: float, price: float, use_tax_credit: bool = False) -> float:
        """
        Sells shares with highest cost basis first.
        Returns total realized G/L from the sale.
        If use_tax_credit is True, adds tax_savings from losses immediately to cash.
        """
        if ticker not in self.holdings:
            return 0.0
        
        # Sort lots by cost basis descending (HIFO)
        self.holdings[ticker].sort(key=lambda x: x.cost_basis, reverse=True)
        
        shares_to_sell = quantity
        realized_gl = 0.0
        remaining_lots = []
        
        for lot in self.holdings[ticker]:
            if shares_to_sell <= 0:
                remaining_lots.append(lot)
                continue
                
            if lot.shares <= shares_to_sell:
                # Sell entire lot
                proceeds = lot.shares * price
                cost = lot.shares * lot.cost_basis
                gl = proceeds - cost
                realized_gl += gl
                shares_to_sell -= lot.shares
                self.cash += proceeds
                # Log gain or loss
                if gl > 0:
                    self.realized_gains += gl
                else:
                    self.realized_losses += abs(gl)
                    if use_tax_credit:
                        self.cash += abs(gl) * TAX_RATE
            else:
                # Sell partial lot
                proceeds = shares_to_sell * price
                cost = shares_to_sell * lot.cost_basis
                gl = proceeds - cost
                realized_gl += gl
                
                # Update lot
                lot.shares -= shares_to_sell
                remaining_lots.append(lot) # Keep the rest
                
                self.cash += proceeds
                if gl > 0:
                    self.realized_gains += gl
                else:
                    self.realized_losses += abs(gl)
                    if use_tax_credit:
                        self.cash += abs(gl) * TAX_RATE
                shares_to_sell = 0
        
        self.holdings[ticker] = remaining_lots
        # Cleanup empty keys
        if not self.holdings[ticker]:
            del self.holdings[ticker]
            
        return realized_gl

    def harvest_losses(self, current_prices: Dict[str, float], threshold: float = -0.05, use_tax_credit: bool = False) -> Dict[str, float]:
        """
        Scans all lots. If (Price < Basis * (1+threshold)), trigger a sell.
        Returns a dictionary of {ticker: quantity_sold} and updates realized losses.
        If use_tax_credit is True, adds tax_savings from losses immediately to cash.
        """
        sold_quantities = {}
        
        for ticker, lots in list(self.holdings.items()):
            if ticker not in current_prices:
                continue
            
            price = current_prices[ticker]
            
            new_lots = []
            ticker_sold_qty = 0.0
            
            for lot in lots:
                # Check loss threshold
                if price < lot.cost_basis * (1 + threshold):
                    # Sell this lot
                    proceeds = lot.shares * price
                    cost = lot.shares * lot.cost_basis
                    gl = proceeds - cost
                    # gl should be negative here
                    loss = abs(gl)
                    self.realized_losses += loss 
                    self.cash += proceeds
                    if use_tax_credit:
                        self.cash += loss * TAX_RATE
                    ticker_sold_qty += lot.shares
                else:
                    new_lots.append(lot)
            
            if ticker_sold_qty > 0:
                self.holdings[ticker] = new_lots
                sold_quantities[ticker] = ticker_sold_qty
                if not self.holdings[ticker]:
                    del self.holdings[ticker]

        return sold_quantities
    
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        value = self.cash
        for ticker, lots in self.holdings.items():
            if ticker in current_prices:
                value += sum(lot.shares for lot in lots) * current_prices[ticker]
        return value

