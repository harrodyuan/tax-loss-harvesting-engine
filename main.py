import pandas as pd
from data_loader import get_sp500_tickers, download_data
from strategies import BacktestEngine
from scenarios import apply_income_withdrawal, apply_charitable_giving
import visualization
import matplotlib.pyplot as plt

from config import INITIAL_CASH

def main():
    print("Starting Tax-Loss Harvesting Backtesting Engine...")
    
    # 1. Load Data
    tickers = get_sp500_tickers()
    try:
        data = download_data(tickers)
    except Exception as e:
        print(f"Error downloading data: {e}")
        return

    if data.empty:
        print("No data downloaded.")
        return

    # 2. Initialize Engine
    engine = BacktestEngine(tickers, data)
    
    strategies = [
        ("Baseline (No Harvesting)", engine.run_baseline),
        ("Greedy (No Wash Rule)", engine.run_greedy_no_wash),
        ("Greedy (With Wash Rule)", engine.run_greedy_with_wash),
        ("Optimized (Tax Aware)", engine.run_optimized_tax_aware)
    ]
    
    scenarios = [
        ("Income Withdrawal", apply_income_withdrawal),
        ("Charitable Giving", apply_charitable_giving)
    ]
    
    results = []
    
    # Store history for plotting
    # Nested dict: history[Scenario][Strategy] = Series
    history = {}

    # 3. Run Simulations
    for scen_name, scen_func in scenarios:
        history[scen_name] = {}
        for strat_name, strat_func in strategies:
            print(f"Running {strat_name} with {scen_name}...")
            metrics = strat_func(scenario_func=scen_func)
            
            # Extract history
            hist_series = metrics.pop("History")
            history[scen_name][strat_name] = hist_series
            
            # Calculate CAGR
            years = 10
            final_val = metrics['Final Wealth']
            cagr = (final_val / INITIAL_CASH) ** (1/years) - 1
            
            # Calculate Net Tax Impact (Tax Paid - Tax Credits?)
            # Or simply Tax Paid vs Tax Savings. 
            # Group 7 defines Net Tax Impact likely as value added from tax strategy.
            # For simplicity, we'll define it as: (Final Wealth - Baseline Final Wealth) / Initial Cash
            # But to be precise, let's stick to the metrics we have: Total Taxes Paid.
            # We will add a computed field "Net Tax Impact" as (Tax Savings from Losses - Taxes Paid).
            # Tax Savings = Realized Losses * 0.20
            tax_savings = metrics['Total Realized Losses'] * 0.20
            net_tax_impact = tax_savings - metrics['Total Taxes Paid']

            res = {
                "Strategy": strat_name,
                "Scenario": scen_name,
                "CAGR": cagr,
                "Net Tax Impact": net_tax_impact,
                **metrics
            }
            results.append(res)
            print(f"Completed. Final Wealth: ${metrics['Final Wealth']:,.2f}")

    # 4. Print Summary
    print("\n" + "="*80)
    print("FINAL RESULTS SUMMARY")
    print("="*80)
    
    df_results = pd.DataFrame(results)
    # Reorder columns
    cols = ["Strategy", "Scenario", "Final Wealth", "CAGR", "Net Tax Impact", "Total Taxes Paid", "Total Realized Losses", "Tracking Error"]
    df_results = df_results[cols]
    
    # Format
    pd.options.display.float_format = '{:,.2f}'.format
    print(df_results.to_string(index=False))
    
    # Save to CSV
    df_results.to_csv("backtest_results.csv", index=False)
    print("\nResults saved to backtest_results.csv")

    # 5. Visualizations
    print("\nGenerating Visualizations...")
    
    # Plot Wealth Curves for each Scenario
    for scen_name, strategies_data in history.items():
        visualization.plot_wealth_curves(strategies_data, title=f"Wealth Over Time - {scen_name}")
        visualization.plot_drawdowns(strategies_data, title=f"Drawdowns - {scen_name}")

    # Plot Comparison Metrics
    visualization.plot_metrics_comparison(df_results)
    visualization.plot_tax_efficiency(df_results)

if __name__ == "__main__":
    main()
