import json
import aiohttp
import requests

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.base_client import AIClient


class CustomAnthropicAIClient(AIClient):

    def response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # https://platform.claude.com/docs/en/api/messages/create
        # - set headers: x-api-key (self._api_key is the RAW key here, no Bearer),
        #   Content-Type, and anthropic-version ("2023-06-01")
        # - build the request body: model, system (self._system_prompt),
        #   max_tokens (kwargs.get default 1024; required by Anthropic), messages=[m.to_dict() ...]
        # - POST with requests to "{self._base_url}/v1/messages" (base_url is the bare host)
        # - on 200: join the .text of content blocks where type == "text", print, return
        #   Message(Role.ASSISTANT, content); raise ValueError if there are no content blocks
        # - on non-200: raise with the status code and response text
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - same url + headers; add "stream": True to the request body
        # - open an aiohttp ClientSession and POST
        # - on 200: async-iterate response.content lines; for lines starting with "data: ",
        #   strip the prefix and json.loads it, then branch on the parsed "type":
        #     - "content_block_delta" with delta.type == "text_delta": print + accumulate delta.text
        #     - "message_stop": break
        # - on non-200: read and print the error text
        # - print() a newline, return Message(Role.ASSISTANT, joined content)
        raise NotImplementedError()

