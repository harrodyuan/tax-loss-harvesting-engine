# Tax-Aware Portfolio Construction and Optimization

**Abstract**
This paper investigates the efficacy of Tax-Loss Harvesting (TLH) strategies applied to a Direct Indexing portfolio tracking the S&P 500 over the period 2014-2024. We compare active harvesting strategies against a passive benchmark under specific wash-sale constraints. Our results demonstrate that while harvesting generates theoretical alpha, the "cash drag" mandated by the IRS Wash Sale Rule significantly erodes these gains in a strong bull market. We further analyze the impact of different cash-flow scenarios, finding that a charitable giving liquidation strategy maximizes final wealth retention.

## 1. Introduction

Classical portfolio optimization frameworks, such as the standard Markovitz model, focus on the tradeoff between expected return and risk, typically measured by variance or tracking error relative to a benchmark index. These models usually ignore the impact of tax implications on the net effective returns. However, for taxable investors, portfolio rebalancing decisions have important tax consequences that can greatly affect long-term performance.

In a taxable portfolio, taxes are paid only on the net "realized" gains/losses. This results in path-dependent returns that standard models often fail to capture. In contrast, standard portfolio models depend only on current prices, expected returns, and covariance estimates.

Taxation creates several challenges for portfolio construction. Capital gains and losses are only taxable upon realization. This creates an incentive to build a strategy that defer the sale of appreciated assets while strategically recognizing losses. To prevent massive selloffs due to tax harvesting, regulatory constraints such as the wash-sale rule are put in place—the rule restricts the investor's ability to claim tax deductions on realized losses when the same security is repurchased within a short window, usually 30 days.

In this project, we study tax-efficient strategies to track a broad equity market index over a long investment horizon. We consider a 10-year horizon and begin with an all-cash endowment of \$10 million, rebalancing the portfolio on a regular schedule. We compare several tax-aware strategies against a baseline strategy that perfectly replicates the benchmark index using standard performance metrics.

## 2. Methodology and Mathematical Formulation

### 2.1 Benchmark Portfolio (Baseline)
The benchmark strategy attempts to perfectly replicate the market index. Let $\hat{w}_{i, t}$ be the weight of asset $i$ in the index at time $t$, and let $V_{t}$ denote the total value of the portfolio. The baseline portfolio holds:
$$
x_{i, t}=\hat{w}_{i, t} V_{t}
$$
dollars invested in each asset $i$ at every rebalancing date. This strategy ignores tax considerations entirely and realizes capital gains and losses whenever rebalancing requires trading.

### 2.2 Greedy Tax-Loss Harvesting (No Wash-Sale Constraints)
This strategy implements a greedy tax-loss harvesting rule: at each date $t$, the investor compares the current market price $P_{i, t}$ of each asset to its tax cost basis $B_{i, t}$. The unrealized gain or loss is given by:
$$
G_{i, t}=P_{i, t}-B_{i, t}
$$
Positions where $G_{i, t} < 0$ (specifically, below a threshold, e.g., -5\%) are classified as having unrealized capital losses and are immediately sold. The realized loss generates a tax credit equal to:
$$
\text{Tax Credit}_{i, t}=\tau \cdot |G_{i, t}| \cdot q_{i, t}
$$
where $\tau$ is the capital gains tax rate (20\%) and $q_{i, t}$ is the number of shares sold. The proceeds from the sale, together with the tax credit, are immediately reinvested in the same asset. This represents the theoretical upper bound of TLH performance.

### 2.3 Greedy Tax-Loss Harvesting (With Wash-Sale Constraints)
This approach accounts for regulatory wash-sale constraints. As before, assets with significant losses are sold. However, repurchasing the same security is delayed by 30 days so as not to trigger the wash-sale rule.
During the exclusion period, the proceeds from the sale are held in **Cash** (yielding 0\%). If $\mathcal{S}_{t}$ denotes the set of assets subject to the wash-sale restriction at time $t$:
$$
w_{i, t}=0 \quad \forall i \in \mathcal{S}_{t}
$$
Once the restriction expires, the asset is repurchased. This delay introduces "Cash Drag"—the opportunity cost of being out of the market during the lockout period.

