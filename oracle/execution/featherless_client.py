"""
Featherless AI Client — LLM council agents via OpenAI-compatible API
"""
from openai import OpenAI
from loguru import logger
from oracle.config.settings import FEATHERLESS_API_KEY, FEATHERLESS_MODEL, FEATHERLESS_BASE_URL


class FeatherlessClient:
    """OpenAI-compatible client pointing to Featherless AI."""

    def __init__(self):
        self.client = OpenAI(
            api_key=FEATHERLESS_API_KEY,
            base_url=FEATHERLESS_BASE_URL,
        )
        self.model = FEATHERLESS_MODEL
        logger.info(f"✅ Featherless AI client initialized ({self.model})")

    def chat(self, system_prompt: str, user_message: str,
             temperature: float = 0.3, max_tokens: int = 512) -> str:
        """Single completion call — returns assistant content string."""
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_message},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Featherless API error: {e} — using fallback")
            return "NEUTRAL: Unable to reach AI model. Defaulting to no action."


# Singleton
_fl_client = None


def get_featherless() -> FeatherlessClient:
    global _fl_client
    if _fl_client is None:
        _fl_client = FeatherlessClient()
    return _fl_client
