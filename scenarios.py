from portfolio import Portfolio
from config import TAX_RATE

def apply_income_withdrawal(portfolio: Portfolio, current_prices: dict, year: int):
    """
    Withdraw 5% of AUM. Calculate tax bill on liquidation.
    """
    total_value = portfolio.get_total_value(current_prices)
    withdrawal_amount = total_value * 0.05
    
    # Check if we have enough cash
    if portfolio.cash < withdrawal_amount:
        needed = withdrawal_amount - portfolio.cash
        # Liquidate pro-rata or specific? 
        # Usually standard withdrawal is pro-rata or HIFO.
        # We'll use HIFO to minimize tax impact of the withdrawal itself.
        # We need to raise 'needed' cash.
        
        # Simple approach: Sell specific amount from each holding? 
        # Or just call HIFO on everything until we have cash?
        # Let's iterate tickers and sell HIFO.
        
        # We need to know which tickers to sell. 
        # Let's try to sell proportionally from all holdings to maintain balance?
        # Or just pick one?
        # AUM withdrawal usually implies selling across the board.
        # Let's sell 5% of shares of EACH ticker (pro-rata withdrawal).
        
        for ticker, lots in portfolio.holdings.items():
            current_price = current_prices.get(ticker, 0)
            if current_price > 0:
                # Sell 5% of shares of this ticker?
                # No, we need a specific dollar amount 'needed'. 
                # But 'withdrawal_amount' is 5% of TOTAL value.
                # So selling 5% of EACH position (and 5% of cash) covers it exactly.
                
                # Sell 5% of shares
                total_shares = sum(lot.shares for lot in lots)
                shares_to_sell = total_shares * 0.05
                portfolio.hifo_liquidation(ticker, shares_to_sell, current_price)
    
    portfolio.cash -= withdrawal_amount
    # Tax bill is handled by realized gains in portfolio during HIFO.
    # But the prompt says "Calculate tax bill on liquidation."
    # The portfolio tracks 'realized_gains' and 'realized_losses'.
    # We just let the portfolio track it.

def apply_charitable_giving(portfolio: Portfolio, current_prices: dict, year: int):
    """
    Charitable giving: in addition to the initial $10M, you will make additional contributions
    of $1M at the end of year 1, 2, . . . , N − 1. At the end of year N , your entire portfolio will
    be donate to your favorite non-profit institution (e.g., Carnegie Mellon) and thus there
    will be no any taxes paid at that final time.
    """
    # 1. Annual Contribution of $1M
    contribution_amount = 1_000_000
    portfolio.cash += contribution_amount

    # Donation logic is terminal. Handled by main loop calling liquidate_for_donation at end of sim.
    
def liquidate_for_donation(portfolio: Portfolio, current_prices: dict):
    """
    Liquidates entire portfolio with 0% tax (Donation).
    Sets realized gains to 0 effectively for the liquidation part?
    Or just calculates final value without tax?
    """
    # Just sell everything.
    for ticker in list(portfolio.holdings.keys()):
        current_price = current_prices.get(ticker, 0)
        lots = portfolio.holdings[ticker]
        total_shares = sum(l.shares for l in lots)
        # We sell, but we don't want to trigger tax.
        # We can just manually clear holdings and add cash.
        proceeds = total_shares * current_price
        portfolio.cash += proceeds
    
    portfolio.holdings = {}
    # Do not update realized_gains/losses for this step (0% tax)
