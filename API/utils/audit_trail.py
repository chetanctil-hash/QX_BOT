import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

class AuditTrail:
    """
    Analyzes the Learning Ledger to identify failure modes
    and suggest strategy weight optimizations.
    """

    def __init__(self, db_path="qx_terminal.db"):
        self.db_path = db_path

    def analyze_failures(self):
        """
        Correlates losses with component scores to find 'Failure Modes'.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            # Only analyze signals that have a recorded outcome
            query = "SELECT mom_score, earnings_score, entry_score, outcome_return_1m FROM signal_snapshots WHERE outcome_return_1m IS NOT NULL"
            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                return "No outcome data available for analysis."

            # Split into Wins and Losses
            wins = df[df['outcome_return_1m'] > 0]
            losses = df[df['outcome_return_1m'] <= 0]

            if losses.empty:
                return "No losses recorded yet. System is performing perfectly!"

            # Calculate mean scores for wins vs losses
            win_means = wins[['mom_score', 'earnings_score', 'entry_score']].mean()
            loss_means = losses[['mom_score', 'earnings_score', 'entry_score']].mean()

            # The 'failure driver' is the component where losses have significantly
            # different scores than wins (or very low scores in general)
            diff = win_means - loss_means
            failure_driver = diff.idxmax()

            return {
                'win_rate': len(wins) / len(df),
                'failure_driver': failure_driver,
                'win_avg_scores': win_means.to_dict(),
                'loss_avg_scores': loss_means.to_dict(),
                'insight': f"Losses are most strongly associated with low {failure_driver} scores."
            }

        except Exception as e:
            return f"Analysis Error: {e}"

    def suggest_weight_updates(self):
        """
        Suggests new weights based on correlation with returns.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT mom_score, earnings_score, entry_score, outcome_return_1m FROM signal_snapshots WHERE outcome_return_1m IS NOT NULL"
            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty: return "Insufficient data for weight optimization."

            # Calculate correlation of each score with the actual return
            correlations = {
                'mom': df['mom_score'].corr(df['outcome_return_1m']),
                'earn': df['earnings_score'].corr(df['outcome_return_1m']),
                'entry': df['entry_score'].corr(df['outcome_return_1m'])
            }

            # Suggest weights proportional to positive correlation
            # Filter out negative correlations (those that lead to losses)
            pos_corrs = {k: max(0, v) for k, v in correlations.items()}
            total_corr = sum(pos_corrs.values())

            if total_corr == 0:
                return "No positive correlations found. Weights remain unchanged."

            suggested_weights = {k: v / total_corr for k, v in pos_corrs.items()}

            return {
                'correlations': correlations,
                'suggested_weights': suggested_weights,
                'version': "v8.1 (Empirical)"
            }

        except Exception as e:
            return f"Optimization Error: {e}"

if __name__ == "__main__":
    audit = AuditTrail()
    print("--- Failure Mode Analysis ---")
    print(audit.analyze_failures())
    print("\n--- Weight Optimization ---")
    print(audit.suggest_weight_updates())
