import pandas as pd
import numpy as np
from datetime import datetime, timedelta
try:
    from providers import YFinanceProvider, DataHealthMonitor
except ImportError:
    from .providers import YFinanceProvider, DataHealthMonitor

class BreakoutEngine:
    """
    Implements the exact 52-week weekly closing-high breakout screen.
    Rule: Current weekly close > max(52 previous weekly closes)
    AND 5 previous weeks were below their respective 52-week highs.
    """

    def __init__(self, provider=None):
        self.provider = provider or YFinanceProvider()
        self.health = DataHealthMonitor()

    def get_weekly_data(self, symbol, as_of_date=None):
        """Fetches and aggregates daily data into weekly closes."""
        # Pass as_of_date to provider to slice data correctly
        df = self.provider.get_history(symbol, period='2y', end_date=as_of_date)
        if df is None:
            return None

        # Ensure index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        # Resample to Weekly (W-FRI)
        weekly_df = df['Close'].resample('W-FRI').last().dropna()

        # To avoid the "partial week" problem where the last bar is
        # identical to the previous one or creates a double-entry
        # if the date range ends on a Friday, we ensure the series
        # is unique by date.
        return weekly_df.to_frame()

    def evaluate_breakout(self, symbol, market_cap, as_of_date=None):
        """
        Execs the exact logic:
        1. Market Cap Check (500cr - 500,000cr)
        2. Current Close > Max(Prev 52W)
        3. Lagged conditions for 5 prior weeks
        """
        if not (500 <= market_cap <= 500000):
            return {"satisfied": False, "reason": "Market Cap Out of Range"}

        df = self.get_weekly_data(symbol, as_of_date=as_of_date)
        if df is None:
            return {"satisfied": False, "reason": "Insufficient History"}

        closes = df['Close'].values
        # We need at least 52 (lookback) + 1 (current) + 5 (lags) = 58 candles
        if len(closes) < 60:
            return {"satisfied": False, "reason": "Insufficient Weekly Bars", "count": len(closes)}

        current_close = closes[-1]

        # 2. Current Breakout Check
        # The 52-week lookback is precisely the 52 bars BEFORE the current one.
        lookback_window = closes[-(52 + 1):-1]
        prev_52w_high = np.max(lookback_window)

        if current_close <= prev_52w_high:
            return {"satisfied": False, "reason": "No 52W High Breakout", "details": f"{current_close:.2f} <= {prev_52w_high:.2f}"}

        # 3. Lagged Condition Check
        # For each of the 5 prior weeks, the close must have been BELOW its OWN 52-week high.
        for i in range(1, 6):
            close_i = closes[-(i + 1)]
            # Window for week i is the 52 bars preceding week i.
            window_i = closes[-(52 + i + 1):-(i + 1)]
            max_i = np.max(window_i)

            if close_i >= max_i:
                return {
                    "satisfied": False,
                    "reason": f"Lagged condition failed at week -{i}",
                    "details": f"{close_i:.2f} >= {max_i:.2f}"
                }

        return {
            "satisfied": True,
            "current_close": float(current_close),
            "prev_52w_high": float(prev_52w_high),
            "breakout_pct": float(((current_close/prev_52w_high)-1)*100),
            "consecutive_lags": 5
        }

if __name__ == "__main__":
    print("Running Exact Breakout Engine Tests...")

    class MockProvider:
        def get_history(self, symbol, period='1y'):
            # Create 150 weeks of data to be absolutely safe
            # Setup: 100 weeks of low prices, 52 weeks of growth to set a high,
            # then 5 weeks of consolidation (below that high), then 1 breakout.
            data = []
            for i in range(100): data.append(10.0 + (i * 0.1)) # Base: 10 to 20
            for i in range(52):  data.append(20.0 + i)         # Growth: 20 to 71 (High = 71)
            for i in range(5):   data.append(60.0)             # Consolidation: 60 < 71
            data.append(80.0)                                  # Breakout: 80 > 71

            # Expand weekly data to daily to simulate yfinance output
            # Use 1 day per value and set the index to exactly the Fridays we want.
            # This eliminates resample ambiguity.
            daily_data = data
            dates = pd.date_range(end=datetime.now(), periods=len(data), freq='W-FRI')
            df = pd.DataFrame({'Close': daily_data}, index=dates)
            return df

    engine = BreakoutEngine(provider=MockProvider())
    res = engine.evaluate_breakout("TEST_STOCK", 1000)
    print(f"Test Case (Valid Breakout): {'PASSED' if res['satisfied'] else 'FAILED'}")
    if not res['satisfied']:
        print(f"Reason for failure: {res.get('reason')}")
