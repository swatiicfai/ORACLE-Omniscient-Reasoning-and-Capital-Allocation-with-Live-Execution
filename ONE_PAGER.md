# ORACLE — Architecture & Technical One-Pager

## 1. AI Logic: The Contrarian Council
ORACLE introduces a multi-agent investment committee framework powered by LLMs (OpenAI-compatible / Groq API). Every trade signal passes through an adversarial debate before execution:
- **Bull Agent**: Assesses upside momentum, catalyst strength, and bullish scenarios.
- **Bear Agent**: Identifies downside exposure, macro headwinds, and structural traps.
- **Risk Agent**: Enforces position limits, portfolio correlation checks, and tail-risk bounds.
- **Quant Agent**: Evaluates implied volatility rank, statistical edge, and expected value.
- **Judge Agent**: Synthesizes all perspectives into a unified confidence score (0–100). Trades require a minimum score of 70 to proceed.

## 2. Risk Gates & Safety Mechanics
- **Max Portfolio Risk per Trade**: 2.0% of total capital.
- **Daily Drawdown Circuit Breaker**: Trading halts automatically if daily portfolio loss exceeds 5.0%.
- **Structural Mismatch Protection**: Rejects non-directional strategies (e.g., Iron Condors) on high-beta directional momentum moves.
- **Dynamic VIX Regime Filter**: Adjusts strategy allocation based on market state (`CALM_BULL`, `VOLATILE_BEAR`, `EXTREME_FEAR`).

## 3. Alpaca Infrastructure Implementation
- **Market Data Integration**: Uses `StockHistoricalDataClient` with IEX feed fallback for real-time snapshot scanning and historical volatility calculation.
- **Multi-Leg Execution**: Leverages Alpaca's `mleg` order class to atomically construct multi-leg options orders (Iron Condors).
- **Paper Trading Engine**: Continuously tracks account status, buying power, and portfolio P&L (`PA3WIAHM05TN`).
- **AutoNarrator Social Engine**: Automatically formats and broadcasts trade decisions and Council rationale.
