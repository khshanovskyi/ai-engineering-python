import asyncio

from t1_llm_api.base_app import start
from commons.constants import OPENAI_BASE_URL, OPENAI_API_KEY, DEFAULT_SYSTEM_PROMPT, GPT_5_4_MINI
from t1_llm_api.openai.responses.client import OpenAIResponsesClient
from t1_llm_api.openai.responses.custom_client import CustomOpenAIResponsesClient

openai_client = OpenAIResponsesClient(
    base_url=OPENAI_BASE_URL,
    model_name=GPT_5_4_MINI,
    api_key=OPENAI_API_KEY,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)
openai_custom_client = CustomOpenAIResponsesClient(
    base_url=OPENAI_BASE_URL,
    model_name=GPT_5_4_MINI,
    api_key=OPENAI_API_KEY,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)

asyncio.run(
    start(True, openai_client)
)
