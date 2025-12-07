import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
import os
import time
import random

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import get_sp500_tickers, download_data
from strategies import BacktestEngine
from scenarios import apply_income_withdrawal
from config import IMAGE_DIR, DATA_DIR

# --- CYBERPUNK CONFIG ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def type_print(text, delay=0.01, color=Colors.GREEN):
    """Prints text one character at a time for a retro feel."""
    sys.stdout.write(color)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(Colors.ENDC + "\n")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    header = r"""
  _______  ___   ___      ___  ________      
 /_  __l \/ _ \ / _ \    /  |/  / __/      
  / / / _  /  \/  /_/ /   / /|_/ / _/        
 /_/ /_/|_/_/\_/\___\   /_/  /_/___/        
                                             
  TAX-LOSS HARVESTING ENGINE v2.0            
  [SYSTEM: ONLINE] [MODE: SIMULATION]        
    """
    print(Colors.CYAN + header + Colors.ENDC)

def loading_bar(duration=1.5):
    print(Colors.BLUE + "INITIALIZING..." + Colors.ENDC, end="")
    for _ in range(20):
        sys.stdout.write(Colors.CYAN + "█")
        sys.stdout.flush()
        time.sleep(duration/20)
    print(Colors.GREEN + " [OK]" + Colors.ENDC)

def show_image(title, filename):
    print(f"\n{Colors.CYAN}>> ACCESSING VISUAL: {title}...{Colors.ENDC}")
    filepath = os.path.join(IMAGE_DIR, filename)
    
    if os.path.exists(filepath):
        try:
            img = mpimg.imread(filepath)
            plt.figure(figsize=(12, 8))
            plt.imshow(img)
            plt.axis('off')
            plt.title(title, fontsize=16, color='black') # Keep title readable
            plt.show(block=True)
            print(f"{Colors.GREEN}>> VISUAL CLOSED.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL} [!] ERR: VISUAL CORRUPTED ({e}){Colors.ENDC}")
    else:
        print(f"{Colors.FAIL} [!] ERR: FILE MISSING ({filepath}){Colors.ENDC}")

def main():
    clear_screen()
    print_header()
    loading_bar()
    print("\n")
    
    type_print("WELCOME, USER.", delay=0.05)
    type_print("INITIATING PORTFOLIO BACKTEST SEQUENCE...", delay=0.03)
    
    input(f"\n{Colors.WARNING}>> PRESS ENTER TO EXECUTE CORE LOGIC...{Colors.ENDC}")

    # 1. Data Setup
    print(f"\n{Colors.HEADER}[PHASE 1] DATA ACQUISITION{Colors.ENDC}")
    tickers = get_sp500_tickers()
    print(f" > UNIVERSE: {len(tickers)} ASSETS (S&P 500 TOP CONSTITUENTS)")
    
    # Load Data
    data_path = os.path.join(DATA_DIR, "sp500_data.csv")
    if os.path.exists(data_path):
        print(f" > CACHE DETECTED: {Colors.GREEN}{data_path}{Colors.ENDC}")
        data = pd.read_csv(data_path, index_col=0, parse_dates=True)
    else:
        print(f" > CACHE MISSING. {Colors.WARNING}ESTABLISHING UPLINK TO YAHOO FINANCE...{Colors.ENDC}")
        data = download_data(tickers)
    
    # DYNAMIC DATE DETECTION
    start_date = data.index[0].strftime('%Y-%m-%d')
    end_date = data.index[-1].strftime('%Y-%m-%d')
    years = (data.index[-1] - data.index[0]).days / 365.25
    
    print(f" > TIMEFRAME: {Colors.CYAN}{start_date}{Colors.ENDC} TO {Colors.CYAN}{end_date}{Colors.ENDC}")
    print(f" > DURATION:  {Colors.CYAN}{years:.1f} YEARS{Colors.ENDC} ({data.shape[0]} TICKS)")
    
    input(f"\n{Colors.WARNING}>> PRESS ENTER TO RUN ALGORITHMS...{Colors.ENDC}")

    # 2. Run Simulations
    print(f"\n{Colors.HEADER}[PHASE 2] STRATEGY EXECUTION (SCENARIO: INCOME){Colors.ENDC}")
    print(f" > PARAMETERS: 5% WITHDRAWAL RATE | LIQUIDATION @ T=END")
    
    engine = BacktestEngine(tickers, data)
    
    # Helper to print nice results
    def print_result(name, result):
        val = result['Final Wealth']
        color = Colors.GREEN if val > 26000000 else Colors.FAIL # Dynamic coloring based on baseline
        print(f"   :: {name:<30} | {color}${val:,.0f}{Colors.ENDC}")
        time.sleep(0.2)

    print("\n PROCESSING...")
    
    # Baseline
    res_base = engine.run_baseline(scenario_func=apply_income_withdrawal)
    print_result("BASELINE (BUY & HOLD)", res_base)
    
    # Ideal Case
    res_ideal = engine.run_greedy_no_wash(scenario_func=apply_income_withdrawal)
    print_result("GREEDY (NO WASH)", res_ideal)
    
    # Realistic Case
    res_real = engine.run_greedy_with_wash(scenario_func=apply_income_withdrawal)
    print_result("GREEDY (WITH WASH)", res_real)
    
    type_print("\n[ANALYSIS COMPLETE]", delay=0.02)
    print(f"{Colors.CYAN} > OBSERVED: 'NO WASH' GENERATES ALPHA VIA TAX CREDITS.{Colors.ENDC}")
    print(f"{Colors.FAIL} > WARN: 'WITH WASH' SUFFERS CASH DRAG PENALTY.{Colors.ENDC}")
    
    input(f"\n{Colors.WARNING}>> PRESS ENTER TO RENDER VISUALS...{Colors.ENDC}")

    # 3. Visualizations
    print(f"\n{Colors.HEADER}[PHASE 3] DATA VISUALIZATION{Colors.ENDC}")
    
    show_image("WEALTH CURVE (CASH DRAG EFFECT)", "wealth_curves_wealth_over_time_-_income_withdrawal.png")
    show_image("RISK PROFILE (DRAWDOWNS)", "drawdowns_drawdowns_-_income_withdrawal.png")
    show_image("FINAL COMPARISON", "comparison_final_wealth.png")
    
    print("\n" + "="*60)
    print(f"{Colors.GREEN}   SYSTEM SHUTDOWN. SESSION SAVED.{Colors.ENDC}")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.FAIL}[!] ABORT COMMAND RECEIVED.{Colors.ENDC}")
        sys.exit(0)