import numpy as np
import pandas as pd

class QuantMetrics:
    """
    Utility class for calculating professional quantitative performance metrics.
    """

    @staticmethod
    def calculate_expectancy(returns: list):
        """
        Expectancy = (Win Rate * Avg Win) - (Loss Rate * Avg Loss)
        """
        if not returns: return 0.0

        returns = np.array(returns)
        wins = returns[returns > 0]
        losses = returns[returns <= 0]

        win_rate = len(wins) / len(returns)
        loss_rate = len(losses) / len(returns)

        avg_win = np.mean(wins) if len(wins) > 0 else 0
        avg_loss = abs(np.mean(losses)) if len(losses) > 0 else 0

        return (win_rate * avg_win) - (loss_rate * avg_loss)

    @staticmethod
    def calculate_sharpe_ratio(returns: list, risk_free_rate=0.02):
        """
        Annualized Sharpe Ratio.
        """
        if len(returns) < 2: return 0.0

        returns = np.array(returns)
        # Convert to daily if they are monthly
        # For simplicity, we treat these as independent event returns
        # Annualizing: Mean / Std * sqrt(number of signals per year)
        # Assuming 20 signals/year on average
        mean_ret = np.mean(returns) - (risk_free_rate / 12)
        std_ret = np.std(returns)

        if std_ret == 0: return 0.0
        return (mean_ret / std_ret) * np.sqrt(12)

    @staticmethod
    def calculate_sortino_ratio(returns: list, risk_free_rate=0.02):
        """
        Annualized Sortino Ratio (only considers downside volatility).
        """
        if len(returns) < 2: return 0.0

        returns = np.array(returns)
        mean_ret = np.mean(returns) - (risk_free_rate / 12)

        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0: return 0.0

        downside_std = np.std(downside_returns)
        if downside_std == 0: return 0.0

        return (mean_ret / downside_std) * np.sqrt(12)

    @staticmethod
    def calculate_max_drawdown(equity_curve: list):
        """
        Maximum peak-to-trough decline.
        """
        if not equity_curve: return 0.0

        curve = np.array(equity_curve)
        peak = curve[0]
        max_dd = 0

        for value in curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd

        return float(max_dd)
