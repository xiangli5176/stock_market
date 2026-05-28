"""Stock data fetcher using Robinhood (via robin_stocks).

This module provides an isolated alternative to yfinance-based fetchers,
using the unofficial robin_stocks library to interact with Robinhood's
private API.

WARNING:
    - This module requires your Robinhood login credentials.
    - Automated logins may violate Robinhood's Terms of Service.
    - Your account could be restricted or flagged.
    - Use at your own risk — NOT recommended for production.
"""

import hashlib
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from .models import Stock, Quote, HistoricalData


class RobinhoodAuthError(Exception):
    """Raised when Robinhood authentication fails."""
    pass


class RobinhoodFetcher:
    """Fetch stock data from Robinhood using the robin_stocks library.

    This class encapsulates all Robinhood-specific logic, keeping it
    isolated from the rest of the codebase. It produces the same
    Stock / Quote / HistoricalData models used elsewhere.

    Usage:
        fetcher = RobinhoodFetcher()
        fetcher.login(username="your@email.com", password="your_password")

        # Fetch a quote
        stock = fetcher.fetch_quote("AAPL")
        print(stock.quote.price)

        # Fetch historical data
        stock = fetcher.fetch_historical_data("AAPL", period="week", interval="hour")

        # Always logout when done
        fetcher.logout()

    Attributes:
        logged_in: Whether the fetcher is currently authenticated.
        demo_mode: Whether the fetcher is in demo (no auth) mode.
    """

    # Deterministic "base prices" for well-known symbols (used in demo mode)
    _BASE_PRICES: Dict[str, float] = {
        "AAPL": 178.50, "GOOGL": 141.20, "MSFT": 378.90, "AMZN": 178.30,
        "TSLA": 248.50, "NVDA": 880.30, "META": 495.60, "SPY": 510.40,
        "QQQ": 438.20, "AMD": 162.80, "INTC": 44.30, "NFLX": 575.10,
        "DIS": 111.40, "BA": 180.20, "JPM": 183.70, "V": 275.30,
        "WMT": 165.20, "JNJ": 156.80, "PG": 158.90, "XOM": 117.30,
    }

    def __init__(self, demo_mode: bool = False):
        """Initialize the Robinhood fetcher.

        Args:
            demo_mode: If True, the fetcher runs in demo mode generating
                       synthetic data without requiring Robinhood credentials.
                       Defaults to False.
        """
        self._rh = None  # Will hold the robin_stocks.robinhood module
        self.logged_in = False
        self.demo_mode = demo_mode

    def login(self, username: str, password: str, mfa_code: Optional[str] = None) -> None:
        """Authenticate with Robinhood.

        In demo mode, this is a no-op (fetcher is "logged in" immediately).

        Args:
            username: Robinhood account email/username.
            password: Robinhood account password.
            mfa_code: Optional multi-factor authentication code.
                      If required and not provided, the library will prompt
                      interactively.

        Raises:
            RobinhoodAuthError: If login fails (not in demo mode).
        """
        if self.demo_mode:
            self.logged_in = True
            return

        import robin_stocks.robinhood as rh

        try:
            if mfa_code:
                login_result = rh.login(
                    username=username,
                    password=password,
                    mfa_code=mfa_code,
                )
            else:
                login_result = rh.login(
                    username=username,
                    password=password,
                )

            if not login_result:
                raise RobinhoodAuthError(
                    "Robinhood login returned empty result. "
                    "Check credentials or MFA requirements."
                )

            self._rh = rh
            self.logged_in = True

        except RobinhoodAuthError:
            raise
        except Exception as e:
            raise RobinhoodAuthError(f"Robinhood login failed: {str(e)}")

    def logout(self) -> None:
        """Log out of Robinhood.

        In demo mode, this is a no-op.
        """
        if self.demo_mode:
            self.logged_in = False
            return
        if self._rh and self.logged_in:
            try:
                self._rh.logout()
            except Exception:
                pass  # Best-effort logout
            finally:
                self._rh = None
                self.logged_in = False

    def _require_auth(self) -> None:
        """Ensure the fetcher is authenticated before making API calls.

        In demo mode, this check is automatically satisfied.

        Raises:
            RobinhoodAuthError: If not logged in and not in demo mode.
        """
        if self.demo_mode:
            return
        if not self._rh or not self.logged_in:
            raise RobinhoodAuthError(
                "Not authenticated. Call login() first."
            )

    @staticmethod
    def _parse_price(price_value: Any) -> float:
        """Safely parse a price string to float.

        Robinhood API returns prices as strings (e.g., '178.5000').

        Args:
            price_value: Price value (string, float, int, or None).

        Returns:
            Parsed float, or 0.0 if unparseable.
        """
        if price_value is None:
            return 0.0
        try:
            return float(price_value)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def _parse_volume(volume_value: Any) -> int:
        """Safely parse a volume value to int.

        Args:
            volume_value: Volume value (string, int, or None).

        Returns:
            Parsed int, or 0 if unparseable.
        """
        if volume_value is None:
            return 0
        try:
            return int(float(volume_value))
        except (ValueError, TypeError):
            return 0

    def _get_demo_base_price(self, symbol: str) -> float:
        """Get a deterministic base price for a symbol in demo mode.

        Uses a hash of the symbol to generate a stable price if the symbol
        is not in the known list.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            Base price for demo mode.
        """
        symbol_upper = symbol.upper()
        if symbol_upper in self._BASE_PRICES:
            return self._BASE_PRICES[symbol_upper]

        # Deterministic pseudo-random price based on symbol hash
        hash_val = int(hashlib.md5(symbol_upper.encode()).hexdigest(), 16)
        return 20.0 + (hash_val % 10000) / 100.0  # $20.00 - $120.00

    def _generate_demo_quote(self, symbol: str) -> Quote:
        """Generate a synthetic quote for demo mode.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            Quote object with synthetic data.
        """
        base_price = self._get_demo_base_price(symbol)
        # Add a small random variation so price changes between calls
        noise = random.uniform(-0.02, 0.02) * base_price
        price = round(base_price + noise, 2)
        open_price = round(base_price + random.uniform(-0.01, 0.01) * base_price, 2)
        high_price = round(max(price, open_price) + random.uniform(0, 0.015) * base_price, 2)
        low_price = round(min(price, open_price) - random.uniform(0, 0.015) * base_price, 2)
        volume = random.randint(5000000, 80000000)
        prev_close = round(base_price + random.uniform(-0.01, 0.01) * base_price, 2)

        return Quote(
            symbol=symbol.upper(),
            price=price,
            currency="USD",
            timestamp=datetime.now(),
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            volume=volume,
            previous_close=prev_close,
        )

    def _generate_demo_historical_data(
        self, symbol: str, period: str, interval: str
    ) -> List[HistoricalData]:
        """Generate synthetic historical data for demo mode.

        Args:
            symbol: Stock ticker symbol.
            period: Time span ('day', 'week', 'month', '3month', 'year', '5year').
            interval: Data interval ('5minute', '10minute', 'hour', 'day', 'week').

        Returns:
            List of HistoricalData objects with synthetic but realistic data.
        """
        symbol_upper = symbol.upper()
        base_price = self._get_demo_base_price(symbol_upper)

        # Map period/interval to number of data points
        span_hours = {
            "day": 6.5,  # Trading day ~6.5 hours
            "week": 32.5,
            "month": 143,
            "3month": 429,
            "year": 1716,
            "5year": 8580,
        }
        interval_minutes = {
            "5minute": 5,
            "10minute": 10,
            "hour": 60,
            "day": 1440,
            "week": 10080,
        }

        hours = span_hours.get(period, 429)  # default to 3month
        mins = interval_minutes.get(interval, 1440)  # default to day

        num_points = max(2, int(hours * 60 / mins))

        # Cap to prevent excessive data generation
        num_points = min(num_points, 1000)

        records: List[HistoricalData] = []
        seed = sum(ord(c) for c in symbol_upper)

        # Generate a price series that follows a random walk with drift
        prices = []
        drift = 0.0001  # slight upward drift
        volatility = 0.008  # ~0.8% per period

        rng = random.Random(seed)
        price = base_price
        now = datetime.now()

        for i in range(num_points):
            # Time goes backwards from now
            dt = now - timedelta(minutes=mins * (num_points - i))

            # Random walk
            change = rng.gauss(drift * price, volatility * price)
            price = price + change
            price = max(price, 0.01)  # floor at $0.01

            open_p = round(price, 2)
            high_p = round(price * (1 + abs(rng.gauss(0, 0.005))), 2)
            low_p = round(price * (1 - abs(rng.gauss(0, 0.005))), 2)
            close_p = round(price * (1 + rng.gauss(0, 0.004)), 2)
            volume_val = rng.randint(1000000, 60000000)

            records.append(HistoricalData(
                symbol=symbol_upper,
                date=dt,
                open_price=open_p,
                high_price=max(high_p, open_p, close_p),
                low_price=min(low_p, open_p, close_p),
                close_price=close_p,
                volume=volume_val,
                adjusted_close=close_p,
            ))

        return records

    def fetch_quote(self, symbol: str) -> Optional[Stock]:
        """Fetch current stock quote from Robinhood.

        In demo mode, generates a synthetic quote.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL').

        Returns:
            Stock object with current quote, or None if fetch fails.
        """
        self._require_auth()

        if self.demo_mode:
            quote = self._generate_demo_quote(symbol)
            return Stock(symbol=symbol.upper(), quote=quote)

        try:
            symbol_upper = symbol.upper()
            # Robinhood returns a list of quotes
            quotes_data = self._rh.stocks.get_quotes([symbol_upper])

            if not quotes_data or len(quotes_data) == 0:
                print(f"Warning: Could not fetch quote for {symbol_upper}")
                return Stock(symbol=symbol_upper)

            q = quotes_data[0]

            # Parse the 'updated_at' timestamp
            timestamp = datetime.now()
            try:
                if q.get("updated_at"):
                    timestamp = datetime.fromisoformat(
                        q["updated_at"].replace("Z", "+00:00")
                    )
            except (ValueError, AttributeError):
                pass

            quote = Quote(
                symbol=symbol_upper,
                price=self._parse_price(q.get("last_trade_price")),
                currency="USD",
                timestamp=timestamp,
                open_price=self._parse_price(q.get("open_price")),
                high_price=self._parse_price(q.get("high_price")),
                low_price=self._parse_price(q.get("low_price")),
                volume=self._parse_volume(q.get("volume")),
                previous_close=self._parse_price(q.get("previous_close")),
            )

            return Stock(symbol=symbol_upper, quote=quote)

        except Exception as e:
            print(f"Error fetching quote for {symbol}: {str(e)}")
            return Stock(symbol=symbol)

    def fetch_historical_data(
        self,
        symbol: str,
        period: str = "week",
        interval: str = "10minute",
    ) -> Optional[Stock]:
        """Fetch historical price data from Robinhood.

        Robinhood supports different span/interval combinations:
            span='day'   -> interval='5minute' or '10minute'
            span='week'  -> interval='10minute' or 'hour'
            span='month' -> interval='hour' or 'day'
            span='3month', 'year', '5year' -> interval='day'

        In demo mode, generates synthetic historical data.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL').
            period: Time span ('day', 'week', 'month', '3month', 'year', '5year').
            interval: Data interval ('5minute', '10minute', 'hour', 'day', 'week').

        Returns:
            Stock object with historical data, or None if fetch fails.
        """
        self._require_auth()

        if self.demo_mode:
            records = self._generate_demo_historical_data(symbol, period, interval)
            stock = Stock(symbol=symbol.upper())
            stock.add_historical_data(records)
            return stock

        try:
            symbol_upper = symbol.upper()
            hist_data = self._rh.stocks.get_stock_historicals(
                symbol_upper,
                interval=interval,
                span=period,
            )

            if not hist_data:
                print(f"Warning: No historical data for {symbol_upper}")
                return Stock(symbol=symbol_upper)

            historical_records: List[HistoricalData] = []
            for entry in hist_data:
                # Parse the datetime
                try:
                    date_str = entry.get("begins_at", "")
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    dt = datetime.now()

                open_price = self._parse_price(entry.get("open_price"))
                high_price = self._parse_price(entry.get("high_price"))
                low_price = self._parse_price(entry.get("low_price"))
                close_price = self._parse_price(entry.get("close_price"))
                volume = self._parse_volume(entry.get("volume"))

                # Robinhood does not provide adjusted close; use close_price
                record = HistoricalData(
                    symbol=symbol_upper,
                    date=dt,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume,
                    adjusted_close=close_price,
                )
                historical_records.append(record)

            # Sort chronologically (Robinhood returns newest-first)
            historical_records.sort(key=lambda x: x.date)

            stock = Stock(symbol=symbol_upper)
            stock.add_historical_data(historical_records)
            return stock

        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {str(e)}")
            return Stock(symbol=symbol)

    def fetch_quote_and_history(
        self,
        symbol: str,
        period: str = "week",
        interval: str = "10minute",
    ) -> Optional[Stock]:
        """Fetch both current quote and historical data from Robinhood.

        In demo mode, generates both synthetically.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL').
            period: Time span for historical data.
            interval: Data interval for historical data.

        Returns:
            Stock object with both quote and historical data, or None.
        """
        self._require_auth()

        try:
            stock = self.fetch_quote(symbol)
            if stock:
                hist_stock = self.fetch_historical_data(symbol, period, interval)
                if hist_stock and hist_stock.historical_data:
                    stock.add_historical_data(hist_stock.historical_data)
            return stock
        except Exception as e:
            print(f"Error fetching quote and history for {symbol}: {str(e)}")
            return Stock(symbol=symbol)

    def fetch_multiple_quotes(self, symbols: List[str]) -> Dict[str, Stock]:
        """Fetch quotes for multiple stocks from Robinhood.

        In demo mode, generates synthetic quotes for all symbols.

        Args:
            symbols: List of stock ticker symbols.

        Returns:
            Dictionary mapping symbols to Stock objects.
        """
        self._require_auth()

        if self.demo_mode:
            stocks = {}
            for s in symbols:
                quote = self._generate_demo_quote(s)
                stocks[s.upper()] = Stock(symbol=s.upper(), quote=quote)
            return stocks

        stocks = {}
        try:
            # Robinhood supports batch quote fetching
            symbols_upper = [s.upper() for s in symbols]
            quotes_data = self._rh.stocks.get_quotes(symbols_upper)

            if quotes_data:
                for q in quotes_data:
                    symbol = q.get("symbol", "").upper()
                    if not symbol:
                        continue

                    timestamp = datetime.now()
                    try:
                        if q.get("updated_at"):
                            timestamp = datetime.fromisoformat(
                                q["updated_at"].replace("Z", "+00:00")
                            )
                    except (ValueError, AttributeError):
                        pass

                    quote = Quote(
                        symbol=symbol,
                        price=self._parse_price(q.get("last_trade_price")),
                        currency="USD",
                        timestamp=timestamp,
                        open_price=self._parse_price(q.get("open_price")),
                        high_price=self._parse_price(q.get("high_price")),
                        low_price=self._parse_price(q.get("low_price")),
                        volume=self._parse_volume(q.get("volume")),
                        previous_close=self._parse_price(q.get("previous_close")),
                    )
                    stocks[symbol] = Stock(symbol=symbol, quote=quote)

            # Fill in any missing symbols with empty Stock objects
            for s in symbols_upper:
                if s not in stocks:
                    stocks[s] = Stock(symbol=s)

        except Exception as e:
            print(f"Error fetching multiple quotes: {str(e)}")
            for s in symbols:
                stocks[s.upper()] = Stock(symbol=s)

        return stocks

    def fetch_account_info(self) -> Optional[Dict[str, Any]]:
        """Fetch Robinhood account information.

        In demo mode, returns mock account information.

        Returns:
            Dictionary with account details (buying power, portfolio value, etc.),
            or None if fetch fails.

        NOTE: This returns Robinhood-specific data not available via yfinance.
        """
        self._require_auth()

        if self.demo_mode:
            return {
                "account_number": "DEMO-ACCT-12345",
                "buying_power": 15750.42,
                "cash": 12500.00,
                "portfolio_value": 97500.00,
                "equity": 97500.00,
                "currency": "USD",
            }

        try:
            profile = self._rh.profiles.load_account_profile()
            portfolio = self._rh.profiles.load_portfolio_profile()

            if not profile:
                return None

            return {
                "account_number": profile.get("account_number"),
                "buying_power": self._parse_price(profile.get("buying_power")),
                "cash": self._parse_price(profile.get("cash")),
                "portfolio_value": self._parse_price(
                    portfolio.get("market_value") if portfolio else None
                ),
                "equity": self._parse_price(
                    portfolio.get("equity") if portfolio else None
                ),
                "currency": "USD",
            }
        except Exception as e:
            print(f"Error fetching account info: {str(e)}")
            return None

    def fetch_positions(self) -> List[Dict[str, Any]]:
        """Fetch current stock positions from Robinhood portfolio.

        In demo mode, returns mock positions for popular stocks.

        Returns:
            List of dictionaries with position details (symbol, quantity,
            average buy price, current price, etc.).

        NOTE: This returns Robinhood-specific data not available via yfinance.
        """
        self._require_auth()

        if self.demo_mode:
            return [
                {
                    "symbol": "AAPL",
                    "quantity": 25.0,
                    "average_buy_price": 165.30,
                    "equity": self._get_demo_base_price("AAPL") * 25,
                    "percent_change": 8.2,
                    "equity_change": (self._get_demo_base_price("AAPL") - 165.30) * 25,
                },
                {
                    "symbol": "MSFT",
                    "quantity": 10.0,
                    "average_buy_price": 350.00,
                    "equity": self._get_demo_base_price("MSFT") * 10,
                    "percent_change": 8.3,
                    "equity_change": (self._get_demo_base_price("MSFT") - 350.00) * 10,
                },
                {
                    "symbol": "NVDA",
                    "quantity": 5.0,
                    "average_buy_price": 820.00,
                    "equity": self._get_demo_base_price("NVDA") * 5,
                    "percent_change": 7.4,
                    "equity_change": (self._get_demo_base_price("NVDA") - 820.00) * 5,
                },
            ]

        try:
            positions = self._rh.account.build_holdings()
            results: List[Dict[str, Any]] = []

            for symbol, pos in positions.items():
                results.append({
                    "symbol": symbol,
                    "quantity": self._parse_price(pos.get("quantity")),
                    "average_buy_price": self._parse_price(
                        pos.get("average_buy_price")
                    ),
                    "equity": self._parse_price(pos.get("equity")),
                    "percent_change": self._parse_price(
                        pos.get("percent_change")
                    ),
                    "equity_change": self._parse_price(
                        pos.get("equity_change")
                    ),
                })

            return results
        except Exception as e:
            print(f"Error fetching positions: {str(e)}")
            return []


