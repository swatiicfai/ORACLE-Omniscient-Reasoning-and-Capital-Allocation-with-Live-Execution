"""
ORACLE Alpaca Client — wrapper around alpaca-py TradingClient + DataClient
"""
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest, LimitOrderRequest, GetOrdersRequest,
    GetOptionContractsRequest,
)
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus, AssetClass
from alpaca.data.historical import StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.requests import (
    StockBarsRequest, StockSnapshotRequest,
    OptionChainRequest, OptionLatestQuoteRequest,
)
from alpaca.data.timeframe import TimeFrame
from loguru import logger
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

from oracle.config.settings import (
    ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
)


class AlpacaClient:
    """Unified Alpaca client for trading + market data."""

    def __init__(self):
        self.trading = TradingClient(
            api_key=ALPACA_API_KEY,
            secret_key=ALPACA_SECRET_KEY,
            paper=True,
            url_override=ALPACA_BASE_URL,
        )
        self.stock_data = StockHistoricalDataClient(
            api_key=ALPACA_API_KEY,
            secret_key=ALPACA_SECRET_KEY,
        )
        self.option_data = OptionHistoricalDataClient(
            api_key=ALPACA_API_KEY,
            secret_key=ALPACA_SECRET_KEY,
        )
        logger.info("✅ Alpaca client initialized (paper trading)")

    # ── Account ───────────────────────────────────────────────────────────────

    def get_account(self):
        """Return account object with equity, buying power, P&L."""
        return self.trading.get_account()

    def get_equity(self) -> float:
        acct = self.get_account()
        return float(acct.equity)

    def get_buying_power(self) -> float:
        acct = self.get_account()
        return float(acct.buying_power)

    def get_portfolio_value(self) -> float:
        acct = self.get_account()
        return float(acct.portfolio_value)

    # ── Positions ─────────────────────────────────────────────────────────────

    def get_all_positions(self):
        return self.trading.get_all_positions()

    def get_open_position_count(self) -> int:
        return len(self.get_all_positions())

    def close_position(self, symbol: str):
        logger.info(f"Closing position: {symbol}")
        return self.trading.close_position(symbol)

    # ── Orders ────────────────────────────────────────────────────────────────

    def get_open_orders(self):
        req = GetOrdersRequest(status=OrderStatus.OPEN)
        return self.trading.get_orders(filter=req)

    def cancel_all_orders(self):
        return self.trading.cancel_orders()

    def place_market_order(self, symbol: str, qty: int, side: OrderSide,
                           time_in_force: TimeInForce = TimeInForce.DAY):
        req = MarketOrderRequest(
            symbol=symbol, qty=qty, side=side, time_in_force=time_in_force
        )
        return self.trading.submit_order(req)

    def place_limit_order(self, symbol: str, qty: int, side: OrderSide,
                          limit_price: float,
                          time_in_force: TimeInForce = TimeInForce.DAY):
        req = LimitOrderRequest(
            symbol=symbol, qty=qty, side=side,
            limit_price=round(limit_price, 2),
            time_in_force=time_in_force,
        )
        return self.trading.submit_order(req)

    def place_mleg_order(self, legs: list, limit_price: float, qty: int = 1,
                         time_in_force: TimeInForce = TimeInForce.DAY):
        """
        Place a multi-leg options order (Iron Condor, Spread, Straddle, etc.)
        legs = [{"symbol": ..., "ratio_qty": 1, "side": "buy"|"sell",
                 "position_intent": "buy_to_open"|"sell_to_open"}]
        """
        import httpx, json
        from oracle.config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY

        payload = {
            "order_class": "mleg",
            "qty": str(qty),
            "type": "limit",
            "limit_price": str(round(limit_price, 2)),
            "time_in_force": time_in_force.value,
            "legs": legs,
        }
        headers = {
            "APCA-API-KEY-ID": ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
            "accept": "application/json",
            "content-type": "application/json",
        }
        response = httpx.post(
            f"{ALPACA_BASE_URL}/v2/orders",
            headers=headers,
            content=json.dumps(payload),
            timeout=30,
        )
        response.raise_for_status()
        logger.info(f"✅ MLeg order placed: {response.json().get('id')}")
        return response.json()

    # ── Market Data ───────────────────────────────────────────────────────────

    def get_stock_snapshot(self, symbols: list) -> dict:
        """Latest price, bar, quote for multiple symbols."""
        req = StockSnapshotRequest(symbol_or_symbols=symbols, feed="iex")
        return self.stock_data.get_stock_snapshot(req)

    def get_historical_bars(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Daily bars for IV rank computation."""
        end   = datetime.now()
        start = end - timedelta(days=days)
        req   = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start,
            end=end,
            feed="iex"
        )
        bars = self.stock_data.get_stock_bars(req)
        return bars.df if hasattr(bars, "df") else pd.DataFrame()

    def get_option_chain(self, symbol: str, expiration_date_gte: str,
                         expiration_date_lte: str) -> list:
        """Fetch option contracts for a symbol within date range."""
        req = GetOptionContractsRequest(
            underlying_symbols=[symbol],
            expiration_date_gte=expiration_date_gte,
            expiration_date_lte=expiration_date_lte,
            status="active",
        )
        contracts = self.trading.get_option_contracts(req)
        return contracts.option_contracts if hasattr(contracts, "option_contracts") else []

    def get_option_latest_quote(self, symbols: list) -> dict:
        """Latest bid/ask for option symbols."""
        req = OptionLatestQuoteRequest(symbol_or_symbols=symbols)
        return self.option_data.get_option_latest_quote(req)

    def get_clock(self):
        """Market clock — is market open?"""
        return self.trading.get_clock()

    def is_market_open(self) -> bool:
        return self.get_clock().is_open


# Singleton instance
_client: Optional[AlpacaClient] = None


def get_client() -> AlpacaClient:
    global _client
    if _client is None:
        _client = AlpacaClient()
    return _client
