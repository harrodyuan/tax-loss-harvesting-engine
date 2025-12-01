import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from typing import Dict, List

def plot_wealth_curves(results_history: Dict[str, pd.Series], title: str = "Portfolio Wealth Over Time"):
    """
    Plots wealth curves for different strategies.
    results_history: Dict where Key = Strategy Name, Value = Series of portfolio values over time.
    """
    plt.figure(figsize=(12, 6))
    
    for label, series in results_history.items():
        plt.plot(series.index, series.values, label=label)
        
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    # Save plot
    filename = f"wealth_curves_{title.replace(' ', '_').lower()}.png"
    plt.savefig(filename)
    print(f"Saved plot to {filename}")
    plt.close()

def plot_drawdowns(results_history: Dict[str, pd.Series], title: str = "Portfolio Drawdowns"):
    """
    Plots drawdown curves.
    """
    plt.figure(figsize=(12, 6))
    
    for label, series in results_history.items():
        # Calculate drawdown
        rolling_max = series.cummax()
        drawdown = (series - rolling_max) / rolling_max
        plt.plot(drawdown.index, drawdown.values, label=label)
        
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Drawdown (%)")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    filename = f"drawdowns_{title.replace(' ', '_').lower()}.png"
    plt.savefig(filename)
    print(f"Saved plot to {filename}")
    plt.close()

def plot_metrics_comparison(df_results: pd.DataFrame):
    """
    Bar charts for Final Wealth, Total Taxes, Realized Losses.
    """
    metrics = ["Final Wealth", "Total Taxes Paid", "Total Realized Losses", "Tracking Error"]
    
    for metric in metrics:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_results, x="Strategy", y=metric, hue="Scenario")
        plt.title(f"{metric} Comparison")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        filename = f"comparison_{metric.replace(' ', '_').lower()}.png"
        plt.savefig(filename)
        print(f"Saved plot to {filename}")
        plt.close()

