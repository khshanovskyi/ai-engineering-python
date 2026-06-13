from anthropic import Anthropic, AsyncAnthropic

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.base_client import AIClient


class AnthropicAIClient(AIClient):

    def __init__(self, base_url: str, model_name: str, api_key: str, system_prompt: str):
        super().__init__(base_url, model_name, api_key, system_prompt)
        #TODO:
        # Add Anthropic and AsyncAnthropic clients https://github.com/anthropics/anthropic-sdk-python?tab=readme-ov-file#usage
        # (In readme you can find samples with both of these clients)
        # Useful links with request/response samples:
        #   - https://platform.claude.com/docs/en/api/overview
        #   - https://platform.claude.com/docs/en/api/messages/create
        # - create the Anthropic SDK clients with api_key + base_url, storing them on
        #   self._client (Anthropic(...)) and self._async_client (AsyncAnthropic(...))

    def response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - call self._client.messages.create with system=self._system_prompt, max_tokens (required
        #   by Anthropic; default 1024), model=self._model_name, messages=[msg.to_dict() ...]
        # - response.content is a list of blocks; concatenate the .text of blocks where type == 'text'
        # - print the content, return Message(Role.ASSISTANT, content)
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - call self._async_client.messages.create with system, max_tokens, model, stream=True,
        #   messages=[msg.to_dict() ...] and await it
        # - async-iterate the stream; when chunk.type == "content_block_delta" and the chunk has
        #   delta.text, print it (end='') and accumulate it (guard with hasattr)
        # - print() a newline, return Message(Role.ASSISTANT, joined content)
        raise NotImplementedError()
