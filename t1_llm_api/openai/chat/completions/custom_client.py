import json
import aiohttp
import requests

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class CustomOpenAIChatCompletionsClient(BaseOpenAIClient):

    def response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create
        # - set Authorization (self._api_key is already "Bearer {key}") and Content-Type headers
        # - build the messages payload: system prompt as a message + each message.to_dict()
        # - POST with requests to "{self._base_url}/chat/completions" (base_url ends in /v1)
        # - on 200: read choices[0].message.content, print it, return Message(Role.ASSISTANT, content);
        #   if there are no choices, raise ValueError
        # - on non-200: raise with the status code and response text
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - same url + headers; add "stream": True to the request body
        # - open an aiohttp ClientSession and POST
        # - on 200: async-iterate response.content lines; for lines starting with "data: ",
        #   strip the prefix; if the payload is "[DONE]" print a newline, else pass it to
        #   _get_content_snippet, print the snippet (end='') and accumulate it
        # - on non-200: read and print the error text
        # - return Message(Role.ASSISTANT, joined content)
        raise NotImplementedError()

    def _get_content_snippet(self, data: str) -> str:
        #TODO:
        # - json.loads the SSE data chunk
        # - return choices[0].delta.content if present, else '' (use .get defensively)
        raise NotImplementedError()
