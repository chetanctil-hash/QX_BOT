import pandas as pd
import numpy as np
from .base import BaseScoringModule

class MomentumModule(BaseScoringModule):
    """
    Calculates Momentum Score based on Relative Strength (RS)
    across multiple timeframes (3M, 6M, 12M) and checks for acceleration.
    """

    def calculate(self, symbol: str, data: dict) -> float:
        """
        Args:
            symbol: Stock ticker.
            data: Must contain 'stock_history' and 'benchmark_history' (Pandas DataFrames).
        """
        stock_hist = data.get('stock_history')
        bench_hist = data.get('benchmark_history')

        if stock_hist is None or bench_hist is None:
            return 50.0  # Neutral score if data is missing

        try:
            # 1. Calculate Returns for 3M, 6M, 12M
            # Approx trading days: 3M=63, 6M=126, 12M=252
            windows = {'3M': 63, '6M': 126, '12M': 252}
            rs_values = {}

            for label, days in windows.items():
                if len(stock_hist) < days or len(bench_hist) < days:
                    return 50.0

                stock_ret = (stock_hist['Close'].iloc[-1] / stock_hist['Close'].iloc[-days]) - 1
                bench_ret = (bench_hist['Close'].iloc[-1] / bench_hist['Close'].iloc[-days]) - 1
                rs_values[label] = stock_ret - bench_ret

            # 2. Relative Strength Score (0-100)
            # We use the 6M RS as the anchor.
            # Assume 20% relative outperformance = 100 points.
            avg_rs = sum(rs_values.values()) / 3
            rs_score = min(100, max(0, avg_rs * 500))

            # 3. Acceleration Bonus
            # If 3M RS > 6M RS > 12M RS, the trend is accelerating.
            acceleration_multiplier = 1.0
            if rs_values['3M'] > rs_values['6M'] > rs_values['12M']:
                acceleration_multiplier = 1.2
            elif rs_values['3M'] < rs_values['6M']:
                acceleration_multiplier = 0.8 # Decelerating

            final_score = rs_score * acceleration_multiplier
            return float(min(100, max(0, final_score)))

        except Exception as e:
            print(f"Momentum Calculation Error for {symbol}: {e}")
            return 50.0
