"""
ORACLE — Omniscient Reasoning & Capital Allocation with Live Execution
Configuration settings loaded from .env
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Alpaca ────────────────────────────────────────────────────────────────────
ALPACA_API_KEY    = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL   = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
ALPACA_DATA_URL   = "https://data.alpaca.markets"

# ── AI Provider ──────────────────────────────────────────────────────────────
FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY", "")
FEATHERLESS_MODEL   = os.getenv("FEATHERLESS_MODEL", "qwen/qwen3.8-27b")
FEATHERLESS_BASE_URL = os.getenv("FEATHERLESS_BASE_URL", "https://api.groq.com/openai/v1")

# ── Oracle Core Settings ─────────────────────────────────────────────────────
SCAN_INTERVAL_MINUTES        = int(os.getenv("ORACLE_SCAN_INTERVAL_MINUTES", "15"))
MAX_POSITIONS                = int(os.getenv("ORACLE_MAX_POSITIONS", "6"))
MAX_RISK_PER_TRADE_PCT       = float(os.getenv("ORACLE_MAX_RISK_PER_TRADE_PCT", "2.0"))
DAILY_LOSS_LIMIT_PCT         = float(os.getenv("ORACLE_DAILY_LOSS_LIMIT_PCT", "5.0"))
COUNCIL_APPROVAL_THRESHOLD   = int(os.getenv("ORACLE_COUNCIL_APPROVAL_THRESHOLD", "70"))
PROFIT_TAKE_PCT              = float(os.getenv("ORACLE_PROFIT_TAKE_PCT", "50.0"))
STOP_LOSS_PCT                = float(os.getenv("ORACLE_STOP_LOSS_PCT", "200.0"))

# ── Signal Thresholds ────────────────────────────────────────────────────────
MOMENTUM_FADE_MIN_MOVE_PCT   = float(os.getenv("MOMENTUM_FADE_MIN_MOVE_PCT", "5.0"))
IV_CRUSH_MIN_IV_RANK         = float(os.getenv("IV_CRUSH_MIN_IV_RANK", "40.0"))
SENTIMENT_EXTREME_THRESHOLD  = float(os.getenv("SENTIMENT_EXTREME_THRESHOLD", "80.0"))
VIX_CALM_THRESHOLD           = float(os.getenv("VIX_CALM_THRESHOLD", "15.0"))
VIX_FEAR_THRESHOLD           = float(os.getenv("VIX_FEAR_THRESHOLD", "25.0"))

# ── Options Parameters ────────────────────────────────────────────────────────
TARGET_DTE_MIN  = 21   # minimum days to expiration
TARGET_DTE_MAX  = 45   # maximum days to expiration
SHORT_DELTA     = 0.16 # ~1 sigma OTM (16 delta)
WING_WIDTH      = 5    # points between short and long strike
MIN_CREDIT      = 0.30 # minimum credit per spread to enter

# ── Narrator ─────────────────────────────────────────────────────────────────
NARRATOR_ENABLED     = os.getenv("NARRATOR_ENABLED", "true").lower() == "true"
NARRATOR_OUTPUT_FILE = os.getenv("NARRATOR_OUTPUT_FILE", "narrator_posts.txt")
