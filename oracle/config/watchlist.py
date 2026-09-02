# ORACLE Watchlist — High-liquidity optionable symbols
# Chosen for high options volume, tight spreads, and good IV data

WATCHLIST = [
    # Mega-cap tech (highest options liquidity)
    "SPY",   # S&P 500 ETF — most liquid options in the world
    "QQQ",   # Nasdaq 100 ETF
    "AAPL",  # Apple
    "NVDA",  # NVIDIA
    "MSFT",  # Microsoft
    "TSLA",  # Tesla — high IV, great for premium selling
    "AMZN",  # Amazon
    "META",  # Meta
    "GOOGL", # Alphabet
    # Volatility / Macro
    "SPX",   # S&P 500 Index options (cash-settled)
    "IWM",   # Russell 2000 ETF
    "GLD",   # Gold ETF (tail risk hedge)
    # High-IV individual names
    "AMD",   # AMD
    "NFLX",  # Netflix
    "COIN",  # Coinbase
]

# Symbols for tail-risk protection (portfolio hedge)
HEDGE_SYMBOLS = ["SPY", "QQQ"]

# Earnings calendar symbols to monitor (updated weekly)
EARNINGS_WATCHLIST = [
    "AAPL", "NVDA", "MSFT", "TSLA", "AMZN",
    "META", "GOOGL", "AMD", "NFLX", "COIN",
]
