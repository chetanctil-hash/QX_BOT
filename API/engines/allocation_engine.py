import pandas as pd
import numpy as np
from providers import MarketDataProvider, YFinanceProvider
from engines.scoring_engine import ScoringEngine

class AllocationEngine:
    """
    Implements Risk Parity allocation scaled by Quantamental Scores.
    """

    def __init__(self, provider=None, scoring_engine=None, db_path="qx_terminal.db"):
        self.provider = provider or YFinanceProvider()
        self.scoring_engine = scoring_engine or ScoringEngine(db_path=db_path)
        self.db_path = db_path

    def _calculate_annualized_volatility(self, symbol: str):
        """
        Calculates annualized volatility of daily returns.
        """
        try:
            hist = self.provider.get_history(symbol, period='1y')
            if hist is None or hist.empty:
                return 0.4  # Neutral default volatility (40%)

            # Calculate daily returns
            returns = hist['Close'].pct_change().dropna()
            if returns.empty:
                return 0.4

            # Annualize: std_dev * sqrt(252)
            vol = returns.std() * np.sqrt(252)
            return float(vol)
        except Exception as e:
            print(f"Volatility Error for {symbol}: {e}")
            return 0.4

    def calculate_target_weights(self, symbols: list):
        """
        Computes risk-parity weights scaled by Quant Scores.

        Formula:
        RawWeight = (1 / Volatility) * (CompositeScore / 100)
        TargetWeight = RawWeight / Sum(RawWeights)
        """
        if not symbols:
            return {}

        raw_weights = {}
        total_raw_weight = 0.0

        for sym in symbols:
            # 1. Get Volatility
            vol = self._calculate_annualized_volatility(sym)
            # Avoid division by zero
            inv_vol = 1.0 / max(vol, 0.01)

            # 2. Get Quant Score
            score_data = self.scoring_engine.calculate_composite_score(sym)
            score = score_data['composite_score'] if score_data else 50.0
            quant_scale = score / 100.0

            # 3. Exit Threshold
            if score < 40.0:
                raw_weights[sym] = 0.0
            else:
                raw_weights[sym] = inv_vol * quant_scale

            total_raw_weight += raw_weights[sym]

        # 4. Normalization and Caps
        target_weights = {}
        if total_raw_weight == 0:
            # Uniform distribution if no assets qualify
            return {sym: 1.0 / len(symbols) for sym in symbols}

        for sym in symbols:
            weight = raw_weights[sym] / total_raw_weight
            # Cap at 15% per position to prevent concentration
            target_weights[sym] = min(0.15, weight)

        # Re-normalize if caps reduced total below 1.0
        sum_weights = sum(target_weights.values())
        if sum_weights < 1.0:
            # Distribute remaining weight proportionally to those under the cap
            remainder = 1.0 - sum_weights
            eligible = [s for s in symbols if target_weights[s] < 0.15]
            if eligible:
                share = remainder / len(eligible)
                for s in eligible:
                    target_weights[s] += share

        return target_weights
