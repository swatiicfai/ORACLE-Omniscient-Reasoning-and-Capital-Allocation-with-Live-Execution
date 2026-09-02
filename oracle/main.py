"""
ORACLE Main Runner
Orchestrates the entire scanning, debating, and execution loop.
"""
import time
from loguru import logger
import urllib3

# Disable insecure request warnings for simplicity in dev
urllib3.disable_warnings()

from oracle.signals.vix_regime import VixRegimeScanner
from oracle.signals.momentum_fade import MomentumFadeScanner
from oracle.council.council import Council
from oracle.execution.order_builder import OrderBuilder
from oracle.execution.alpaca_client import get_client
from oracle.narrator.trade_narrator import get_narrator
from oracle.config.watchlist import WATCHLIST
from oracle.config.settings import (
    SCAN_INTERVAL_MINUTES, MAX_POSITIONS, MAX_RISK_PER_TRADE_PCT, MIN_CREDIT
)

class Oracle:
    def __init__(self):
        logger.info("Initializing ORACLE Trading System...")
        self.vix_scanner = VixRegimeScanner()
        self.scanners = [
            MomentumFadeScanner(),
            # Add IV Crush, Smart Money etc. here later
        ]
        self.council = Council()
        self.client = get_client()
        self.narrator = get_narrator()

    def run_cycle(self):
        """Run a single end-to-end scanning and execution cycle."""
        logger.info("=" * 60)
        logger.info("🔄 STARTING ORACLE CYCLE")
        logger.info("=" * 60)
        
        # 1. Market Open Check
        if not self.client.is_market_open():
            logger.info("Market is closed. Sleeping...")
            return

        # 2. Global Risk Checks
        open_positions = self.client.get_open_position_count()
        if open_positions >= MAX_POSITIONS:
            logger.warning(f"Max positions reached ({MAX_POSITIONS}). Halting new entries.")
            return

        # 3. Determine Market Regime
        regime = self.vix_scanner.get_current_regime()
        if regime == "CRISIS":
            logger.critical("VIX > 35 (CRISIS). Halting all premium selling strategies.")
            return

        # 4. Generate Signals
        all_signals = []
        for scanner in self.scanners:
            signals = scanner.scan(WATCHLIST)
            all_signals.extend(signals)
            
        if not all_signals:
            logger.info("No actionable signals found in this cycle.")
            return
            
        # 5. Debate & Execute High-Confidence Signals
        for signal in sorted(all_signals, key=lambda x: x.confidence, reverse=True):
            if self.client.get_open_position_count() >= MAX_POSITIONS:
                break
                
            # Convene the council
            debate_result = self.council.debate(signal)
            
            if debate_result.approved:
                # Build Order
                if signal.recommended_strategy == "IRON_CONDOR":
                    order_data = OrderBuilder.build_iron_condor(signal.symbol, signal.underlying_price)
                    
                    if order_data:
                        logger.info(f"Executing trade: {order_data['strikes']}")
                        # We use a static limit price approx for paper trading demo
                        # In prod, we'd fetch live quotes for the 4 legs
                        limit_price = max(MIN_CREDIT, 0.45) 
                        
                        try:
                            # Actually place the order via Alpaca
                            resp = self.client.place_mleg_order(
                                legs=order_data["legs"],
                                limit_price=limit_price,
                                qty=max(1, int(1 * debate_result.suggested_sizing_pct))
                            )
                            logger.success(f"Order filled/placed! ID: {resp.get('id')}")
                            
                            # Narrate Success
                            self.narrator.generate_entry_post(debate_result, order_data)
                            
                        except Exception as e:
                            logger.error(f"Failed to place order: {e}")
            else:
                # Narrate Rejection
                self.narrator.generate_rejection_post(debate_result)

        logger.info("✅ ORACLE cycle complete.")


if __name__ == "__main__":
    oracle = Oracle()
    
    # Run once immediately
    oracle.run_cycle()
    
    # Simple loop for hackathon
    while True:
        logger.info(f"Sleeping for {SCAN_INTERVAL_MINUTES} minutes...")
        time.sleep(SCAN_INTERVAL_MINUTES * 60)
        oracle.run_cycle()
