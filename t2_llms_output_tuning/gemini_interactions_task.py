from commons.constants import GEMINI_3_FLASH
from t2_llms_output_tuning._clients.gemini_interactions_client import GeminiInteractionsAIClient
from t2_llms_output_tuning._main import run


run(
    client=GeminiInteractionsAIClient(GEMINI_3_FLASH),
    print_request=True, # Switch to False if you do not want to see the request in console
    print_only_content=False, # Switch to True if you want to see only content from response

    generation_config={
        "max_output_tokens": 16,
        "thinking_level": "low",
    }
)
