"""
ORACLE Order Builder
Constructs complex multi-leg options orders (e.g. Iron Condors) for Alpaca.
"""
from loguru import logger
from datetime import datetime, timedelta
import math

from oracle.execution.alpaca_client import get_client
from oracle.config.settings import (
    TARGET_DTE_MIN, TARGET_DTE_MAX, WING_WIDTH
)

class OrderBuilder:
    
    @staticmethod
    def _find_target_expiry(contracts: list) -> str:
        """Finds an expiration date between TARGET_DTE_MIN and TARGET_DTE_MAX."""
        if not contracts:
            return None
            
        today = datetime.now().date()
        target_min = today + timedelta(days=TARGET_DTE_MIN)
        target_max = today + timedelta(days=TARGET_DTE_MAX)
        
        # Extract unique dates
        dates = sorted(list(set([c.expiration_date for c in contracts])))
        
        # Try to find one in the sweet spot
        for d in dates:
            d_obj = datetime.strptime(d, "%Y-%m-%d").date()
            if target_min <= d_obj <= target_max:
                return d
                
        # Fallback to the furthest date if none in range, or closest if all far
        return dates[-1] if dates else None

    @staticmethod
    def build_iron_condor(symbol: str, underlying_price: float) -> dict:
        """
        Builds a neutral Iron Condor payload for the MLeg API.
        Sells strikes roughly +- 1 stdev away, buys wings outside of that.
        Returns None if unable to construct.
        """
        client = get_client()
        logger.info(f"[OrderBuilder] Constructing Iron Condor for {symbol} @ {underlying_price}")
        
        try:
            # 1. Fetch contracts for next 60 days
            start_date = (datetime.now() + timedelta(days=TARGET_DTE_MIN)).strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=TARGET_DTE_MAX + 15)).strftime("%Y-%m-%d")
            
            contracts = client.get_option_chain(symbol, start_date, end_date)
            
            if not contracts:
                logger.warning(f"[OrderBuilder] No contracts found for {symbol} in date range")
                return None
                
            expiry = OrderBuilder._find_target_expiry(contracts)
            if not expiry:
                return None
                
            # 2. Filter contracts for this expiry
            expiry_chain = [c for c in contracts if c.expiration_date == expiry]
            
            calls = sorted([c for c in expiry_chain if c.type == "call"], key=lambda x: float(x.strike_price))
            puts = sorted([c for c in expiry_chain if c.type == "put"], key=lambda x: float(x.strike_price))
            
            if not calls or not puts:
                return None
                
            # 3. Determine Strikes (Simplified 16 delta approx: ~7% out of the money)
            # In a full quant system, we'd use Black-Scholes delta. For hackathon, % offset is fine.
            offset_pct = 0.07 
            
            short_call_strike = underlying_price * (1 + offset_pct)
            short_put_strike = underlying_price * (1 - offset_pct)
            
            # Find closest actual strikes
            short_call = min(calls, key=lambda x: abs(float(x.strike_price) - short_call_strike))
            short_put = min(puts, key=lambda x: abs(float(x.strike_price) - short_put_strike))
            
            long_call_strike = float(short_call.strike_price) + WING_WIDTH
            long_put_strike = float(short_put.strike_price) - WING_WIDTH
            
            long_call = min(calls, key=lambda x: abs(float(x.strike_price) - long_call_strike))
            long_put = min(puts, key=lambda x: abs(float(x.strike_price) - long_put_strike))
            
            # 4. Construct MLeg Payload
            legs = [
                # Short Call
                {"symbol": short_call.symbol, "ratio_qty": 1, "side": "sell", "position_intent": "sell_to_open"},
                # Long Call (Wing)
                {"symbol": long_call.symbol, "ratio_qty": 1, "side": "buy", "position_intent": "buy_to_open"},
                # Short Put
                {"symbol": short_put.symbol, "ratio_qty": 1, "side": "sell", "position_intent": "sell_to_open"},
                # Long Put (Wing)
                {"symbol": long_put.symbol, "ratio_qty": 1, "side": "buy", "position_intent": "buy_to_open"},
            ]
            
            logger.info(f"[OrderBuilder] Iron Condor legs built for {symbol} expiring {expiry}")
            return {
                "strategy": "IRON_CONDOR",
                "legs": legs,
                "expiry": expiry,
                "strikes": f"P{long_put.strike_price}/{short_put.strike_price} - C{short_call.strike_price}/{long_call.strike_price}"
            }
            
        except Exception as e:
            logger.error(f"[OrderBuilder] Error building condor for {symbol}: {e}")
            return None
