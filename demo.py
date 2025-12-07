import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
import os

# Add src to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import get_sp500_tickers, download_data
from strategies import BacktestEngine
from scenarios import apply_income_withdrawal
from config import IMAGE_DIR, DATA_DIR

def show_image(title, filename):
    """Helper to display an image in the demo flow."""
    print(f"\n[DEMO] Displaying: {title}")
    filepath = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(filepath):
        try:
            img = mpimg.imread(filepath)
            plt.figure(figsize=(12, 8))
            plt.imshow(img)
            plt.axis('off')
            plt.title(title)
            plt.show(block=True) # Pause until closed
        except Exception as e:
            print(f"Could not open image: {e}")
    else:
        print(f"File not found: {filepath}")

def main():
    print("===================================================")
    print("   TAX IS ALL YOU NEED: PROJECT DEMO")
    print("===================================================")
    print("This demo walks through the key components of the analysis.")
    input("Press Enter to start...")

    # 1. Data Loading
    print("\n[1] DATA & UNIVERSE")
    tickers = get_sp500_tickers()
    print(f"Universe: Top {len(tickers)} S&P 500 Constituents")
    print("Period: 2004-2024 (20 Years)")
    
    # Load from local CSV in results/ if available
    data_path = os.path.join(DATA_DIR, "sp500_data.csv")
    if os.path.exists(data_path):
        print(f"Loading cached data from {data_path}...")
        data = pd.read_csv(data_path, index_col=0, parse_dates=True)
    else:
        print("Cached data not found. Downloading...")
        data = download_data(tickers)
        
    print(f"Data Shape: {data.shape} (Rows, Cols)")
    input("Press Enter to run simulations...")

    # 2. Strategies
    print("\n[2] RUNNING STRATEGIES (Income Scenario)")
    engine = BacktestEngine(tickers, data)
    
    # We run the key comparisons on the fly to prove code works
    print("Running Baseline...")
    res_base = engine.run_baseline(scenario_func=apply_income_withdrawal)
    print(f" > Final Wealth: ${res_base['Final Wealth']:,.0f}")
    
    print("Running Greedy (No Wash - Ideal)...")
    res_ideal = engine.run_greedy_no_wash(scenario_func=apply_income_withdrawal)
    print(f" > Final Wealth: ${res_ideal['Final Wealth']:,.0f}")
    
    print("Running Greedy (With Wash - Compliant)...")
    res_real = engine.run_greedy_with_wash(scenario_func=apply_income_withdrawal)
    print(f" > Final Wealth: ${res_real['Final Wealth']:,.0f}")
    
    input("Press Enter to view Results Visualization...")

    # 3. Visualization Walkthrough
    print("\n[3] VISUALIZATION WALKTHROUGH")
    print("Opening Wealth Curves...")
    show_image("Wealth Accumulation (Income Scenario)", "wealth_curves_wealth_over_time_-_income_withdrawal.png")
    
    print("Opening Drawdowns...")
    show_image("Drawdowns (Income Scenario)", "drawdowns_drawdowns_-_income_withdrawal.png")
    
    print("Opening Metric Comparisons...")
    show_image("Final Wealth Comparison", "comparison_final_wealth.png")
    
    print("\n[4] KEY CONCLUSION")
    print("The 'With Wash' strategy underperforms the Baseline due to 'Cash Drag'.")
    print("In a strong bull market (2004-2024), missing 30 days of returns is costlier than the tax benefit.")
    
    print("\nDemo Complete.")

if __name__ == "__main__":
    main()
