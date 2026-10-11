import pandas as pd
import numpy as np
from .base import BaseScoringModule

class EarningsModule(BaseScoringModule):
    """
    Calculates Earnings Score based on Revenue/PAT growth
    and identifies fundamental acceleration.
    """

    def calculate(self, symbol: str, data: dict) -> float:
        """
        Args:
            symbol: Stock ticker.
            data: Must contain 'fundamentals' (dict from YFinanceProvider).
        """
        fundamentals = data.get('fundamentals')
        if not fundamentals:
            return 50.0  # Neutral score for missing data

        try:
            score = 0.0
            coverage = 0

            # 1. Revenue Growth Score
            rev_growth = fundamentals.get('revenue_growth')
            if rev_growth is not None:
                coverage += 1
                if rev_growth > 0.20: score += 70
                elif rev_growth > 0.10: score += 40
                elif rev_growth > 0: score += 20

            # 2. ROE Score (Quality Filter)
            roe = fundamentals.get('roe')
            if roe is not None:
                coverage += 1
                if roe > 0.20: score += 30
                elif roe > 0.10: score += 15

            # 3. PEG Ratio (Growth at Reasonable Price)
            peg = fundamentals.get('peg_ratio')
            if peg is not None:
                coverage += 1
                if 0 < peg < 1.2: score += 10 # Efficient growth

            # Normalize score to 0-100 based on fields found
            if coverage == 0: return 50.0

            # Scale the sum to a 0-100 range
            # Max possible score is 70 (rev) + 30 (roe) + 10 (peg) = 110
            final_score = (score / 110) * 100
            return float(min(100, max(0, final_score)))

        except Exception as e:
            print(f"Earnings Calculation Error for {symbol}: {e}")
            return 50.0
