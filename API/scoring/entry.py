import pandas as pd
import numpy as np
from .base import BaseScoringModule

class EntryQualityModule(BaseScoringModule):
    """
    Calculates Entry Quality Score to ensure the stock is not
    overextended (too far from its SMA or overbought).
    """

    def calculate(self, symbol: str, data: dict) -> float:
        """
        Args:
            symbol: Stock ticker.
            data: Must contain 'stock_history' (Pandas DataFrame).
        """
        stock_hist = data.get('stock_history')
        if stock_hist is None or len(stock_hist) < 50:
            return 50.0

        try:
            close = stock_hist['Close'].iloc[-1]

            # 1. SMA 50 Distance
            sma50 = stock_hist['Close'].rolling(window=50).mean().iloc[-1]
            dist_sma50 = (close / sma50) - 1

            # 2. RSI (14) Calculation
            delta = stock_hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs_idx = gain / loss
            rsi = 100 - (100 / (1 + rs_idx.iloc[-1]))

            # Scoring Logic: Start at 100 and penalize
            score = 100.0

            # Distance Penalty
            if dist_sma50 > 0.15: score -= 50
            elif dist_sma50 > 0.05: score -= 20

            # RSI Penalty
            if rsi > 85: score -= 40
            elif rsi > 70: score -= 20

            return float(min(100, max(0, score)))

        except Exception as e:
            print(f"Entry Quality Calculation Error for {symbol}: {e}")
            return 50.0
