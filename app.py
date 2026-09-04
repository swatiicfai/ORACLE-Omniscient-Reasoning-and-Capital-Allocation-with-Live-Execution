"""
ORACLE Streamlit Web Dashboard
"""
import streamlit as st
import pandas as pd
from oracle.execution.alpaca_client import get_client
from oracle.signals.vix_regime import VixRegimeScanner
from oracle.signals.momentum_fade import MomentumFadeScanner
from oracle.council.council import Council
from oracle.execution.order_builder import OrderBuilder
from oracle.narrator.trade_narrator import get_narrator

st.set_page_config(page_title="ORACLE AI Trading Agent", page_icon="🔮", layout="wide")

st.title("🔮 ORACLE — Multi-Agent AI Trading Dashboard")
st.caption("Omniscient Reasoning and Capital Allocation with Live Execution")

st.sidebar.header("Agent Controls")
watchlist = st.sidebar.multiselect("Watchlist Symbols", ["NVDA", "TSLA", "AAPL", "MSFT", "AMD"], default=["NVDA", "TSLA", "AAPL"])
threshold = st.sidebar.slider("Momentum Trigger Threshold (%)", 0.01, 5.0, 0.01, 0.01)

if st.sidebar.button("🚀 Run Live Scan & Council Debate"):
    st.subheader("1. Alpaca Account Status")
    try:
        client = get_client()
        acct = client.get_account()
        col1, col2, col3 = st.columns(3)
        col1.metric("Status", str(acct.status))
        col2.metric("Buying Power", f"${float(acct.buying_power):,.2f}")
        col3.metric("Portfolio Value", f"${float(acct.portfolio_value):,.2f}")
    except Exception as e:
        st.error(f"Alpaca connection failed: {e}")

    st.subheader("2. Market Regime & Signal Scan")
    vix_scanner = VixRegimeScanner()
    regime = vix_scanner.get_current_regime()
    st.info(f"Active Market Regime: **{regime}**")

    scanner = MomentumFadeScanner()
    signals = scanner.scan(watchlist)

    if not signals:
        st.warning("No moves exceeded threshold.")
    else:
        st.success(f"Detected {len(signals)} trade signal(s)!")
        target_signal = sorted(signals, key=lambda x: x.confidence, reverse=True)[0]
        st.write(f"Targeting **{target_signal.symbol}** with strategy **{target_signal.recommended_strategy}**")

        st.subheader("3. 🏛️ Contrarian Council Debate")
        council = Council()
        debate_result = council.debate(target_signal)

        cols = st.columns(3)
        for idx, vote in enumerate(debate_result.votes):
            with cols[idx % 3]:
                st.markdown(f"### {vote.agent_name}")
                st.metric("Decision", vote.decision, f"{vote.confidence}% confidence")
                st.caption(vote.reasoning)

        st.markdown("---")
        st.subheader("4. ⚖️ Judge Ruling")
        if debate_result.approved:
            st.success(f"APPROVED (Score: {debate_result.score}/100)")
        else:
            st.error(f"REJECTED (Score: {debate_result.score}/100)")
        st.write(debate_result.rejection_reason)

st.markdown("---")
st.caption("Powered by Alpaca Trading API, Groq LLM & Streamlit.")
