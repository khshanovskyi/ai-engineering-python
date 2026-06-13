import json
import aiohttp
import requests

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.gemini.base import BaseGeminiClient


class CustomGeminiGenerateContentAIClient(BaseGeminiClient):

    def _to_gemini_contents(self, messages: list[Message]) -> list[dict]:
        #TODO:
        # https://ai.google.dev/api/generate-content
        # - map each Message to a dict with role=self._to_gemini_role(msg.role) (assistant -> "model")
        #   and parts=[{"text": msg.content}]
        # - return the list of contents
        raise NotImplementedError()

    def response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - headers = self._auth_headers() (sets x-goog-api-key)
        # - build the request body: system_instruction as {"parts": [{"text": ...}]},
        #   contents=self._to_gemini_contents(messages), generationConfig={"maxOutputTokens": ...} (camelCase)
        # - POST with requests to "{self._base_url}/v1beta/models/{self._model_name}:generateContent"
        # - on 200: join the text of candidates[0].content.parts, print, return Message(Role.ASSISTANT, content);
        #   raise ValueError if there are no candidates
        # - on non-200: raise with the status code and response text
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - same headers + request body as response()
        # - POST with aiohttp to "{self._base_url}/v1beta/models/{self._model_name}:streamGenerateContent?alt=sse"
        #   (?alt=sse is required for streaming)
        # - on 200: async-iterate response.content lines; for lines starting with "data: ", strip the
        #   prefix and json.loads it, then walk candidates[0].content.parts and print + accumulate each part's text
        # - on non-200: read and print the error text
        # - print() a newline, return Message(Role.ASSISTANT, joined content)
        raise NotImplementedError()
