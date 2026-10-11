# Phase 5: Historical Backtesting Laboratory Implementation Plan

## 1. Overview
The goal is to implement a professional-grade backtesting system for the QX-8.0 strategy. This system will validate the predictive power of signals recorded in the `signal_snapshots` table (The Learning Ledger) by measuring their forward returns and calculating risk-adjusted performance metrics.

## 2. Proposed File Structure
```text
C:\Users\ira\OneDrive\Desktop\QX_BOT\API\
├── engines/
│   ├── backtest_engine.py      # New: Main BacktestEngine class
│   ├── breakout_engine.py     # Modified: Add as_of_date support
│   └── scoring_engine.py      # Modified: Add as_of_date support
├── providers.py               # Modified: Enhance YFinanceProvider for point-in-time data
└── ...
```

## 3. Implementation Details

### 3.1 Point-in-Time (PIT) Data Slicing
To avoid look-ahead bias, the system must simulate the state of the world as it was on a specific date.

- **`YFinanceProvider` Enhancement**: 
    - Modify `get_history` to accept `end_date`.
    - Ensure all data fetched for a specific signal is capped at the signal's `timestamp`.
- **Engine Slicing**:
    - `BreakoutEngine.evaluate_breakout(symbol, market_cap, as_of_date=None)`
    - `ScoringEngine.calculate_composite_score(symbol, as_of_date=None)`
    - If `as_of_date` is provided, the engines will use it as the `end` parameter for `yfinance` history calls, effectively hiding all future data.

### 3.2 Backtest Engine Logic (`BacktestEngine`)
The engine will follow a vectorized approach using Pandas for efficiency.

**Workflow**:
1. **Entry Identification**: Query `signal_snapshots` for all signals where `outcome_return_1m` is NULL.
2. **Forward Window Analysis**:
    - For each signal, identify the `signal_price` and `timestamp`.
    - Fetch price data starting from `timestamp` up to `timestamp + 30 days`.
    - Calculate the 1-month return: $\text{Return} = \frac{\text{Price}_{t+30} - \text{Price}_t}{\text{Price}_t}$.
3. **Audit Trail Update**: 
    - Update `signal_snapshots` with `outcome_return_1m` and `outcome_status` (e.g., "WIN", "LOSS", "BREAKEVEN").

### 3.3 Quantitative Metrics Calculation
The engine will compute a performance summary based on the portfolio of signals.

| Metric | Formula / Approach |
| :--- | :--- |
| **Sharpe Ratio** | $\frac{R_p - R_f}{\sigma_p}$ where $R_p$ is avg return, $R_f$ is risk-free rate, $\sigma_p$ is std dev of returns. |
| **Sortino Ratio** | $\frac{R_p - R_f}{\sigma_{downside}}$ where $\sigma_{downside}$ only considers negative returns. |
| **Max Drawdown** | $\max \left( \frac{\text{Peak Value} - \text{Trough Value}}{\text{Peak Value}} \right)$ calculated on the equity curve of the signals. |
| **Expectancy** | $(Win\% \times \text{Avg Win}) - (Loss\% \times \text{Avg Loss})$ |

## 4. Verification Plan (Anti-Cheating)

To ensure no look-ahead bias:
1. **The "Wall" Test**: Create a test case where a stock crashes 50% tomorrow. Ensure the `BreakoutEngine` with `as_of_date=today` does NOT see that crash and still triggers if the 52W breakout is met.
2. **Log Audit**: Log the exact dates fetched from `yfinance` for every signal evaluation to verify `end_date <= signal_timestamp`.
3. **Out-of-Sample Split**: Validate the strategy on data from 2023 and test it on 2024 data.

## 5. Step-by-Step Execution Strategy

1. **Provider Update**: Add `end_date` support to `YFinanceProvider.get_history`.
2. **Engine Modification**: Update `BreakoutEngine` and `ScoringEngine` to support `as_of_date` and propagate this to their data fetches.
3. **BacktestEngine Development**: 
    - Implement `fetch_outcomes()` to iterate through `signal_snapshots`.
    - Implement `calculate_metrics()` for the quantitative analysis.
4. **Integration**: Create a runner script to execute the backtest and update the database.
