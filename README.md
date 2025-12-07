```text
  _______  ___   ___      ___  ________      
 /_  __l \/ _ \ / _ \    /  |/  / __/      
  / / / _  /  \/  /_/ /   / /|_/ / _/        
 /_/ /_/|_/_/\_/\___\   /_/  /_/___/        
                                             
  TAX-LOSS HARVESTING ENGINE        
  [SYSTEM: ONLINE] [MODE: SIMULATION]        
```

[![View Full Project Report](https://img.shields.io/badge/View-Full_Report_PDF-00ff00?style=for-the-badge&logo=adobeacrobatreader&logoColor=black)](writeup.pdf)
[![Demo Status](https://img.shields.io/badge/Demo-Operational-00ffff?style=for-the-badge&logo=python&logoColor=black)](demo.py)

# Tax is All You Need

> **"In a bull market, being out of the market (Cash Drag) hurts you more than taxes help you. Unless you cheat (No Wash), it's hard to beat the Baseline.**

This project simulates and evaluates the performance of **Tax-Loss Harvesting (TLH)** strategies on a Direct Indexing portfolio tracking the S&P 500 (Top 50 constituents) over the last 10 years (2014-2024).

##  Key Findings (2014-2024)

![Wealth Curve](images/wealth_curves_wealth_over_time_-_income_withdrawal.png)

1.  **"No Wash" Strategy Wins**: The theoretical best performer was the **Greedy (No Wash)** strategy (**$28.2M** vs $25.9M Baseline). By ignoring the 30-day lockout period, it captured tax credits without missing out on market rebounds ("Cash Drag").
2.  **Cash Drag Hurts**: Strategies that strictly obeyed wash sale rules (Greedy With Wash, Optimized) **underperformed** the simple Buy & Hold baseline (**$25.0M** vs $25.9M). In a strong bull market like 2014-2024, the opportunity cost of sitting in cash for 30 days outweighed the tax benefits of harvesting.
3.  **Charity is Powerful**: The "Charitable Giving" scenario (annual contribution + terminal donation) resulted in the highest final wealth (**$83.3M**) because it avoids the massive liquidation tax at the end of the investment horizon.

##  Terminal Demo

Experience the simulation in your own terminal with our interactive cyberpunk demo script.

```bash
python demo.py
```

```text
[PHASE 2] STRATEGY EXECUTION (SCENARIO: INCOME)
 > PARAMETERS: 5% WITHDRAWAL RATE | LIQUIDATION @ T=END

 PROCESSING...
   :: Baseline (Buy & Hold)          | $25,962,240
   :: Greedy (No Wash - Ideal)       | $28,227,765
   :: Greedy (With Wash - Realistic) | $25,059,144

[ANALYSIS COMPLETE]
 > OBSERVED: 'NO WASH' GENERATES ALPHA VIA TAX CREDITS.
 > WARN: 'WITH WASH' SUFFERS CASH DRAG PENALTY.
```

##  Methodology

*   **Universe**: Top 50 S&P 500 stocks.
*   **Period**: Jan 1, 2014 - Jan 1, 2024 (10 Years).
*   **Initial Capital**: $10,000,000.
*   **Tax Rate**: Flat 20%.
*   **Reinvestment**: Realized losses generate an immediate tax credit (`Loss * 0.20`) which is reinvested into the portfolio.

### Strategies Tested
1.  **Baseline**: Buy & Hold (Monthly Rebalancing). No harvesting.
2.  **Greedy (No Wash)**: Sells losers and immediately buys them back. Captures tax alpha but violates wash sale rules.
3.  **Greedy (With Wash)**: Sells losers and holds cash for 30 days before buying back. Compliant but suffers from cash drag.
4.  **Optimized**: Uses convex optimization (`cvxpy`) to track the index while avoiding restricted stocks.
