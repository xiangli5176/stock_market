"""Data models for stock market information."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Quote:
    """Current stock quote information."""
    symbol: str
    price: float
    currency: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    volume: int
    previous_close: float
    
    def __repr__(self) -> str:
        return (
            f"Quote(symbol={self.symbol}, price=${self.price:.2f}, "
            f"volume={self.volume:,}, timestamp={self.timestamp})"
        )


@dataclass
class HistoricalData:
    """Historical price data for a stock."""
    symbol: str
    date: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    adjusted_close: float
    
    def __repr__(self) -> str:
        return (
            f"HistoricalData(symbol={self.symbol}, date={self.date.date()}, "
            f"close=${self.close_price:.2f}, volume={self.volume:,})"
        )


class Stock:
    """Represents a stock with quote and historical data."""
    
    def __init__(self, symbol: str, quote: Optional[Quote] = None):
        """Initialize a Stock object.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            quote: Optional Quote object for current stock information
        """
        self.symbol = symbol.upper()
        self.quote = quote
        self.historical_data: List[HistoricalData] = []
    
    def add_historical_data(self, historical_data: List[HistoricalData]) -> None:
        """Add historical data to the stock.
        
        Args:
            historical_data: List of HistoricalData objects
        """
        self.historical_data = historical_data
    
    def get_latest_price(self) -> Optional[float]:
        """Get the latest stock price.
        
        Returns:
            Latest price if quote exists, None otherwise
        """
        return self.quote.price if self.quote else None
    
    def get_price_change(self) -> Optional[float]:
        """Get the price change from previous close.
        
        Returns:
            Price change if quote exists, None otherwise
        """
        if not self.quote:
            return None
        return self.quote.price - self.quote.previous_close
    
    def get_price_change_percent(self) -> Optional[float]:
        """Get the percentage price change.
        
        Returns:
            Price change percentage if quote exists, None otherwise
        """
        if not self.quote or self.quote.previous_close == 0:
            return None
        change = self.quote.price - self.quote.previous_close
        return (change / self.quote.previous_close) * 100
    
    def __repr__(self) -> str:
        quote_str = str(self.quote) if self.quote else "No quote available"
        return f"Stock(symbol={self.symbol}, {quote_str})"
