"""Stock data fetcher using yfinance."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import yfinance as yf
from .models import Stock, Quote, HistoricalData


class StockFetcher:
    """Fetch stock data from Yahoo Finance using yfinance."""
    
    def __init__(self):
        """Initialize the stock fetcher."""
        pass
    
    @staticmethod
    def _parse_historical_dataframe(symbol: str, hist) -> List[HistoricalData]:
        """Parse a yfinance history DataFrame into a list of HistoricalData objects.
        
        Handles newer versions of yfinance (>=1.3.0) where 'Adj Close' column
        may be absent (prices are already adjusted).
        
        Args:
            symbol: Stock ticker symbol
            hist: DataFrame from yfinance Ticker.history()
            
        Returns:
            List of HistoricalData objects
        """
        historical_data = []
        has_adj_close = 'Adj Close' in hist.columns
        
        for date, row in hist.iterrows():
            historical_data.append(
                HistoricalData(
                    symbol=symbol.upper(),
                    date=date,
                    open_price=float(row['Open']),
                    high_price=float(row['High']),
                    low_price=float(row['Low']),
                    close_price=float(row['Close']),
                    volume=int(row['Volume']),
                    adjusted_close=float(row['Adj Close']) if has_adj_close else float(row['Close'])
                )
            )
        
        return historical_data
    
    def fetch_quote(self, symbol: str) -> Optional[Stock]:
        """Fetch current stock quote information.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Stock object with current quote, or None if fetch fails
        """
        try:
            ticker = yf.Ticker(symbol.upper())
            data = ticker.info
            
            if not data or 'currentPrice' not in data:
                print(f"Warning: Could not fetch data for {symbol}")
                return Stock(symbol=symbol)
            
            quote = Quote(
                symbol=symbol.upper(),
                price=float(data.get('currentPrice', 0)),
                currency=data.get('currency', 'USD'),
                timestamp=datetime.now(),
                open_price=float(data.get('open', 0)),
                high_price=float(data.get('dayHigh', 0)),
                low_price=float(data.get('dayLow', 0)),
                volume=int(data.get('volume', 0)),
                previous_close=float(data.get('previousClose', 0))
            )
            
            stock = Stock(symbol=symbol, quote=quote)
            return stock
            
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {str(e)}")
            return Stock(symbol=symbol)
    
    def fetch_historical_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[Stock]:
        """Fetch historical price data for a stock.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max')
            interval: Data interval ('1m', '5m', '15m', '30m', '60m', '1d', '1wk', '1mo')
            
        Returns:
            Stock object with historical data, or None if fetch fails
        """
        try:
            ticker = yf.Ticker(symbol.upper())
            hist = ticker.history(period=period, interval=interval)
            
            historical_data = self._parse_historical_dataframe(symbol, hist)
            
            stock = Stock(symbol=symbol)
            stock.add_historical_data(historical_data)
            return stock
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {str(e)}")
            return Stock(symbol=symbol)
    
    def fetch_quote_and_history(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[Stock]:
        """Fetch both current quote and historical data.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            period: Time period for historical data
            interval: Data interval for historical data
            
        Returns:
            Stock object with both quote and historical data
        """
        try:
            # Fetch current quote
            stock = self.fetch_quote(symbol)
            
            # Fetch historical data
            ticker = yf.Ticker(symbol.upper())
            hist = ticker.history(period=period, interval=interval)
            
            historical_data = self._parse_historical_dataframe(symbol, hist)
            
            stock.add_historical_data(historical_data)
            return stock
            
        except Exception as e:
            print(f"Error fetching quote and history for {symbol}: {str(e)}")
            return Stock(symbol=symbol)
    
    def fetch_quote_and_history_safe(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Stock:
        """Fetch both current quote and historical data, with graceful fallback.
        
        Unlike fetch_quote_and_history, this method ensures the returned Stock
        always has historical data attached even if the quote fetch fails.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            period: Time period for historical data
            interval: Data interval for historical data
            
        Returns:
            Stock object with historical data (quote may be None if unavailable)
        """
        stock = Stock(symbol=symbol)
        
        # Try fetching quote
        try:
            quote_stock = self.fetch_quote(symbol)
            if quote_stock and quote_stock.quote:
                stock.quote = quote_stock.quote
        except Exception as e:
            print(f"Warning: Could not fetch quote for {symbol}: {str(e)}")
        
        # Fetch historical data
        try:
            ticker = yf.Ticker(symbol.upper())
            hist = ticker.history(period=period, interval=interval)
            
            historical_data = self._parse_historical_dataframe(symbol, hist)
            
            stock.add_historical_data(historical_data)
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {str(e)}")
        
        return stock
    
    def fetch_multiple_quotes(self, symbols: List[str]) -> Dict[str, Stock]:
        """Fetch quotes for multiple stocks.
        
        Args:
            symbols: List of stock ticker symbols
            
        Returns:
            Dictionary mapping symbols to Stock objects
        """
        stocks = {}
        for symbol in symbols:
            stocks[symbol.upper()] = self.fetch_quote(symbol)
        return stocks
    
    def fetch_multiple_historical(
        self,
        symbols: List[str],
        period: str = "1mo",
        interval: str = "1d"
    ) -> Dict[str, Stock]:
        """Fetch historical data for multiple stocks.
        
        Args:
            symbols: List of stock ticker symbols
            period: Time period for historical data
            interval: Data interval for historical data
            
        Returns:
            Dictionary mapping symbols to Stock objects with historical data
        """
        stocks = {}
        for symbol in symbols:
            stocks[symbol.upper()] = self.fetch_historical_data(symbol, period, interval)
        return stocks