class RobinhoodFetcherBuilder:
    """Builder for creating RobinhoodFetcher instances with login.

    This provides a cleaner way to create an authenticated fetcher:

        fetcher = (RobinhoodFetcherBuilder()
                   .with_credentials("user@email.com", "password")
                   .build())
    """

    def __init__(self):
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._mfa_code: Optional[str] = None
        self._demo_mode: bool = False

    def with_credentials(
        self, username: str, password: str
    ) -> "RobinhoodFetcherBuilder":
        """Set Robinhood login credentials."""
        self._username = username
        self._password = password
        return self

    def with_mfa(self, mfa_code: str) -> "RobinhoodFetcherBuilder":
        """Set MFA code for login."""
        self._mfa_code = mfa_code
        return self

    def as_demo(self) -> "RobinhoodFetcherBuilder":
        """Set the fetcher to run in demo mode (no credentials needed)."""
        self._demo_mode = True
        return self

    def build(self) -> RobinhoodFetcher:
        """Build and return an authenticated RobinhoodFetcher.

        Raises:
            RobinhoodAuthError: If credentials are missing or login fails.
        """
        if self._demo_mode:
            fetcher = RobinhoodFetcher(demo_mode=True)
            fetcher.login(username="", password="")
            return fetcher

        if not self._username or not self._password:
            raise RobinhoodAuthError(
                "Username and password are required. Call with_credentials()."
            )

        fetcher = RobinhoodFetcher()
        fetcher.login(
            username=self._username,
            password=self._password,
            mfa_code=self._mfa_code,
        )
        return fetcher