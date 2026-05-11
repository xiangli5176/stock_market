"""Utility functions for data export and formatting."""

import csv
from pathlib import Path
from typing import List, Optional
from .models import Stock, Quote, HistoricalData


def export_quote_to_csv(
    stock: Stock,
    filepath: str = None
) -> str:
    """Export stock quote to CSV file.
    
    Args:
        stock: Stock object with quote data
        filepath: Output file path (default: data/{symbol}_quote.csv)
        
    Returns:
        Path to the exported file
    """
    if not stock.quote:
        raise ValueError(f"No quote data available for {stock.symbol}")
    
    if filepath is None:
        Path("data").mkdir(exist_ok=True)
        filepath = f"data/{stock.symbol}_quote.csv"
    
    quote = stock.quote
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Symbol', 'Price', 'Currency', 'Timestamp',
            'Open', 'High', 'Low', 'Volume', 'Previous Close'
        ])
        writer.writerow([
            quote.symbol,
            f"{quote.price:.2f}",
            quote.currency,
            quote.timestamp.isoformat(),
            f"{quote.open_price:.2f}",
            f"{quote.high_price:.2f}",
            f"{quote.low_price:.2f}",
            quote.volume,
            f"{quote.previous_close:.2f}"
        ])
    
    print(f"Quote exported to {filepath}")
    return filepath


def export_historical_to_csv(
    stock: Stock,
    filepath: str = None
) -> str:
    """Export stock historical data to CSV file.
    
    Args:
        stock: Stock object with historical data
        filepath: Output file path (default: data/{symbol}_historical.csv)
        
    Returns:
        Path to the exported file
    """
    if not stock.historical_data:
        raise ValueError(f"No historical data available for {stock.symbol}")
    
    if filepath is None:
        Path("data").mkdir(exist_ok=True)
        filepath = f"data/{stock.symbol}_historical.csv"
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Symbol', 'Date', 'Open', 'High', 'Low', 'Close',
            'Adjusted Close', 'Volume'
        ])
        
        for data in stock.historical_data:
            writer.writerow([
                data.symbol,
                data.date.date(),
                f"{data.open_price:.2f}",
                f"{data.high_price:.2f}",
                f"{data.low_price:.2f}",
                f"{data.close_price:.2f}",
                f"{data.adjusted_close:.2f}",
                data.volume
            ])
    
    print(f"Historical data exported to {filepath}")
    return filepath


def export_quote_summary(stock: Stock) -> str:
    """Generate a formatted summary of stock quote.
    
    Args:
        stock: Stock object with quote data
        
    Returns:
        Formatted string with quote summary
    """
    if not stock.quote:
        return f"{stock.symbol}: No quote data available"
    
    quote = stock.quote
    change = stock.get_price_change()
    change_pct = stock.get_price_change_percent()
    
    change_str = f"{change:+.2f}" if change is not None else "N/A"
    change_pct_str = f"{change_pct:+.2f}%" if change_pct is not None else "N/A"
    
    summary = f"""
Stock Quote Summary - {quote.symbol}
{'='*50}
Current Price:    ${quote.price:.2f}
Open Price:       ${quote.open_price:.2f}
High (Day):       ${quote.high_price:.2f}
Low (Day):        ${quote.low_price:.2f}
Previous Close:   ${quote.previous_close:.2f}
Price Change:     {change_str} ({change_pct_str})
Volume:           {quote.volume:,}
Currency:         {quote.currency}
Timestamp:        {quote.timestamp}
{'='*50}
"""
    return summary


def print_quote_summary(stock: Stock) -> None:
    """Print a formatted summary of stock quote.
    
    Args:
        stock: Stock object with quote data
    """
    print(export_quote_summary(stock))


def export_historical_summary(stock: Stock) -> str:
    """Generate a formatted summary of historical data.
    
    Args:
        stock: Stock object with historical data
        
    Returns:
        Formatted string with historical summary
    """
    if not stock.historical_data:
        return f"{stock.symbol}: No historical data available"
    
    data = stock.historical_data
    if not data:
        return "No data"
    
    closing_prices = [d.close_price for d in data]
    min_price = min(closing_prices)
    max_price = max(closing_prices)
    avg_price = sum(closing_prices) / len(closing_prices)
    
    volumes = [d.volume for d in data]
    avg_volume = sum(volumes) / len(volumes)
    
    summary = f"""
Historical Data Summary - {stock.symbol}
{'='*50}
Period:           {data[0].date.date()} to {data[-1].date.date()}
Data Points:      {len(data)}
Min Price:        ${min_price:.2f}
Max Price:        ${max_price:.2f}
Avg Price:        ${avg_price:.2f}
Avg Volume:       {int(avg_volume):,}
Latest Close:     ${data[-1].close_price:.2f}
{'='*50}
"""
    return summary


def print_historical_summary(stock: Stock) -> None:
    """Print a formatted summary of historical data.
    
    Args:
        stock: Stock object with historical data
    """
    print(export_historical_summary(stock))


def format_price(price: float) -> str:
    """Format price to 2 decimal places with dollar sign.
    
    Args:
        price: Price value
        
    Returns:
        Formatted price string
    """
    return f"${price:.2f}"


def format_volume(volume: int) -> str:
    """Format volume with thousand separators.
    
    Args:
        volume: Volume value
        
    Returns:
        Formatted volume string
    """
    return f"{volume:,}"


def format_percent(percent: float) -> str:
    """Format percentage with sign.
    
    Args:
        percent: Percentage value
        
    Returns:
        Formatted percentage string
    """
    return f"{percent:+.2f}%"
