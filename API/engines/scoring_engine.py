import sqlite3
import pandas as pd
from datetime import datetime
from providers import MarketDataProvider, YFinanceProvider
from scoring.momentum import MomentumModule
from scoring.earnings import EarningsModule
from scoring.entry import EntryQualityModule

class ScoringEngine:
    """
    Orchestrates the QX-8.0 Quantamental Scoring system.
    Combines Momentum, Earnings, and Entry quality into a composite score.
    """

    def __init__(self, provider=None, db_path="qx_terminal.db"):
        self.provider = provider or YFinanceProvider()
        self.db_path = db_path
        self.modules = {
            'mom': MomentumModule(),
            'earn': EarningsModule(),
            'entry': EntryQualityModule()
        }
        self.benchmark = "^NSEI"

    def _get_strategy_weights(self):
        """Fetches weights from the strategy_config table."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Default weights if DB is empty or record missing
            weights = {'mom': 0.4, 'earn': 0.4, 'entry': 0.2}

            query = "SELECT mom_weight, earnings_weight, val_weight FROM strategy_config ORDER BY created_at DESC LIMIT 1"
            df = pd.read_sql_query(query, conn)
            conn.close()

            if not df.empty:
                weights['mom'] = float(df['mom_weight'].iloc[0])
                weights['earn'] = float(df['earnings_weight'].iloc[0])
                # Note: val_weight mapped to entry for now
                weights['entry'] = float(df['val_weight'].iloc[0])

            # Normalize weights to sum to 1.0
            total = sum(weights.values())
            return {k: v / total for k, v in weights.items()}
        except Exception as e:
            print(f"Weight Fetch Error: {e}")
            return {'mom': 0.4, 'earn': 0.4, 'entry': 0.2}

    def calculate_composite_score(self, symbol: str, as_of_date=None):
        """
        Calculates the full QX-8.0 score for a symbol.
        """
        try:
            # 1. Data Aggregation
            # Pass as_of_date to provider to slice data correctly
            stock_hist = self.provider.get_history(symbol, period='2y', end_date=as_of_date)
            bench_hist = self.provider.get_history(self.benchmark, period='2y', end_date=as_of_date)
            fundamentals = self.provider.get_fundamentals(symbol)

            if stock_hist is None or bench_hist is None:
                return None

            data_bundle = {
                'stock_history': stock_hist,
                'benchmark_history': bench_hist,
                'fundamentals': fundamentals
            }

            # 2. Module Scoring
            scores = {
                'mom_score': self.modules['mom'].calculate(symbol, data_bundle),
                'earnings_score': self.modules['earn'].calculate(symbol, data_bundle),
                'entry_score': self.modules['entry'].calculate(symbol, data_bundle)
            }

            # 3. Composite Weighting
            weights = self._get_strategy_weights()
            composite = (
                scores['mom_score'] * weights['mom'] +
                scores['earnings_score'] * weights['earn'] +
                scores['entry_score'] * weights['entry']
            )

            # 4. Confidence Level
            coverage = 0
            if fundamentals:
                # Simple check: how many of our target fields are present
                fields = ['revenue_growth', 'roe', 'peg_ratio']
                coverage = sum(1 for f in fields if fundamentals.get(f) is not None) / len(fields)

            confidence = "HIGH" if coverage >= 0.8 else "MEDIUM" if coverage >= 0.4 else "LOW"

            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                **scores,
                'composite_score': float(composite),
                'data_coverage': float(coverage),
                'data_confidence': confidence
            }

        except Exception as e:
            print(f"Scoring Error for {symbol}: {e}")
            return None

    def save_signal(self, signal_data, action="HOLD", signal_price=None):
        """Persists the score to the signal_snapshots table (Learning Ledger)."""
        if not signal_data: return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO signal_snapshots
                (symbol, timestamp, regime, mom_score, earnings_score, entry_score, composite_score, action, signal_price, data_coverage, data_confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_data['symbol'],
                signal_data['timestamp'],
                "BULLISH", # Default regime for now
                signal_data['mom_score'],
                signal_data['earnings_score'],
                signal_data['entry_score'],
                signal_data['composite_score'],
                action,
                signal_price,
                signal_data['data_coverage'],
                signal_data['data_confidence']
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Save Error: {e}")
