from abc import ABC

from t1_llm_api.base_client import AIClient


class BaseOpenAIClient(AIClient, ABC):
    """
    Abstract base class for OpenAI API clients.

    This class extends AIClient and adds OpenAI-specific initialization,
    particularly formatting the API key as a Bearer token for authorization.

    Attributes:
        Inherits all attributes from AIClient.
    """

    def __init__(self, base_url: str, model_name: str, system_prompt: str, api_key: str):
        """
        Initialize the OpenAI client with Bearer token authentication.

        Args:
            base_url (str): The OpenAI API base URL (e.g. 'https://api.openai.com/v1').
            model_name (str): The OpenAI model identifier (e.g., 'gpt-5').
            system_prompt (str): The system-level instruction for the model.
            api_key (str): The raw OpenAI API key (will be prefixed with 'Bearer ').

        Raises:
            ValueError: If api_key is None, empty, or contains only whitespace.
        """
        #TODO:
        # - validate api_key: raise ValueError if it is None, empty, or whitespace-only
        # - call super().__init__(...) forwarding base_url, model_name, system_prompt, and the
        #   api_key formatted as a Bearer header value ("Bearer {api_key}") so the custom client
        #   can drop self._api_key straight into the Authorization header
        raise NotImplementedError()