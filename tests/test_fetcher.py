"""Unit tests for stock data fetcher."""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import pandas as pd
from src.fetcher import StockFetcher
from src.models import Stock, Quote, HistoricalData


class TestStockFetcher(unittest.TestCase):
    """Tests for the StockFetcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = StockFetcher()
    
    @patch('src.fetcher.yf.Ticker')
    def test_fetch_quote_success(self, mock_ticker_class):
        """Test successful quote fetching."""
        # Mock the yfinance Ticker
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        # Mock ticker.info with sample data
        mock_ticker.info = {
            'currentPrice': 150.00,
            'currency': 'USD',
            'open': 148.50,
            'dayHigh': 152.00,
            'dayLow': 147.50,
            'volume': 50000000,
            'previousClose': 149.50
        }
        
        stock = self.fetcher.fetch_quote('AAPL')
        
        self.assertIsNotNone(stock)
        self.assertEqual(stock.symbol, 'AAPL')
        self.assertIsNotNone(stock.quote)
        self.assertEqual(stock.quote.price, 150.00)
        self.assertEqual(stock.quote.currency, 'USD')
        self.assertEqual(stock.quote.volume, 50000000)
    
    @patch('src.fetcher.yf.Ticker')
    def test_fetch_quote_missing_current_price(self, mock_ticker_class):
        """Test quote fetching when current price is missing."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        # Mock ticker.info without currentPrice
        mock_ticker.info = {
            'currency': 'USD',
            'open': 148.50
        }
        
        stock = self.fetcher.fetch_quote('AAPL')
        
        self.assertIsNotNone(stock)
        self.assertEqual(stock.symbol, 'AAPL')
        # Should still return a Stock object even if data is incomplete
        self.assertIsNotNone(stock)
    
    @patch('src.fetcher.yf.Ticker')
    def test_fetch_quote_exception(self, mock_ticker_class):
        """Test quote fetching with exception."""
        mock_ticker_class.side_effect = Exception("Network error")
        
        stock = self.fetcher.fetch_quote('INVALID')
        
        self.assertIsNotNone(stock)
        self.assertEqual(stock.symbol, 'INVALID')
    
    @patch('src.fetcher.yf.Ticker')
    def test_fetch_quote_symbol_uppercase(self, mock_ticker_class):
        """Test that symbol is converted to uppercase."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        mock_ticker.info = {
            'currentPrice': 150.00,
            'currency': 'USD',
            'open': 148.50,
            'dayHigh': 152.00,
            'dayLow': 147.50,
            'volume': 50000000,
            'previousClose': 149.50
        }
        
        stock = self.fetcher.fetch_quote('aapl')
        
        self.assertEqual(stock.symbol, 'AAPL')
        mock_ticker_class.assert_called_with('AAPL')
    
    @patch('src.fetcher.yf.Ticker')
    def test_fetch_historical_data_success(self, mock_ticker_class):
        """Test successful historical data fetching."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        # Create mock historical data
        dates = pd.date_range('2024-01-14', periods=2)
        mock_ticker.history.return_value = pd.DataFrame({
            'Open': [148.00, 148.50],
            'High': [151.00, 152.00],
            'Low': [147.00, 147.50],
            'Close': [149.50, 150.00],
            'Adj Close': [149.50, 150.00],
            'Volume': [45000000, 50000000]
        }, index=dates)
        
        stock = self.fetcher.fetch_historical_data('AAPL', period='2d', interval='1d')
        
        self.assertIsNotNone(stock)
        self.assertEqual(stock.symbol, 'AAPL')
        self.assertEqual(len(stock.historical_data), 2)
        self.assertEqual(stock.historical_data[0].close_price, 149.50)
        self.assertEqual(stock.historical_data[1].close_price, 150.00)
    
    @patch('src.fetcher.yf.Ticker')
    def test_fetch_historical_data_empty(self, mock_ticker_class):
        """Test historical data fetching with empty result."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        
        # Return empty dataframe
        mock_ticker.history.return_value = pd.DataFrame()
        
        stock = self.fetcher.fetch_historical_data('INVALID', period='1d', interval='1d')
        
        self.assertIsNotNone(stock)
        self.assertEqual(len(stock.historical_data), 0)
    
    @patch('src.fetcher.yf.Ticker')
    def test_fetch_historical_data_exception(self, mock_ticker_class):
        """Test historical data fetching with exception."""
        mock_ticker_class.side_effect = Exception("Network error")
        
        stock = self.fetcher.fetch_historical_data('AAPL')
        
        self.assertIsNotNone(stock)
        self.assertEqual(stock.symbol, 'AAPL')
        self.assertEqual(len(stock.historical_data), 0)
    
    @patch('src.fetcher.yf.Ticker')
    def test_fetch_historical_data_default_parameters(self, mock_ticker_class):
        """Test that default parameters are used correctly."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.history.return_value = pd.DataFrame()
        
        self.fetcher.fetch_historical_data('AAPL')
        
        # Check that history was called with default parameters
        mock_ticker.history.assert_called_with(period='1mo', interval='1d')
    
    @patch('src.fetcher.yf.Ticker')
    def test_fetch_historical_data_custom_parameters(self, mock_ticker_class):
        """Test that custom parameters are used correctly."""
        mock_ticker = MagicMock()
        mock_ticker_class.return_value = mock_ticker
        mock_ticker.history.return_value = pd.DataFrame()
        
        self.fetcher.fetch_historical_data('AAPL', period='1y', interval='1wk')
        
        # Check that history was called with custom parameters
        mock_ticker.history.assert_called_with(period='1y', interval='1wk')
    
    @patch('src.fetcher.StockFetcher.fetch_historical_data')
    @patch('src.fetcher.StockFetcher.fetch_quote')
    def test_fetch_quote_and_history(self, mock_fetch_quote, mock_fetch_hist):
        """Test fetching both quote and historical data."""
        # Mock the individual fetch methods
        quote = Quote(
            symbol='AAPL',
            price=150.00,
            currency='USD',
            timestamp=datetime.now(),
            open_price=148.50,
            high_price=152.00,
            low_price=147.50,
            volume=50000000,
            previous_close=149.50
        )
        stock_with_quote = Stock(symbol='AAPL', quote=quote)
        mock_fetch_quote.return_value = stock_with_quote
        
        hist_data = [
            HistoricalData(
                symbol='AAPL',
                date=datetime(2024, 1, 14),
                open_price=148.00,
                high_price=151.00,
                low_price=147.00,
                close_price=149.50,
                volume=45000000,
                adjusted_close=149.50
            )
        ]
        stock_with_hist = Stock(symbol='AAPL')
        stock_with_hist.add_historical_data(hist_data)
        mock_fetch_hist.return_value = stock_with_hist
        
        stock = self.fetcher.fetch_quote_and_history('AAPL')
        
        # Verify both methods were called
        mock_fetch_quote.assert_called_once()
        mock_fetch_hist.assert_called_once()


if __name__ == '__main__':
    unittest.main()
