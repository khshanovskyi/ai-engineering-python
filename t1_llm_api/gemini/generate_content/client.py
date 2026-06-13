from google import genai
from google.genai import types

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.gemini.base import BaseGeminiClient


class GeminiGenerateContentAIClient(BaseGeminiClient):

    def __init__(self, base_url: str, model_name: str, api_key: str, system_prompt: str):
        super().__init__(base_url, model_name, api_key, system_prompt)
        #TODO:
        # https://ai.google.dev/api/generate-content
        # - create the google-genai SDK client on self._client, pointing it at base_url via
        #   types.HttpOptions: genai.Client(api_key=api_key, http_options=types.HttpOptions(base_url=base_url))

    def _to_gemini_contents(self, messages: list[Message]) -> list[types.Content]:
        #TODO:
        # - map each Message to a types.Content with role=self._to_gemini_role(msg.role)
        #   (assistant -> "model") and parts=[types.Part(text=msg.content)]
        # - return the list of contents
        raise NotImplementedError()

    def response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - call self._client.models.generate_content with model, contents=self._to_gemini_contents(messages),
        #   and config=types.GenerateContentConfig(system_instruction=self._system_prompt,
        #   max_output_tokens=kwargs.get("max_tokens", 1024))
        # - read response.text, print it
        # - return Message(Role.ASSISTANT, content)
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - await self._client.aio.models.generate_content_stream(...) (same model/contents/config)
        #   and async-iterate the result
        # - when chunk.text is truthy, print it (end='') and accumulate it
        # - print() a newline, return Message(Role.ASSISTANT, joined content)
        raise NotImplementedError()
