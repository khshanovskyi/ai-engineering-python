from google import genai
from google.genai import types

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.gemini.base import BaseGeminiClient


class GeminiInteractionsAIClient(BaseGeminiClient):

    def __init__(self, base_url: str, model_name: str, api_key: str, system_prompt: str):
        super().__init__(base_url, model_name, api_key, system_prompt)
        #TODO:
        # https://ai.google.dev/api/interactions-api
        # - create the google-genai SDK client on self._client, pointing it at base_url via
        #   types.HttpOptions: genai.Client(api_key=api_key, http_options=types.HttpOptions(base_url=base_url))

    def _to_input(self, messages: list[Message]) -> list[dict]:
        #TODO:
        # - map each Message to an Interactions "step": type "model_output" for Role.ASSISTANT,
        #   else "user_input"; content=[{"type": "text", "text": msg.content}]
        # - return the list of steps
        raise NotImplementedError()

    def response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - call self._client.interactions.create with model, input=self._to_input(messages),
        #   system_instruction=self._system_prompt, generation_config={"max_output_tokens": ...}
        # - read interaction.output_text, print it
        # - return Message(Role.ASSISTANT, content)
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - call self._client.aio.interactions.create(..., stream=True) and await it
        # - async-iterate events; when event.event_type == "step.delta" and event.delta.type == "text",
        #   print event.delta.text (end='') and accumulate it
        # - print() a newline, return Message(Role.ASSISTANT, joined content)
        raise NotImplementedError()
