from commons.constants import GEMINI_3_FLASH
from t2_llms_output_tuning._clients.gemini_interactions_client import GeminiInteractionsAIClient
from t2_llms_output_tuning._main import run

# All parameters below must be passed inside generation_config={...}
# NOTE: the Interactions API uses snake_case field names (generation_config, top_p, max_output_tokens),
#  unlike the Generate Content API's camelCase (generationConfig, topP, maxOutputTokens).

# TODO 1: temperature — controls randomness. Range: 0.0-2.0, default: 1.0
#  Lower = more deterministic, higher = more creative
#  Query: "Give me a name for a coffee shop"
#  Try: "temperature": 0.0 vs "temperature": 2.0, compare outputs

# TODO 2: top_p — nucleus sampling, keeps tokens within cumulative probability. Range: 0.0-1.0, default: 0.95
#  Lower = fewer token choices, more focused output
#  Query: "List 5 alternative uses for a paperclip"
#  Try: "top_p": 0.1 vs "top_p": 0.95

# TODO 3: max_output_tokens — max number of tokens in the response. Default: 1024 (set in gemini_interactions_client.py)
#  Query: "Explain quantum computing"
#  Try: "max_output_tokens": 50 vs "max_output_tokens": 2048

# TODO 4: stop_sequences — list of strings; generation stops when one is produced
#  Query: "Count from 1 to 20"
#  Try: "stop_sequences": ["5"] — generation halts before "5" is emitted

# TODO 5: thinking_level — depth of extended thinking (chain-of-thought). Values: "minimal", "low", "medium", "high"
#  Model reasons step-by-step before answering; higher = more reasoning, slower/costlier
#  Query: "How many r's are in the word strawberry?"
#  Try: "thinking_level": "minimal" vs "thinking_level": "high"

# TODO 6: thinking_summaries — whether the response includes a summary of the model's thinking. Values: "auto", "none"
#  Query: "How many r's are in the word strawberry?"
#  Try: "thinking_summaries": "auto" vs "thinking_summaries": "none"

# TODO 7: seed — fixes the sampling seed for reproducible output. Integer
#  Same seed + same input + same params → (near-)identical output
#  Query: "Give me a name for a coffee shop"
#  Try: "seed": 42 across two runs and compare, then change temperature and observe

run(
    client=GeminiInteractionsAIClient(GEMINI_3_FLASH),
    print_request=True, # Switch to False if you do not want to see the request in console
    print_only_content=False, # Switch to True if you want to see only content from response


)
