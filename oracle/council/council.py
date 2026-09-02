"""
ORACLE Contrarian Council
A multi-agent debate system that evaluates trading signals.
"""
from typing import List, Dict, Any
from pydantic import BaseModel
from loguru import logger
import json
import re

from oracle.signals.base_scanner import Signal
from oracle.execution.featherless_client import get_featherless


class AgentVote(BaseModel):
    agent_name: str
    decision: str     # "APPROVE" or "REJECT"
    confidence: float # 0-100
    reasoning: str


class DebateResult(BaseModel):
    signal: Signal
    votes: List[AgentVote]
    score: float           # 0-100 overall score
    approved: bool
    rejection_reason: str
    suggested_sizing_pct: float # e.g. 1.0 = 100% of standard risk


class Council:
    """Orchestrates the multi-agent debate for a given signal."""

    def __init__(self):
        self.llm = get_featherless()
        
    def _parse_llm_response(self, response: str, agent_name: str) -> AgentVote:
        """Parses the expected JSON-like format from the LLM."""
        try:
            # Try to extract JSON from markdown if present
            match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
            else:
                # Try raw parsing just in case it returned clean JSON
                data = json.loads(response)
                
            return AgentVote(
                agent_name=agent_name,
                decision=str(data.get("decision", "REJECT")).upper(),
                confidence=float(data.get("confidence", 0.0)),
                reasoning=str(data.get("reasoning", "Parse error"))
            )
        except Exception as e:
            logger.error(f"[Council] Failed to parse {agent_name} response: {e}\nResponse: {response}")
            # Safe default on failure
            return AgentVote(
                agent_name=agent_name,
                decision="REJECT",
                confidence=0.0,
                reasoning="Failed to parse LLM response. Defaulting to reject."
            )

    def ask_bull_agent(self, signal: Signal) -> AgentVote:
        """The Bull Agent tries to find reasons WHY the trade will work."""
        sys_prompt = """You are the BULL AGENT in a quantitative trading council. 
Your job is to look at a trade signal and argue FOR taking the trade. Highlight the bullish factors, the statistical edge, and why this is a good setup.
Output strictly in JSON format: {"decision": "APPROVE"|"REJECT", "confidence": 0-100, "reasoning": "your short argument"}"""
        
        user_msg = f"Signal: {signal.symbol} | Strategy: {signal.recommended_strategy} | Direction: {signal.direction} | Metadata: {signal.metadata}"
        resp = self.llm.chat(sys_prompt, user_msg)
        return self._parse_llm_response(resp, "Bull Agent")

    def ask_bear_agent(self, signal: Signal) -> AgentVote:
        """The Bear Agent tries to destroy the thesis and find reasons to reject."""
        sys_prompt = """You are the BEAR AGENT in a quantitative trading council. 
Your job is to aggressively argue AGAINST taking the trade. Find flaws in the thesis, highlight macro risks, sector rotation risks, or mean reversion traps. You are pessimistic.
Output strictly in JSON format: {"decision": "APPROVE"|"REJECT", "confidence": 0-100, "reasoning": "your short argument"}"""
        
        user_msg = f"Signal: {signal.symbol} | Strategy: {signal.recommended_strategy} | Direction: {signal.direction} | Metadata: {signal.metadata}"
        resp = self.llm.chat(sys_prompt, user_msg)
        return self._parse_llm_response(resp, "Bear Agent")

    def ask_risk_agent(self, signal: Signal) -> AgentVote:
        """The Risk Agent only cares about downside and position sizing."""
        sys_prompt = """You are the RISK AGENT in a quantitative trading council. 
You do not care about upside. You only evaluate downside risk, correlation to the broader market, and whether the proposed strategy has defined risk. 
If the trade feels too risky, reject it. If the risk is definable and acceptable, approve it.
Output strictly in JSON format: {"decision": "APPROVE"|"REJECT", "confidence": 0-100, "reasoning": "your short argument"}"""
        
        user_msg = f"Signal: {signal.symbol} | Strategy: {signal.recommended_strategy} | Direction: {signal.direction} | Metadata: {signal.metadata}"
        resp = self.llm.chat(sys_prompt, user_msg)
        return self._parse_llm_response(resp, "Risk Agent")

    def ask_judge_agent(self, signal: Signal, votes: List[AgentVote]) -> dict:
        """The Judge synthesizes the debate and makes the final call."""
        sys_prompt = """You are the CHIEF JUDGE of a quantitative trading council. 
You will be provided with a trade signal and the arguments from the Bull, Bear, and Risk agents. 
Your job is to synthesize these arguments, score the trade from 0 to 100, and make a final APPROVE or REJECT decision. 
You must also suggest a sizing multiplier (0.1 to 1.0) based on conviction.
Output strictly in JSON format: {"final_decision": "APPROVE"|"REJECT", "score": 0-100, "sizing_multiplier": 0.1-1.0, "synthesis": "your final ruling"}"""
        
        debate_text = f"Signal: {signal.symbol} ({signal.recommended_strategy})\n\n"
        for v in votes:
            debate_text += f"{v.agent_name} ({v.decision}, conf {v.confidence}): {v.reasoning}\n"
            
        resp = self.llm.chat(sys_prompt, debate_text)
        
        try:
            match = re.search(r'```json\s*(\{.*?\})\s*```', resp, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
            else:
                data = json.loads(resp)
            return data
        except Exception as e:
            logger.error(f"[Council] Failed to parse Judge response: {e}")
            return {"final_decision": "REJECT", "score": 0, "sizing_multiplier": 0, "synthesis": "Parse error"}

    def debate(self, signal: Signal) -> DebateResult:
        """Run the full council debate for a signal."""
        logger.info(f"[Council] Convening debate for {signal.symbol} ({signal.recommended_strategy})...")
        
        # 1. Gather initial arguments (could be parallelized)
        bull = self.ask_bull_agent(signal)
        bear = self.ask_bear_agent(signal)
        risk = self.ask_risk_agent(signal)
        
        votes = [bull, bear, risk]
        
        # 2. Judge makes final ruling
        judge_data = self.ask_judge_agent(signal, votes)
        
        score = float(judge_data.get("score", 0))
        approved = judge_data.get("final_decision", "REJECT").upper() == "APPROVE"
        
        from oracle.config.settings import COUNCIL_APPROVAL_THRESHOLD
        
        # Hard override: if score is below threshold, force reject
        if score < COUNCIL_APPROVAL_THRESHOLD:
            approved = False
            
        result = DebateResult(
            signal=signal,
            votes=votes,
            score=score,
            approved=approved,
            rejection_reason=judge_data.get("synthesis", "") if not approved else "",
            suggested_sizing_pct=float(judge_data.get("sizing_multiplier", 1.0))
        )
        
        logger.info(f"[Council] Debate concluded for {signal.symbol}. Approved: {result.approved} | Score: {result.score}")
        return result
