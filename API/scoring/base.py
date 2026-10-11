from abc import ABC, abstractmethod

class BaseScoringModule(ABC):
    """
    Abstract base class for all QX Scoring modules.
    Each module must implement a 'calculate' method that returns a score between 0 and 100.
    """

    @abstractmethod
    def calculate(self, symbol: str, data: dict) -> float:
        """
        Calculate a specific quantamental score.

        Args:
            symbol: The stock ticker.
            data: A dictionary containing pre-fetched market and fundamental data.

        Returns:
            A float between 0.0 and 100.0.
        """
        pass
