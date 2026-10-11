import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from providers import MarketDataProvider, YFinanceProvider
from utils.metrics import QuantMetrics

class BacktestEngine:
    """
    The Backtest Lab: Evaluates the performance of signals recorded in the Learning Ledger.
    Prevents look-ahead bias by using Point-in-Time (PIT) price slicing.
    """

    def __init__(self, provider=None, db_path="qx_terminal.db"):
        self.provider = provider or YFinanceProvider()
        self.db_path = db_path
        self.metrics_calc = QuantMetrics()

    def compute_outcomes(self, horizon_days=30):
        """
        Reads signals from the ledger and calculates their forward returns.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            # Get all signals that don't have an outcome yet
            query = "SELECT signal_id, symbol, timestamp FROM signal_snapshots WHERE outcome_return_1m IS NULL"
            df_signals = pd.read_sql_query(query, conn)
            conn.close()

            if df_signals.empty:
                print("No pending signals to evaluate.")
                return pd.DataFrame()

            results = []
            for _, row in df_signals.iterrows():
                sig_id = row['signal_id']
                sym = row['symbol']
                t_entry = pd.to_datetime(row['timestamp'])

                # 1. Fetch Price History
                # Fetch enough data to cover the horizon
                hist = self.provider.get_history(sym, period='1y')
                if hist is None or hist.empty:
                    continue

                # 2. Find Entry and Exit Prices
                try:
                    entry_price = hist.loc[hist.index >= t_entry].iloc[0]['Close']

                    # Exit: Price at t_entry + horizon_days
                    t_exit = t_entry + timedelta(days=horizon_days)
                    exit_data = hist.loc[hist.index >= t_exit]

                    if exit_data.empty:
                        # If no data after horizon, use the last available price
                        exit_price = hist['Close'].iloc[-1]
                    else:
                        exit_price = exit_data.iloc[0]['Close']

                    fwd_return = (exit_price / entry_price) - 1
                    status = "WIN" if fwd_return > 0 else "LOSS"

                    # 3. Update Ledger
                    self._update_snapshot(sig_id, fwd_return, status)

                    results.append({
                        'signal_id': sig_id,
                        'symbol': sym,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'return': fwd_return
                    })
                except Exception as e:
                    print(f"Return calculation error for {sym}: {e}")

            return pd.DataFrame(results)

        except Exception as e:
            print(f"Backtest Error: {e}")
            return pd.DataFrame()

    def _update_snapshot(self, signal_id, fwd_return, status):
        """Persists the outcome to the signal_snapshots table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE signal_snapshots
                SET outcome_return_1m = ?, outcome_status = ?
                WHERE signal_id = ?
            ''', (float(fwd_return), status, signal_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Update Error: {e}")

    def run_full_analysis(self):
        """
        Processes all signals and computes aggregate quantitative metrics.
        """
        print("Starting Historical Backtest Analysis...")
        outcomes_df = self.compute_outcomes()

        if outcomes_df.empty:
            # Try reading already computed outcomes from DB
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT outcome_return_1m FROM signal_snapshots WHERE outcome_return_1m IS NOT NULL", conn)
            conn.close()
            if df.empty:
                print("No outcome data available to analyze.")
                return None
            returns = df['outcome_return_1m'].tolist()
        else:
            returns = outcomes_df['return'].tolist()

        # Calculate Metrics
        expectancy = self.metrics_calc.calculate_expectancy(returns)
        sharpe = self.metrics_calc.calculate_sharpe_ratio(returns)
        sortino = self.metrics_calc.calculate_sortino_ratio(returns)

        # Simulate an equity curve for Max Drawdown
        equity = [1.0]
        for r in returns:
            equity.append(equity[-1] * (1 + r))
        max_dd = self.metrics_calc.calculate_max_drawdown(equity)

        return {
            'total_signals': len(returns),
            'expectancy': expectancy,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': max_dd,
            'win_rate': len([r for r in returns if r > 0]) / len(returns) if returns else 0
        }

if __name__ == "__main__":
    eng = BacktestEngine()
    report = eng.run_full_analysis()
    if report:
        print("\n--- QX-8.0 Backtest Report ---")
        for k, v in report.items():
            print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
