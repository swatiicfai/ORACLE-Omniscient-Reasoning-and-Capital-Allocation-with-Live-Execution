"""
VIX Regime Scanner
Monitors SPX/VIX equivalents to determine current market regime.
Since VIX index data requires a paid subscription on Alpaca, we use an approximation via SPY volatility or VIXY if available.
For hackathon purposes, we'll approximate regime using recent SPY true range or hardcode a calm regime for testing.
"""
from typing import List
from loguru import logger
import pandas as pd
import numpy as np

from oracle.signals.base_scanner import BaseScanner, Signal
from oracle.execution.alpaca_client import get_client
from oracle.config.settings import VIX_CALM_THRESHOLD, VIX_FEAR_THRESHOLD

class VixRegimeScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "VixRegime"

    def _estimate_vix(self) -> float:
        """Estimate VIX using SPY recent volatility (20-day historical volatility annualized)."""
        client = get_client()
        try:
            # Get 21 days of SPY bars
            df = client.get_historical_bars("SPY", days=30)
            if df.empty or len(df) < 10:
                logger.warning("[VixRegime] Insufficient SPY data to estimate VIX. Defaulting to 18.0")
                return 18.0
                
            # Ensure we're using just the close column if it's a multiindex dataframe
            if isinstance(df.index, pd.MultiIndex):
                # alpaca-py returns multiindex (symbol, timestamp)
                closes = df.xs("SPY", level="symbol")["close"]
            else:
                closes = df["close"]
                
            # Calculate daily returns
            daily_returns = closes.pct_change().dropna()
            
            # Annualized historical volatility (proxy for VIX)
            # VIX is roughly annualized standard deviation * 100
            hv = daily_returns.std() * np.sqrt(252) * 100
            
            # Sanity check constraints (cap between 10 and 80)
            estimated_vix = max(10.0, min(hv, 80.0))
            return round(estimated_vix, 2)
            
        except Exception as e:
            logger.error(f"[VixRegime] Error estimating VIX: {e}")
            return 18.0 # Safe default

    def get_current_regime(self) -> str:
        """Returns the current market regime string."""
        vix_val = self._estimate_vix()
        
        if vix_val < VIX_CALM_THRESHOLD:
            return "CALM_BULL"
        elif vix_val < VIX_FEAR_THRESHOLD:
            return "NORMAL"
        elif vix_val < 35.0:
            return "FEAR"
        else:
            return "CRISIS"

    def scan(self, watchlist: List[str]) -> List[Signal]:
        """
        VIX scanner doesn't generate specific stock signals, 
        but emits a global regime signal that the router uses.
        """
        vix_val = self._estimate_vix()
        regime = self.get_current_regime()
        
        logger.info(f"[{self.name}] Estimated VIX: {vix_val} | Regime: {regime}")
        
        # We emit a "macro" signal
        return [Signal(
            symbol="MACRO",
            scanner_name=self.name,
            confidence=100.0,
            underlying_price=vix_val,
            direction="VOLATILE" if regime in ["FEAR", "CRISIS"] else "NEUTRAL",
            metadata={"vix": vix_val, "regime": regime},
            recommended_strategy="NONE"
        )]
