# Tax-Loss Harvesting Backtesting Engine

## Project Overview
This project implements a comprehensive backtesting engine to evaluate Tax-Loss Harvesting (TLH) strategies for a direct indexing portfolio tracking the S&P 500 (Top 50 constituents). It compares the performance of tax-aware strategies against a baseline "Buy & Hold" approach over a 10-year period (2014-2024), considering specific tax rules, wash sale constraints, and cash flow scenarios.

## Methodology

### 1. Portfolio Construction
- **Universe**: Top 50 constituents of the S&P 500.
- **Initial Capital**: $10,000,000.
- **Tax Rate**: Flat 20% on realized gains.
- **Tax Alpha**: Realized losses are assumed to generate an immediate tax credit (`Loss * TaxRate`), which is reinvested into the portfolio (cash injection).
- **Rebalancing**: Monthly rebalancing to Equal Weight.

### 2. Strategies Tested

| Strategy | Description | Wash Sale Handling |
| :--- | :--- | :--- |
| **Baseline (No Harvesting)** | Benchmark strategy. Rebalances monthly to equal weights. No tax-loss harvesting. | N/A |
| **Greedy (No Wash Rule)** | Harvests losses immediately when price drops below threshold (-5%). Immediately repurchases the same asset. | **Violates Rule**: Ignores 30-day wash sale window. Serves as a theoretical upper bound for TLH alpha. |
| **Greedy (With Wash Rule)** | Harvests losses immediately. If sold, the ticker is added to a "Restricted List" for 30 days. Proceeds sit in **Cash** (Cash Drag) until restriction expires. | **Compliant**: Adheres to IRS wash sale rules but suffers from being out of the market. |
| **Optimized (Tax Aware)** | Uses Convex Optimization (`cvxpy`) to minimize Tracking Error vs Benchmark. | **Compliant**: Explicit constraint prevents weight allocation to restricted tickers during the wash sale window. |

### 3. Scenarios

Two distinct cash flow scenarios were applied to each strategy:

*   **Income Generating**: 
    *   Withdraw 5% of AUM annually.
    *   Liquidate entire portfolio at the end of Year 10 (fully taxable event).
*   **Charitable Giving**: 
    *   **Contribute** (Inject) $1M cash annually.
    *   Donate entire portfolio at the end of Year 10 (0% tax on liquidation).

## Code Structure

The project is modularized into the following components:

*   `config.py`: Central configuration for constants (Dates, Tax Rates, etc.).
*   `data_loader.py`: Handles data ingestion from `yfinance` with local caching (`sp500_data.csv`).
*   `tax_lot.py`: Defines the `TaxLot` class and tracks cost basis.
*   `portfolio.py`: Manages holdings, cash, and implements HIFO (Highest In, First Out) liquidation and loss harvesting logic.
*   `strategies.py`: Contains the `BacktestEngine` and the logic for all 4 strategies (Baseline, Greedy No/With Wash, Optimized).
*   `scenarios.py`: Implements the Income Withdrawal and Charitable Giving logic.
*   `visualization.py`: Generates wealth curves, drawdown charts, and metric comparison bar charts.
*   `main.py`: Orchestrates the simulation, runs all 8 variations (4 strategies x 2 scenarios), and saves results.

## Key Results (2014-2024)

*   **Winner**: **Greedy (No Wash Rule)**. By ignoring the wash sale rule, this strategy captured the tax benefits of harvesting losses without suffering from "Cash Drag" (missing out on market rebounds while waiting 30 days).
*   **Impact of Wash Sales**: The **Greedy (With Wash)** and **Optimized** strategies significantly underperformed the Baseline. This is because the 2014-2024 period was largely a bull market. Being forced to sit in cash (or avoid specific stocks) for 30 days after a drop often meant missing the subsequent recovery.
*   **Charitable Giving**: This scenario resulted in drastically higher final wealth due to the annual capital injections and the tax-free terminal liquidation.

## Visualizations
The system automatically generates the following plots in the project directory:
*   `wealth_curves_*.png`: Portfolio value over time.
*   `drawdowns_*.png`: Drawdown depth over time.
*   `comparison_*.png`: Bar charts for Final Wealth, Taxes, Losses, and Tracking Error.

## How to Run

1.  **Install Requirements**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run Simulation**:
    ```bash
    python main.py
    ```
    *   This will download data (if not cached), run all simulations, print a summary table, save `backtest_results.csv`, and generate all plots.

