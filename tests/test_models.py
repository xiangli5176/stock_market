"""Unit tests for data models in the stock market tracker."""

import unittest
from datetime import datetime
from src.models import Quote, HistoricalData, Stock


class TestQuote(unittest.TestCase):
    """Tests for the Quote model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_quote = Quote(
            symbol="AAPL",
            price=150.00,
            currency="USD",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            open_price=148.50,
            high_price=152.00,
            low_price=147.50,
            volume=50000000,
            previous_close=149.50
        )
    
    def test_quote_creation(self):
        """Test Quote object creation."""
        self.assertEqual(self.test_quote.symbol, "AAPL")
        self.assertEqual(self.test_quote.price, 150.00)
        self.assertEqual(self.test_quote.currency, "USD")
        self.assertEqual(self.test_quote.volume, 50000000)
    
    def test_quote_repr(self):
        """Test Quote string representation."""
        repr_str = repr(self.test_quote)
        self.assertIn("AAPL", repr_str)
        self.assertIn("150.00", repr_str)
        self.assertIn("50,000,000", repr_str)


class TestHistoricalData(unittest.TestCase):
    """Tests for the HistoricalData model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = HistoricalData(
            symbol="AAPL",
            date=datetime(2024, 1, 15),
            open_price=148.50,
            high_price=152.00,
            low_price=147.50,
            close_price=150.00,
            volume=50000000,
            adjusted_close=150.00
        )
    
    def test_historical_data_creation(self):
        """Test HistoricalData object creation."""
        self.assertEqual(self.test_data.symbol, "AAPL")
        self.assertEqual(self.test_data.close_price, 150.00)
        self.assertEqual(self.test_data.volume, 50000000)
    
    def test_historical_data_repr(self):
        """Test HistoricalData string representation."""
        repr_str = repr(self.test_data)
        self.assertIn("AAPL", repr_str)
        self.assertIn("150.00", repr_str)
        self.assertIn("50,000,000", repr_str)


class TestStock(unittest.TestCase):
    """Tests for the Stock model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.quote = Quote(
            symbol="AAPL",
            price=150.00,
            currency="USD",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            open_price=148.50,
            high_price=152.00,
            low_price=147.50,
            volume=50000000,
            previous_close=149.50
        )
        self.stock = Stock(symbol="aapl", quote=self.quote)
    
    def test_stock_creation(self):
        """Test Stock object creation."""
        self.assertEqual(self.stock.symbol, "AAPL")
        self.assertIsNotNone(self.stock.quote)
        self.assertEqual(len(self.stock.historical_data), 0)
    
    def test_stock_symbol_uppercase(self):
        """Test that stock symbol is converted to uppercase."""
        stock = Stock(symbol="tsla")
        self.assertEqual(stock.symbol, "TSLA")
    
    def test_get_latest_price(self):
        """Test getting the latest price."""
        price = self.stock.get_latest_price()
        self.assertEqual(price, 150.00)
    
    def test_get_latest_price_no_quote(self):
        """Test getting latest price when no quote exists."""
        stock = Stock(symbol="GOOGL")
        price = stock.get_latest_price()
        self.assertIsNone(price)
    
    def test_get_price_change(self):
        """Test calculating price change."""
        change = self.stock.get_price_change()
        self.assertEqual(change, 0.50)
    
    def test_get_price_change_no_quote(self):
        """Test getting price change when no quote exists."""
        stock = Stock(symbol="GOOGL")
        change = stock.get_price_change()
        self.assertIsNone(change)
    
    def test_get_price_change_percent(self):
        """Test calculating price change percentage."""
        change_pct = self.stock.get_price_change_percent()
        expected = (0.50 / 149.50) * 100
        self.assertAlmostEqual(change_pct, expected, places=2)
    
    def test_get_price_change_percent_no_quote(self):
        """Test getting price change percent when no quote exists."""
        stock = Stock(symbol="GOOGL")
        change_pct = stock.get_price_change_percent()
        self.assertIsNone(change_pct)
    
    def test_get_price_change_percent_zero_previous_close(self):
        """Test getting price change percent with zero previous close."""
        quote = Quote(
            symbol="TEST",
            price=100.00,
            currency="USD",
            timestamp=datetime.now(),
            open_price=100.00,
            high_price=100.00,
            low_price=100.00,
            volume=0,
            previous_close=0.0
        )
        stock = Stock(symbol="TEST", quote=quote)
        change_pct = stock.get_price_change_percent()
        self.assertIsNone(change_pct)
    
    def test_add_historical_data(self):
        """Test adding historical data to stock."""
        hist_data = [
            HistoricalData(
                symbol="AAPL",
                date=datetime(2024, 1, 14),
                open_price=148.00,
                high_price=151.00,
                low_price=147.00,
                close_price=149.50,
                volume=45000000,
                adjusted_close=149.50
            ),
            HistoricalData(
                symbol="AAPL",
                date=datetime(2024, 1, 15),
                open_price=148.50,
                high_price=152.00,
                low_price=147.50,
                close_price=150.00,
                volume=50000000,
                adjusted_close=150.00
            )
        ]
        self.stock.add_historical_data(hist_data)
        self.assertEqual(len(self.stock.historical_data), 2)
        self.assertEqual(self.stock.historical_data[0].close_price, 149.50)
    
    def test_stock_repr(self):
        """Test Stock string representation."""
        repr_str = repr(self.stock)
        self.assertIn("AAPL", repr_str)
        self.assertIn("Stock(", repr_str)


if __name__ == '__main__':
    unittest.main()
