# ORACLE — Omniscient Reasoning & Capital Allocation with Live Execution

![ORACLE Agent](https://img.shields.io/badge/Agent-Autonomous-purple)
![Alpaca](https://img.shields.io/badge/Alpaca-Options_Trading-yellow)
![Featherless](https://img.shields.io/badge/Featherless_AI-Mistral_7B-blue)

**Built for the 2026 Alpaca AI Trading Agents Hackathon.**

ORACLE is a self-governing, multi-strategy trading intelligence that monitors market edges, debates opportunities internally using a 5-agent "Contrarian Council", executes autonomously via Alpaca, and narrates its reasoning in public.

## The Architecture
ORACLE uses a completely unique pipeline:
1. **Signal Layer:** Scans for momentum fades, IV crush, and tail risks.
2. **Contrarian Council:** 5 distinct LLMs (Bull, Bear, Risk, Quant, Judge) debate the signal.
3. **Execution Engine:** Constructs multi-leg options (Iron Condors) via Alpaca `mleg` API.
4. **Auto-Narrator:** Automatically writes a social media post explaining the trade rationale.

## Quick Start (Hackathon Demo)

1. Clone the repository and navigate into it.
2. Set up your Python environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
   pip install -r requirements.txt
   ```
3. Configure your API keys:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` and add your Alpaca Paper Trading keys and Featherless AI key.*

4. Run the Hackathon Demo:
   ```bash
   python demo.py
   ```
   *Note: For the demo to trigger a trade, you may need to temporarily lower `MOMENTUM_FADE_MIN_MOVE_PCT` in your `.env` to `1.0` if no stocks are moving >5% today.*

## Continuous Mode
To run ORACLE as a continuous daemon (scanning every 15 minutes):
```bash
bash scripts/oracle_cli.sh
```

## MCP Server Integration
ORACLE is designed to work alongside the `alpaca-mcp-server`. Run the MCP server in a separate terminal using `uvx` to allow your IDE to query ORACLE's live portfolio status.

---
*Disclaimer: This is for educational purposes and paper trading only. Do not use for live trading without extensive modification and risk management.*
