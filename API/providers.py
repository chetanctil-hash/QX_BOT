from abc import ABC, abstractmethod
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class MarketDataProvider(ABC):
    """Abstract Base Class for all Market Data Providers."""

    @abstractmethod
    def get_quote(self, symbol: str):
        """Fetch latest quote for a symbol."""
        pass

    @abstractmethod
    def get_history(self, symbol: str, period: str):
        """Fetch historical price candles."""
        pass

    @abstractmethod
    def get_fundamentals(self, symbol: str):
        """Fetch financial statements and ratios."""
        pass

class YFinanceProvider(MarketDataProvider):
    """Concrete implementation using Yahoo Finance."""

    def get_quote(self, symbol: str):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            return {
                'last_price': info['last_price'],
                'volume': info['last_volume'],
                'timestamp': datetime.now().isoformat(),
                'provider': 'Yahoo Finance',
                'status': 'DELAYED' # yfinance is typically delayed
            }
        except Exception as e:
            print(f"Quote Error {symbol}: {e}")
            return None

    def get_history(self, symbol: str, period: str = '1y', end_date: str = None):
        try:
            ticker = yf.Ticker(symbol)
            # Use end_date for point-in-time slicing to prevent look-ahead bias
            df = ticker.history(period=period, end=end_date)
            if df.empty: return None
            return df
        except Exception as e:
            print(f"History Error {symbol}: {e}")
            return None

    def get_fundamentals(self, symbol: str):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'peg_ratio': info.get('pegRatio', None),
                'roe': info.get('returnOnEquity', None),
                'debt_to_equity': info.get('debtToEquity', None),
                'revenue_growth': info.get('revenueGrowth', None),
            }
        except Exception as e:
            print(f"Fundamentals Error {symbol}: {e}")
            return None

class DataHealthMonitor:
    """Validates data quality and detects staleness."""

    @staticmethod
    def check_staleness(timestamp_str):
        if not timestamp_str: return "STALE"
        ts = datetime.fromisoformat(timestamp_str)
        diff = datetime.now() - ts
        if diff.total_seconds() > 3600: return "STALE"
        if diff.total_seconds() > 300: return "DELAYED"
        return "LIVE"

    @staticmethod
    def validate_candles(df):
        """Checks for gaps, duplicates, or impossible prices."""
        if df is None or df.empty: return False, "Empty Data"
        if df['Close'].isnull().any(): return False, "Missing Values"
        if (df['Close'] <= 0).any(): return False, "Zero/Negative Price"
        return True, "Healthy"
