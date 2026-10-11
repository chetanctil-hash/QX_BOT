# BUILD PLAN: QX Terminal (v8.0/v9.0)

## 1. Project Status
- **Current State**: Basic FastAPI backend with live `yfinance` pricing and a static-data HTML frontend.
- **Target State**: Production-grade Quant Terminal with automated scoring, historical backtesting, and a Learning Ledger.

## 2. Implementation Phases

### Phase 1: Foundation & Data Architecture (Current)
- [ ] Initialize `ARCHITECTURE.md` and `DATA_SOURCES.md`.
- [ ] Setup Database Schema (SQLite for local, Postgres for prod).
- [ ] Implement `MarketDataProvider` abstraction.
- [ ] Create Instrument Master (NSE Symbol mapping).
- [ ] Implement Data Health Monitor (Staleness/Gap detection).

### Phase 2: The Exact 52-Week Breakout Engine
- [ ] Implement Weekly Candle aggregation logic.
- [ ] Code the exact 52-week breakout expression (with 5-week lag check).
- [ ] Write unit tests for boundary conditions (holidays, missing bars).
- [ ] Implement Market Cap filter (₹500cr - ₹500,000cr).

### Phase 3: Quantamental Scoring Engine (v7.2 $\rightarrow$ v8.0)
- [ ] Implement Automated Momentum Calculation (RS vs Benchmark).
- [ ] Build Earnings Acceleration & Consistency module.
- [ ] Implement Entry-Quality Engine (SMA structure, RSI extension).
- [ ] Create Composite Score Generator (Configurable weights).

### Phase 4: Portfolio & Allocation Engine
- [ ] Implement Current Holdings management.
- [ ] Build Desired Allocation Optimiser (Volatility-adjusted).
  - *Rule*: No cash row, no position-sizing calculator in main view.
- [ ] Sector & Correlation Analysis module.

### Phase 5: Historical Backtesting Laboratory
- [ ] Build Vectorised Backtest Engine.
- [ ] Implement "Point-in-Time" data handling to avoid look-ahead bias.
- [ ] Create Strategy Comparison tool (Simple Mom vs QX-8).
- [ ] Implement Expectancy & Drawdown metrics.

### Phase 6: Learning Ledger & Audit Trail
- [ ] Implement Immutable Signal Snapshots.
- [ ] Build Rejected-Candidate analysis tool.
- [ ] Create Outcome Tracking (Actual vs Predicted returns).

### Phase 7: Professional UI/UX (React/TS)
- [ ] Transition from HTML to React/TS + Tailwind.
- [ ] Implement High-Density Tables (TanStack Table).
- [ ] Build Expandable Research Cards.
- [ ] Integrate TradingView Lightweight Charts.

### Phase 8: Validation, Security & Delivery
- [ ] Run full test suite.
- [ ] Audit API keys and Secret management.
- [ ] Generate Windows Setup Guide.
- [ ] Final Deliverable Report.

## 3. Non-Negotiable Checklists
- [ ] No fabricated data.
- [ ] No look-ahead bias in backtests.
- [ ] No cash row in allocation.
- [ ] Data source timestamps visible everywhere.
- [ ] All weights configurable.
