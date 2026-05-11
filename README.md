# Stock Market Information Tracing App

A Python application for fetching, tracking, and analyzing stock market information using **yfinance** - a safe, mature, and official-friendly market data API.

## Features

- **Current Stock Quotes**: Fetch real-time stock price information including open, high, low, volume, and more
- **Historical Price Data**: Retrieve historical OHLCV (Open, High, Low, Close, Volume) data for any time period
- **Multi-Stock Support**: Fetch data for multiple stocks simultaneously
- **CSV Export**: Export quotes and historical data to CSV files for further analysis
- **Price Analytics**: Calculate price changes and percentage changes
- **Formatted Output**: Beautiful summaries and formatted data output

## Project Structure

```
stock_market/
├── src/
│   ├── __init__.py          # Main API exports
│   ├── models.py            # Data models (Stock, Quote, HistoricalData)
│   ├── fetcher.py           # Stock data fetcher using yfinance
│   └── utils.py             # Utility functions for CSV export and formatting
├── demo/
│   └── stock_tracking_examples.ipynb  # Example Jupyter notebook
├── requirements.txt         # Project dependencies
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/stock_market.git
cd stock_market
```

### 2. Create a Virtual Environment (Recommended)

```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example: Fetch a Stock Quote

```python
from src import StockFetcher, print_quote_summary

# Initialize fetcher
fetcher = StockFetcher()

# Fetch current quote
stock = fetcher.fetch_quote("AAPL")

# Print summary
print_quote_summary(stock)

# Access data
print(f"Current Price: ${stock.quote.price:.2f}")
print(f"Price Change: {stock.get_price_change_percent():.2f}%")
```

### Fetch Historical Data

```python
from src import StockFetcher, print_historical_summary, export_historical_to_csv

fetcher = StockFetcher()

# Fetch 1 month of historical data
stock = fetcher.fetch_historical_data("AAPL", period="1mo")

# Print summary
print_historical_summary(stock)

# Export to CSV
export_historical_to_csv(stock)
```

### Fetch Quote and Historical Data Together

```python
from src import StockFetcher, print_quote_summary, print_historical_summary

fetcher = StockFetcher()

# Fetch both current quote and historical data (3 months)
stock = fetcher.fetch_quote_and_history("AAPL", period="3mo")

print_quote_summary(stock)
print_historical_summary(stock)
```

### Export Data to CSV

```python
from src import StockFetcher, export_quote_to_csv, export_historical_to_csv

fetcher = StockFetcher()
stock = fetcher.fetch_quote_and_history("AAPL", period="6mo")

# Export quote to CSV
quote_file = export_quote_to_csv(stock)  # data/AAPL_quote.csv

# Export historical to CSV
history_file = export_historical_to_csv(stock)  # data/AAPL_historical.csv

print(f"Quote saved to: {quote_file}")
print(f"History saved to: {history_file}")
```

### Fetch Multiple Stocks

```python
from src import StockFetcher

fetcher = StockFetcher()

# Fetch quotes for multiple stocks
symbols = ["AAPL", "GOOGL", "MSFT", "AMZN"]
stocks = fetcher.fetch_multiple_quotes(symbols)

for symbol, stock in stocks.items():
    if stock.quote:
        print(f"{symbol}: ${stock.quote.price:.2f}")
```

## API Reference

### StockFetcher

Main class for fetching stock data.

**Methods:**

- `fetch_quote(symbol)` - Fetch current quote for a stock
- `fetch_historical_data(symbol, period="1mo", interval="1d")` - Fetch historical data
- `fetch_quote_and_history(symbol, period="1mo", interval="1d")` - Fetch both quote and historical data
- `fetch_multiple_quotes(symbols)` - Fetch quotes for multiple stocks
- `fetch_multiple_historical(symbols, period="1mo", interval="1d")` - Fetch historical data for multiple stocks

**Parameters:**

- `symbol` (str): Stock ticker symbol (e.g., "AAPL", "GOOGL")
- `period` (str): Time period for historical data
  - Valid values: `"1d"`, `"5d"`, `"1mo"`, `"3mo"`, `"6mo"`, `"1y"`, `"2y"`, `"5y"`, `"10y"`, `"max"`
- `interval` (str): Data interval
  - Valid values: `"1m"`, `"5m"`, `"15m"`, `"30m"`, `"60m"`, `"1d"`, `"1wk"`, `"1mo"`

### Data Models

**Stock**
- `symbol`: Stock ticker symbol
- `quote`: Current quote (Quote object)
- `historical_data`: List of HistoricalData objects
- Methods:
  - `get_latest_price()` - Get current price
  - `get_price_change()` - Get absolute price change
  - `get_price_change_percent()` - Get percentage price change

**Quote**
- `symbol`: Stock ticker
- `price`: Current price
- `currency`: Currency code
- `timestamp`: Quote timestamp
- `open_price`: Opening price
- `high_price`: High price of the day
- `low_price`: Low price of the day
- `volume`: Trading volume
- `previous_close`: Previous closing price

**HistoricalData**
- `symbol`: Stock ticker
- `date`: Date of the data
- `open_price`: Opening price
- `high_price`: High price
- `low_price`: Low price
- `close_price`: Closing price
- `volume`: Trading volume
- `adjusted_close`: Adjusted closing price

### Utility Functions

- `export_quote_to_csv(stock, filepath=None)` - Export quote to CSV
- `export_historical_to_csv(stock, filepath=None)` - Export historical data to CSV
- `print_quote_summary(stock)` - Print formatted quote summary
- `print_historical_summary(stock)` - Print formatted historical summary
- `format_price(price)` - Format price with dollar sign
- `format_volume(volume)` - Format volume with separators
- `format_percent(percent)` - Format percentage with sign

## Data Sources

This app uses **yfinance**, which provides access to Yahoo Finance data:
- Real-time stock quotes
- Historical price data
- Dividend and split data
- Company information

yfinance is the most popular and mature unofficial wrapper for Yahoo Finance data in Python.

## Examples

See the `demo/stock_tracking_examples.ipynb` Jupyter notebook for comprehensive examples including:
- Fetching and displaying stock quotes
- Analyzing historical price trends
- Comparing multiple stocks
- Exporting data for further analysis

To run the notebook:

```bash
jupyter notebook demo/stock_tracking_examples.ipynb
```

## Limitations

- Data provided by Yahoo Finance (via yfinance) may have slight delays
- Real-time data (< 15 minutes) requires premium Yahoo Finance account
- Some stocks may have missing historical data
- International markets have varying data availability

## Error Handling

The application gracefully handles errors:
- Network failures
- Invalid stock symbols
- Missing data

When errors occur, you'll receive a warning message and an empty or partial Stock object to work with.

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## License

MIT License - See LICENSE file for details

## Disclaimer

This application is for educational and informational purposes only. It is not financial advice. Always consult with a financial advisor before making investment decisions.

## Support

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Include error messages and code examples

---

**Happy tracking! 📈**
