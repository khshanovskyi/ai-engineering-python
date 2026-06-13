import asyncio

from commons.constants import DEFAULT_SYSTEM_PROMPT
from t1_llm_api.anthropic.client import AnthropicAIClient
from t1_llm_api.base_app import start
from t1_llm_api.openai.chat.completions.client import OpenAIChatCompletionsClient
from t1_llm_api.openai.responses.client import OpenAIResponsesClient

LLAMA_HOST = "http://localhost:11434"
LLAMA_OPENAI_BASE_URL = f"{LLAMA_HOST}/v1"
LLAMA_MODEL = "llama3.2:1b"
LOCAL_API_KEY = "ollama"

chat_completions_client = OpenAIChatCompletionsClient(
    base_url=LLAMA_OPENAI_BASE_URL,
    model_name=LLAMA_MODEL,
    api_key=LOCAL_API_KEY,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)

responses_client = OpenAIResponsesClient(
    base_url=LLAMA_OPENAI_BASE_URL,
    model_name=LLAMA_MODEL,
    api_key=LOCAL_API_KEY,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)

anthropic_client = AnthropicAIClient(
    base_url=LLAMA_HOST,
    model_name=LLAMA_MODEL,
    api_key=LOCAL_API_KEY,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)

asyncio.run(
    start(True, anthropic_client)
)
