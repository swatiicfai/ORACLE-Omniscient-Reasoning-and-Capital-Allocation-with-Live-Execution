"""
AutoNarrator Layer
Automatically generates social media posts (X/LinkedIn format) explaining the agent's decisions.
"""
from loguru import logger
import os

from oracle.council.council import DebateResult
from oracle.execution.featherless_client import get_featherless
from oracle.config.settings import NARRATOR_ENABLED, NARRATOR_OUTPUT_FILE

class AutoNarrator:
    """Translates trading actions into human-readable social media updates."""
    
    def __init__(self):
        self.llm = get_featherless()
        self.output_file = NARRATOR_OUTPUT_FILE
        
    def _save_post(self, post: str):
        if not NARRATOR_ENABLED:
            return
            
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write("\n" + "="*50 + "\n")
                f.write(post)
                f.write("\n" + "="*50 + "\n")
            logger.info(f"[Narrator] Saved new post to {self.output_file}")
        except Exception as e:
            logger.error(f"[Narrator] Failed to save post: {e}")

    def generate_entry_post(self, debate: DebateResult, execution_details: dict) -> str:
        """Generate a post for a successfully executed trade."""
        sys_prompt = """You are the public relations voice for ORACLE, an advanced autonomous AI trading agent.
Your agent just executed a trade after a rigorous multi-agent debate. 
Write an engaging, insightful social media post (Twitter/LinkedIn style) explaining the trade.
It must sound robotic but highly intelligent. Do not use emojis excessively. Use a confident tone.
Include the symbol, the strategy, the rationale, and the max risk.
Always end with: '🤖 Paper trading on Alpaca. Not financial advice. #AlpacaHackathon @AlpacaHQ @lablab.ai'"""

        context = f"""
Symbol: {debate.signal.symbol}
Strategy: {debate.signal.recommended_strategy}
Signal Trigger: {debate.signal.scanner_name} (Confidence: {debate.signal.confidence})
Council Score: {debate.score}/100
Bear Agent Warning: {next((v.reasoning for v in debate.votes if v.agent_name == 'Bear Agent'), 'None')}
Execution Details: {execution_details}
"""
        logger.info(f"[Narrator] Generating entry post for {debate.signal.symbol}...")
        post = self.llm.chat(sys_prompt, context, max_tokens=300)
        self._save_post(post)
        return post

    def generate_rejection_post(self, debate: DebateResult) -> str:
        """Generate a post explaining why a trade was rejected by the council."""
        sys_prompt = """You are the public relations voice for ORACLE, an advanced autonomous AI trading agent.
Your multi-agent council just REJECTED a trade signal. This shows discipline.
Write a short, engaging social media post explaining WHY the agent chose NOT to trade. 
Highlight the Bear Agent's or Risk Agent's warning.
Always end with: '🤖 Protecting capital first. #AlpacaHackathon @AlpacaHQ @lablab.ai'"""

        context = f"""
Symbol: {debate.signal.symbol}
Signal Trigger: {debate.signal.scanner_name}
Council Score: {debate.score}/100
Rejection Reason: {debate.rejection_reason}
Bear Agent argued: {next((v.reasoning for v in debate.votes if v.agent_name == 'Bear Agent'), 'None')}
"""
        logger.info(f"[Narrator] Generating rejection post for {debate.signal.symbol}...")
        post = self.llm.chat(sys_prompt, context, max_tokens=250)
        self._save_post(post)
        return post

# Singleton
_narrator = None

def get_narrator() -> AutoNarrator:
    global _narrator
    if _narrator is None:
        _narrator = AutoNarrator()
    return _narrator
