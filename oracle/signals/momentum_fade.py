"""
Momentum Fade Scanner
Identifies stocks that moved > ±5% today without fundamental news, signaling a mean reversion opportunity.
"""
from typing import List
from loguru import logger
import pandas as pd

from oracle.signals.base_scanner import BaseScanner, Signal
from oracle.execution.alpaca_client import get_client
from oracle.config.settings import MOMENTUM_FADE_MIN_MOVE_PCT

class MomentumFadeScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "MomentumFade"

    def scan(self, watchlist: List[str]) -> List[Signal]:
        logger.info(f"[{self.name}] Starting scan of {len(watchlist)} symbols...")
        client = get_client()
        signals = []

        try:
            # 1. Fetch latest snapshots to get today's change %
            snapshots = client.get_stock_snapshot(watchlist)

            for symbol, snapshot in snapshots.items():
                if not snapshot or not snapshot.daily_bar or not snapshot.previous_daily_bar:
                    continue

                prev_close = snapshot.previous_daily_bar.close
                curr_price = snapshot.latest_trade.price
                
                # Protect against division by zero
                if prev_close == 0:
                    continue

                move_pct = ((curr_price - prev_close) / prev_close) * 100

                # 2. Check if the move exceeds our threshold
                if abs(move_pct) >= MOMENTUM_FADE_MIN_MOVE_PCT:
                    direction = "BULLISH" if move_pct < 0 else "BEARISH" # Fade the move!
                    
                    logger.info(f"[{self.name}] Extreme move detected: {symbol} moved {move_pct:.2f}%")
                    
                    # Create signal
                    signal = Signal(
                        symbol=symbol,
                        scanner_name=self.name,
                        confidence=min(60 + abs(move_pct) * 2, 95), # Higher move = higher base confidence
                        underlying_price=curr_price,
                        direction=direction,
                        metadata={
                            "move_pct": move_pct,
                            "prev_close": prev_close,
                        },
                        recommended_strategy="IRON_CONDOR" # Best for harvesting pumped IV during reversion
                    )
                    signals.append(signal)

        except Exception as e:
            logger.error(f"[{self.name}] Error during scan: {e}")

        logger.info(f"[{self.name}] Scan complete. Found {len(signals)} signals.")
        return signals