### 2.4 Tax-Aware Optimization
We formulate portfolio rebalancing as a constrained optimization problem using `cvxpy`. At each rebalancing date, we solve:
$$
\min _{w_{t}} (w_t - \hat{w}_t)^T \Sigma (w_t - \hat{w}_t)
$$
Subject to:
$$
\sum w_{i,t} = 1, \quad w_{i,t} \ge 0, \quad w_{i,t} = 0 \text{ for } i \in \mathcal{S}_t
$$
This framework minimizes tracking error relative to the benchmark while strictly adhering to wash-sale constraints (zero weight on restricted assets). Instead of holding cash, the optimizer attempts to reallocate capital to correlated substitutes within the allowable universe.

## 3. Empirical Results (2014-2024)

The simulation covered a decade characterized by a strong equity bull market. The results for the **Income Withdrawal Scenario** (5\% annual withdrawal) are summarized below:

| Strategy | Final Wealth | Total Tax Paid | Realized Losses |
| :--- | :--- | :--- | :--- |
| **Baseline (Passive)** | \$29,779,543 | \$2,789,422 | \$1,769,279 |
| **Greedy (No Wash)** | **\$32,570,308** | \$2,675,905 | \$6,439,701 |
| **Greedy (With Wash)** | \$25,184,912 | \$4,417,664 | \$22,607,123 |
| **Optimized** | \$25,700,917 | \$4,378,182 | \$22,543,163 |

### 3.1 Analysis of Cash Drag
The most striking finding is the underperformance of the compliant strategies. The **Greedy (With Wash)** strategy underperformed the baseline by over \$4.5M. In a rising market, the opportunity cost of being out of the market (Cash Drag) exceeds the 20\% value of the harvested tax credit. The "No Wash" strategy's outperformance confirms that the *harvesting* itself is valuable ($+\$2.8M$ vs Baseline), but the *regulatory friction* destroys that value in this specific universe and market regime.

### 3.2 Charitable Giving Scenario
We also tested a "Charitable Giving" scenario where the investor contributes \$1M annually and donates the portfolio at Year 10 (avoiding terminal liquidation tax).
*   **Baseline Final Wealth:** \$75,963,882
*   **No Wash Final Wealth:** \$83,256,160
*   **Conclusion:** The combination of tax-free donation and tax-loss harvesting (in the ideal case) creates significant wealth compounding.

## 4. Discussion

Across all scenarios, the results consistently demonstrate that incorporating tax awareness into portfolio rebalancing meaningfully impacts after-tax performance. In the ideal scenario without wash-sale constraints, the greedy tax-loss harvesting strategy dominated all other approaches. This outcome is economically intuitive: by immediately realizing losses while maintaining full market exposure, the strategy systematically converts volatility into tax credits that compound over time.

However, the wash-sale constrained strategy exhibited lower terminal wealth due to forced temporary deviations from the market (Cash Drag). The tax-aware optimization strategy also struggled to outperform the baseline because the universe (50 stocks) was too small to find perfect substitutes for harvested assets, leading to tracking error that was not compensated by the tax benefits.

## 5. Limitations

We made several simplifying assumptions:
1.  **Single Tax Lot:** The tax basis is tracked using a simplified lot logic rather than full specific-share identification for every single fractional trade.
2.  **Universe Size:** Limiting the universe to 50 stocks exaggerates the impact of wash-sale constraints because there are fewer correlated substitutes available than in a full S&P 500 universe.
3.  **Transaction Costs:** We assumed zero transaction costs, which favors high-turnover strategies like Greedy Harvesting.

## 6. References

1.  Moehle, N., Kochenderfer, M. J., Boyd, S., & Ang, A. (2021). *Tax-Aware Portfolio Construction via Convex Optimization*. arXiv:2008.04985 [math.OC].
2.  Chaudhuri, S., Burnham, T., & Lo, A. (2020). *An Empirical Evaluation of Tax-Loss Harvesting Alpha*.
3.  Dammon, R., & Spatt, C. (2012). *Taxes and Investment Choice*.
