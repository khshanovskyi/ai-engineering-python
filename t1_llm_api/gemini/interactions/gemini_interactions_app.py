import asyncio

from t1_llm_api.base_app import start
from commons.constants import GEMINI_BASE_URL, GEMINI_API_KEY, DEFAULT_SYSTEM_PROMPT, GEMINI_3_FLASH
from t1_llm_api.gemini.interactions.client import GeminiInteractionsAIClient
from t1_llm_api.gemini.interactions.custom_client import CustomGeminiInteractionsAIClient

gemini_client = GeminiInteractionsAIClient(
    base_url=GEMINI_BASE_URL,
    model_name=GEMINI_3_FLASH,
    api_key=GEMINI_API_KEY,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)
gemini_custom_client = CustomGeminiInteractionsAIClient(
    base_url=GEMINI_BASE_URL,
    model_name=GEMINI_3_FLASH,
    api_key=GEMINI_API_KEY,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)

asyncio.run(
    start(True, gemini_client)
)