"""Stock Market Information Tracing App.

A Python application for fetching and tracking stock market information.

Main Components:
    - Stock, Quote, HistoricalData: Core data models
    - StockFetcher: Data fetching from Yahoo Finance (yfinance)
    - RobinhoodFetcher: Data fetching from Robinhood (robin_stocks, unofficial)
    - Utility functions: CSV export and data formatting
"""

from .models import Stock, Quote, HistoricalData
from .fetcher import StockFetcher
from .robinhood_fetcher import RobinhoodFetcher, RobinhoodFetcherBuilder, RobinhoodAuthError
from .utils import (
    export_quote_to_csv,
    export_historical_to_csv,
    export_quote_summary,
    print_quote_summary,
    export_historical_summary,
    print_historical_summary,
    format_price,
    format_volume,
    format_percent
)

__version__ = "1.0.0"
__author__ = "Stock Market Tracker"

__all__ = [
    # Models
    'Stock',
    'Quote',
    'HistoricalData',
    # Fetcher
    'StockFetcher',
    'RobinhoodFetcher',
    'RobinhoodFetcherBuilder',
    'RobinhoodAuthError',
    # Utilities
    'export_quote_to_csv',
    'export_historical_to_csv',
    'export_quote_summary',
    'print_quote_summary',
    'export_historical_summary',
    'print_historical_summary',
    'format_price',
    'format_volume',
    'format_percent',
]
