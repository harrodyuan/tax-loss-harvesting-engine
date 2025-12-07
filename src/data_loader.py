import yfinance as yf
import pandas as pd
import os
from typing import List
from config import START_DATE, END_DATE, DATA_DIR

DATA_FILE = os.path.join(DATA_DIR, "sp500_data.csv")

def get_sp500_tickers() -> List[str]:
    """Returns list of top 50 S&P 500 tickers."""
    # Hardcoded list representing a snapshot of top constituents
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "TSLA", "LLY", "AVGO",
        "JPM", "V", "XOM", "UNH", "MA", "PG", "JNJ", "HD", "MRK", "COST",
        "ABBV", "CVX", "CRM", "BAC", "WMT", "AMD", "ACN", "PEP", "KO", "LIN",
        "TMO", "MCD", "DIS", "CSCO", "ABT", "INTC", "QCOM", "VZ", "CMCSA", "INTU",
        "AMGN", "PFE", "IBM", "TXN", "PM", "NEE", "NOW", "GS", "MS", "RTX"
    ]

def download_data(tickers: List[str]) -> pd.DataFrame:
    """
    Checks if data file exists. If so, loads it.
    Otherwise, uses yfinance to download daily Adjusted Close prices for the last 10 years,
    saves to CSV, and returns it.
    """
    if os.path.exists(DATA_FILE):
        print(f"Loading data from {DATA_FILE}...")
        data = pd.read_csv(DATA_FILE, index_col=0, parse_dates=True)
        # Check if we have the right columns/tickers roughly? 
        # For simplicity, assume file is correct if it exists.
        return data

    print(f"Downloading data for {len(tickers)} tickers from {START_DATE} to {END_DATE}...")
    # yfinance auto_adjust=True is often better for backtesting to handle splits/dividends cleanly in one column,
    # but the prompt asked for "Adjusted Close". yf.download default includes "Adj Close".
    # We will use 'Adj Close' explicitly.
    data = yf.download(tickers, start=START_DATE, end=END_DATE, progress=False, auto_adjust=False)["Adj Close"]
    data = data.ffill()
    
    print(f"Saving data to {DATA_FILE}...")
    data.to_csv(DATA_FILE)
    
    return data
