import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
import os
import time

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import get_sp500_tickers, download_data
from strategies import BacktestEngine
from scenarios import apply_income_withdrawal
from config import IMAGE_DIR, DATA_DIR

def clear_screen():
    """Clears the terminal screen for a cleaner demo effect."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_image(title, filename):
    """Helper to pop up an image without crashing if it's missing."""
    print(f"\nOpening chart: {title}...")
    filepath = os.path.join(IMAGE_DIR, filename)
    
    if os.path.exists(filepath):
        try:
            img = mpimg.imread(filepath)
            plt.figure(figsize=(12, 8))
            plt.imshow(img)
            plt.axis('off')
            plt.title(title, fontsize=16)
            plt.show(block=True) # Pauses execution until the window is closed
            print(" (Chart closed)")
        except Exception as e:
            print(f" [!] Couldn't open image (Error: {e})")
    else:
        print(f" [!] Image file not found: {filepath}")

def main():
    clear_screen()
    print("\n" + "="*60)
    print("   TAX IS ALL YOU NEED: Project Demo")
    print("   (20-Year Tax-Loss Harvesting Simulation)")
    print("="*60 + "\n")
    
    print("Hi! This script walks through our backtesting logic and results.")
    print("We'll look at how much 'Alpha' we can generate just by being smart with taxes.\n")
    
    input(">> Press Enter to start the simulation...")

    # 1. Data Setup
    print("\nStep 1: Market Data Setup")
    print("-" * 30)
    tickers = get_sp500_tickers()
    print(f"Universe: Top {len(tickers)} S&P 500 Constituents")
    print("Period:   2004 - 2024 (20 Years)")
    
    # Try loading local cache first to be fast
    data_path = os.path.join(DATA_DIR, "sp500_data.csv")
    if os.path.exists(data_path):
        print(f"Status:   Loaded cached data from {data_path}")
        data = pd.read_csv(data_path, index_col=0, parse_dates=True)
    else:
        print("Status:   Downloading fresh data from Yahoo Finance...")
        data = download_data(tickers)
        
    print(f"Records:  {data.shape[0]} trading days")
    
    input("\n>> Press Enter to run the strategies...")

    # 2. Run Simulations
    print("\nStep 2: Running Backtests (Income Scenario)")
    print("-" * 30)
    print("Scenario: Withdraw 5% annually, Liquidate at Year 20.")
    
    engine = BacktestEngine(tickers, data)
    
    # Helper to print nice results
    def print_result(name, result):
        print(f"  • {name:<30} | Final Wealth: ${result['Final Wealth']:,.0f}")

    # Baseline
    print("\n> Simulating Baseline (Buy & Hold)...")
    res_base = engine.run_baseline(scenario_func=apply_income_withdrawal)
    print_result("Baseline", res_base)
    
    # Ideal Case
    print("> Simulating Greedy (No Wash Rule)...")
    res_ideal = engine.run_greedy_no_wash(scenario_func=apply_income_withdrawal)
    print_result("Greedy (No Wash - Ideal)", res_ideal)
    
    # Realistic Case
    print("> Simulating Greedy (With Wash Rule)...")
    res_real = engine.run_greedy_with_wash(scenario_func=apply_income_withdrawal)
    print_result("Greedy (With Wash - Realistic)", res_real)
    
    print("\nAnalysis:")
    print(" Notice how the 'No Wash' strategy beats the Baseline (Tax Alpha).")
    print(" But the 'With Wash' strategy loses money because of Cash Drag (sitting out of the market).")
    
    input("\n>> Press Enter to see the charts...")

    # 3. Visualizations
    print("\nStep 3: Visualizing Results")
    print("-" * 30)
    print("I'll open a few charts to show exactly what happened.\n")
    
    show_image("1. Wealth Accumulation (The cost of Cash Drag)", "wealth_curves_wealth_over_time_-_income_withdrawal.png")
    show_image("2. Drawdowns (Risk Profile)", "drawdowns_drawdowns_-_income_withdrawal.png")
    show_image("3. Comparison Summary", "comparison_final_wealth.png")
    
    print("\n" + "="*60)
    print("   DEMO COMPLETE")
    print("="*60)
    print("Thanks for watching! The full PDF report is in the repo root.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Demo cancelled by user.")
        sys.exit(0)