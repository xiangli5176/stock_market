"""Unit tests for utility functions in the stock market tracker."""

import unittest
import tempfile
import csv
import os
from datetime import datetime
from pathlib import Path
from src.models import Quote, Stock, HistoricalData
from src.utils import (
    export_quote_to_csv,
    export_historical_to_csv,
    export_quote_summary,
    export_historical_summary,
    format_price,
    format_volume,
    format_percent
)


class TestFormatFunctions(unittest.TestCase):
    """Tests for formatting utility functions."""
    
    def test_format_price(self):
        """Test price formatting."""
        self.assertEqual(format_price(150.5), "$150.50")
        self.assertEqual(format_price(1000.99), "$1000.99")
        self.assertEqual(format_price(0.5), "$0.50")
    
    def test_format_volume(self):
        """Test volume formatting with thousand separators."""
        self.assertEqual(format_volume(1000), "1,000")
        self.assertEqual(format_volume(1000000), "1,000,000")
        self.assertEqual(format_volume(100), "100")
    
    def test_format_percent(self):
        """Test percentage formatting."""
        self.assertEqual(format_percent(5.5), "+5.50%")
        self.assertEqual(format_percent(-2.3), "-2.30%")
        self.assertEqual(format_percent(0.0), "+0.00%")


class TestCSVExportFunctions(unittest.TestCase):
    """Tests for CSV export functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
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
        self.stock_with_quote = Stock(symbol="AAPL", quote=self.quote)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_export_quote_to_csv(self):
        """Test exporting quote to CSV."""
        filepath = os.path.join(self.temp_dir, "test_quote.csv")
        result = export_quote_to_csv(self.stock_with_quote, filepath)
        
        self.assertTrue(os.path.exists(result))
        
        with open(result, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertIn("AAPL", rows[1])
            self.assertIn("150.00", rows[1])
    
    def test_export_quote_to_csv_no_quote(self):
        """Test exporting quote when no quote data exists."""
        stock = Stock(symbol="GOOGL")
        with self.assertRaises(ValueError):
            export_quote_to_csv(stock, os.path.join(self.temp_dir, "test.csv"))
    
    def test_export_historical_to_csv(self):
        """Test exporting historical data to CSV."""
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
        self.stock_with_quote.add_historical_data(hist_data)
        
        filepath = os.path.join(self.temp_dir, "test_historical.csv")
        result = export_historical_to_csv(self.stock_with_quote, filepath)
        
        self.assertTrue(os.path.exists(result))
        
        with open(result, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3)  # header + 2 data rows
    
    def test_export_historical_to_csv_no_data(self):
        """Test exporting historical data when no data exists."""
        stock = Stock(symbol="GOOGL")
        with self.assertRaises(ValueError):
            export_historical_to_csv(
                stock,
                os.path.join(self.temp_dir, "test.csv")
            )


class TestSummaryFunctions(unittest.TestCase):
    """Tests for summary export functions."""
    
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
        self.stock = Stock(symbol="AAPL", quote=self.quote)
    
    def test_export_quote_summary(self):
        """Test exporting quote summary."""
        summary = export_quote_summary(self.stock)
        
        self.assertIn("AAPL", summary)
        self.assertIn("150.00", summary)
        self.assertIn("50,000,000", summary)
        self.assertIn("Stock Quote Summary", summary)
    
    def test_export_quote_summary_no_quote(self):
        """Test exporting quote summary when no quote exists."""
        stock = Stock(symbol="GOOGL")
        summary = export_quote_summary(stock)
        
        self.assertIn("GOOGL", summary)
        self.assertIn("No quote data available", summary)
    
    def test_export_historical_summary(self):
        """Test exporting historical summary."""
        hist_data = [
            HistoricalData(
                symbol="AAPL",
                date=datetime(2024, 1, 14),
                open_price=148.00,
                high_price=151.00,
                low_price=147.00,
                close_price=145.00,
                volume=45000000,
                adjusted_close=145.00
            ),
            HistoricalData(
                symbol="AAPL",
                date=datetime(2024, 1, 15),
                open_price=148.50,
                high_price=152.00,
                low_price=147.50,
                close_price=155.00,
                volume=50000000,
                adjusted_close=155.00
            )
        ]
        self.stock.add_historical_data(hist_data)
        
        summary = export_historical_summary(self.stock)
        
        self.assertIn("AAPL", summary)
        self.assertIn("145.00", summary)  # min price
        self.assertIn("155.00", summary)  # max price
        self.assertIn("Historical Data Summary", summary)
    
    def test_export_historical_summary_no_data(self):
        """Test exporting historical summary when no data exists."""
        stock = Stock(symbol="GOOGL")
        summary = export_historical_summary(stock)
        
        self.assertIn("GOOGL", summary)
        self.assertIn("No historical data available", summary)
    
    def test_export_historical_summary_calculations(self):
        """Test that summary calculations are correct."""
        hist_data = [
            HistoricalData(
                symbol="TEST",
                date=datetime(2024, 1, 10),
                open_price=100.00,
                high_price=105.00,
                low_price=95.00,
                close_price=100.00,
                volume=100000,
                adjusted_close=100.00
            ),
            HistoricalData(
                symbol="TEST",
                date=datetime(2024, 1, 11),
                open_price=100.00,
                high_price=110.00,
                low_price=90.00,
                close_price=110.00,
                volume=200000,
                adjusted_close=110.00
            )
        ]
        stock = Stock(symbol="TEST")
        stock.add_historical_data(hist_data)
        
        summary = export_historical_summary(stock)
        
        # Min: 100.00, Max: 110.00, Avg: 105.00
        self.assertIn("Min Price:        $100.00", summary)
        self.assertIn("Max Price:        $110.00", summary)
        self.assertIn("Avg Price:        $105.00", summary)
        # Total volume: 300000, Avg: 150000
        self.assertIn("Avg Volume:       150,000", summary)


if __name__ == '__main__':
    unittest.main()
