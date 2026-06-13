import asyncio

from t1_llm_api.anthropic.client import AnthropicAIClient
from t1_llm_api.anthropic.custom_client import CustomAnthropicAIClient
from t1_llm_api.base_app import start
from commons.constants import ANTHROPIC_BASE_URL, ANTHROPIC_API_KEY, DEFAULT_SYSTEM_PROMPT, ANTHROPIC_HAIKU_4_5

anthropic_client = AnthropicAIClient(
    base_url=ANTHROPIC_BASE_URL,
    model_name=ANTHROPIC_HAIKU_4_5,
    api_key=ANTHROPIC_API_KEY,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)
anthropic_custom_client = CustomAnthropicAIClient(
    base_url=ANTHROPIC_BASE_URL,
    model_name=ANTHROPIC_HAIKU_4_5,
    api_key=ANTHROPIC_API_KEY,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)

asyncio.run(
    start(True, anthropic_custom_client)
)
