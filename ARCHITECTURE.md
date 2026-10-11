# ARCHITECTURE: QX Terminal

## 1. System Flow
`Market Data Providers` $\rightarrow$ `Data Ingestion Layer` $\rightarrow$ `Quant Engine` $\rightarrow$ `Signal Store` $\rightarrow$ `FastAPI` $\rightarrow$ `Frontend`

## 2. Component Definitions

### A. Data Ingestion Layer (`/api/data`)
- **MarketDataProvider**: Abstract base class. Implements `get_quote()`, `get_history()`, `get_fundamentals()`.
- **NSEProvider**: Concrete implementation using `yfinance` and other permitted sources.
- **HealthMonitor**: Validates data freshness, detects gaps in candles, and flags stale quotes.

### B. Quant Engine (`/api/quant`)
- **MomentumModule**: Calculates RS, Momentum Acceleration, and Trend Structure.
- **FundamentalModule**: Processes PAT growth, Margin trajectories, and Order book data.
- **EntryQualityModule**: Analyzes SMA distance, RSI extension, and Volume confirmation.
- **CompositeEngine**: Combines modules using versioned weights (QX-7.2, QX-8.0).

### C. Signal Store (`/db`)
- **SignalSnapshot**: Immutable record of a stock's score at a specific timestamp.
- **OutcomeLog**: Tracks the subsequent return of a signal to calculate "Hit Rate."
- **UniverseMaster**: Maintains the eligible stock list and market cap filters.

### D. Backtest Lab (`/api/backtest`)
- **StrategyEngine**: Executes rules over historical point-in-time data.
- **MetricsCalculator**: Computes Sharpe, Sortino, Max Drawdown, and Expectancy.

## 3. Data Schema (Conceptual)
- **Instruments**: `symbol`, `name`, `sector`, `benchmark_id`.
- **DailyBars**: `symbol`, `date`, `open`, `high`, `low`, `close`, `volume`, `adj_close`.
- **Signals**: `signal_id`, `symbol`, `timestamp`, `composite_score`, `entry_score`, `action`.
- **Portfolio**: `symbol`, `qty`, `avg_cost`, `last_updated`.

## 4. Tech Stack
- **Backend**: Python 3.10+ | FastAPI | Pandas | NumPy | SQLite/PostgreSQL.
- **Frontend**: React | TypeScript | Tailwind CSS | TanStack Table | TradingView Charts.
- **Infrastructure**: Docker Compose | `.env` for secrets.
