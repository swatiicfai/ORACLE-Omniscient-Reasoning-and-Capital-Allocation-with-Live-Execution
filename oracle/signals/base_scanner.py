"""
ORACLE Base Scanner Class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel
from loguru import logger

class Signal(BaseModel):
    """Data model representing a trade signal identified by a scanner."""
    symbol: str
    scanner_name: str
    confidence: float          # 0 to 100
    underlying_price: float
    direction: str             # "BULLISH", "BEARISH", "NEUTRAL", "VOLATILE"
    metadata: Dict[str, Any]   # Scanner-specific context (e.g., IV rank, move pct)
    recommended_strategy: str  # e.g., "IRON_CONDOR", "STRADDLE"


class BaseScanner(ABC):
    """Abstract base class for all signal scanners."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the scanner (e.g., 'MomentumFade')"""
        pass

    @abstractmethod
    def scan(self, watchlist: List[str]) -> List[Signal]:
        """
        Execute the scan across the watchlist and return a list of Signals.
        Should return an empty list if no opportunities are found.
        """
        pass

    def __str__(self):
        return f"Scanner({self.name})"
