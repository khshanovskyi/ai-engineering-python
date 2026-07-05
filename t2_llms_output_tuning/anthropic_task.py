from commons.constants import ANTHROPIC_HAIKU_4_5
from t2_llms_output_tuning._clients.anthropic_client import AnthropicAIClient
from t2_llms_output_tuning._main import run


run(
    client=AnthropicAIClient(ANTHROPIC_HAIKU_4_5),
    print_request=True, # Switch to False if you do not want to see the request in console
    print_only_content=False, # Switch to True if you want to see only content from response

    max_tokens=16
)