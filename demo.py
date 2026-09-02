"""
ORACLE Demo Script
A simplified version of main.py designed to run immediately and print output clearly for a hackathon video demo.
"""
from loguru import logger
import urllib3
import sys

# Configure loguru for beautiful terminal output during demo
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

urllib3.disable_warnings()

from oracle.signals.vix_regime import VixRegimeScanner
from oracle.signals.momentum_fade import MomentumFadeScanner
from oracle.council.council import Council
from oracle.execution.order_builder import OrderBuilder
from oracle.execution.alpaca_client import get_client
from oracle.narrator.trade_narrator import get_narrator
from oracle.config.settings import MIN_CREDIT

# A smaller watchlist just for the demo to run fast
DEMO_WATCHLIST = ["NVDA", "TSLA", "AAPL"]

def run_demo():
    print("\n" + "="*70)
    print(" [ORACLE] MEGA-AGENT INITIATED - DEMO SEQUENCE")
    print("="*70 + "\n")
    
    client = get_client()
    narrator = get_narrator()
    council = Council()
    
    # 1. Check account
    try:
        acct = client.get_account()
        logger.info(f"Connected to Alpaca Paper Trading. Account Status: {acct.status}")
        logger.info(f"Starting Buying Power: ${float(acct.buying_power):,.2f}")
    except Exception as e:
        logger.error(f"Failed to connect to Alpaca. Check your .env API keys. Error: {e}")
        return

    # 2. VIX Regime Scan
    vix_scanner = VixRegimeScanner()
    regime = vix_scanner.get_current_regime()
    logger.info(f"Active Market Regime: {regime}")

    # 3. Momentum Fade Scan
    scanner = MomentumFadeScanner()
    signals = scanner.scan(DEMO_WATCHLIST)
    
    if not signals:
        logger.warning(f"No >5% moves detected in {DEMO_WATCHLIST} today.")
        logger.info("For the hackathon demo, you can temporarily lower MOMENTUM_FADE_MIN_MOVE_PCT in .env to 1.0 to force a signal.")
        return

    # 4. Take the strongest signal and debate it
    target_signal = sorted(signals, key=lambda x: x.confidence, reverse=True)[0]
    logger.info(f"Targeting {target_signal.symbol} with {target_signal.recommended_strategy} strategy.")
    
    # 5. Debate
    logger.info("\n" + "-"*50)
    logger.info("[COUNCIL] CONVENING THE CONTRARIAN COUNCIL")
    logger.info("-"*50)
    
    debate_result = council.debate(target_signal)
    
    print("\n=== COUNCIL VOTES ===")
    for vote in debate_result.votes:
        print(f"[{vote.agent_name}] -> {vote.decision} (Confidence: {vote.confidence}%)")
        print(f"Reasoning: {vote.reasoning}\n")
        
    print(f"=== JUDGE RULING ===")
    print(f"Score: {debate_result.score}/100 -> {'APPROVED' if debate_result.approved else 'REJECTED'}")
    print(f"Synthesis: {debate_result.rejection_reason}\n")
    
    # 6. Execute if approved
    if debate_result.approved:
        logger.info("Building Order...")
        order_data = OrderBuilder.build_iron_condor(target_signal.symbol, target_signal.underlying_price)
        
        if order_data:
            logger.info(f"Prepared Iron Condor: {order_data['strikes']}")
            logger.info("Executing via Alpaca Trading API...")
            
            try:
                resp = client.place_mleg_order(
                    legs=order_data["legs"],
                    limit_price=max(MIN_CREDIT, 0.45),
                    qty=1
                )
                logger.success(f"Order filled! Alpaca ID: {resp.get('id')}")
                
                logger.info("Generating Social Media Post via AutoNarrator...")
                post = narrator.generate_entry_post(debate_result, order_data)
                print(f"\n[AUTO-NARRATOR] TWEET READY:\n{post}")
                
            except Exception as e:
                logger.error(f"Execution failed: {e}")
        else:
            logger.error("Failed to build option legs. Ensure market is open and options chain is active.")

    print("\n" + "="*70)
    print(" [ORACLE] DEMO SEQUENCE COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_demo()
