import json
import aiohttp
import requests

from commons.constants import GEMINI_API_REVISION
from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.gemini.base import BaseGeminiClient


class CustomGeminiInteractionsAIClient(BaseGeminiClient):

    def _to_input(self, messages: list[Message]) -> list[dict]:
        #TODO:
        # https://ai.google.dev/api/interactions-api
        # - map each Message to an Interactions "step": type "model_output" for Role.ASSISTANT,
        #   else "user_input"; content=[{"type": "text", "text": msg.content}]
        # - return the list of steps
        raise NotImplementedError()

    def _headers(self) -> dict:
        #TODO:
        # - return self._auth_headers() (from BaseGeminiClient: sets x-goog-api-key) extended with
        #   the "Api-Revision" header set to GEMINI_API_REVISION
        raise NotImplementedError()

    def _request_body(self, messages: list[Message], stream: bool, **kwargs) -> dict:
        #TODO:
        # - build the body: model, input=self._to_input(messages), system_instruction,
        #   generation_config={"max_output_tokens": kwargs.get("max_tokens", 1024)}
        # - add "stream": True only when stream is True
        # - return the body
        raise NotImplementedError()

    @staticmethod
    def _extract_text(interaction: dict) -> str:
        #TODO:
        # - walk interaction["steps"]; for steps with type == "model_output", collect the .text of
        #   content blocks where type == "text"
        # - return the joined text
        raise NotImplementedError()

    def response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - POST with requests to "{self._base_url}/v1beta/interactions" using _headers() and
        #   _request_body(messages, stream=False, **kwargs)
        # - on 200: extract text via _extract_text(response.json()), print, return Message(Role.ASSISTANT, content)
        # - on non-200: raise with the status code and response text
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - POST with aiohttp to "{self._base_url}/v1beta/interactions?alt=sse" (?alt=sse is required
        #   for streaming) using _headers() and _request_body(messages, stream=True, **kwargs)
        # - on 200: async-iterate response.content lines; for lines starting with "data: ", strip the
        #   prefix, skip empty payloads and "[DONE]"; json.loads the rest, and when event_type ==
        #   "step.delta" with delta.type == "text", print + accumulate delta.text
        # - on non-200: read and print the error text
        # - print() a newline, return Message(Role.ASSISTANT, joined content)
        raise NotImplementedError()
