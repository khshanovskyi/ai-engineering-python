import json
import aiohttp
import requests

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class CustomOpenAIResponsesClient(BaseOpenAIClient):

    def response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # https://developers.openai.com/api/reference/resources/responses/methods/create
        # - set Authorization (self._api_key is already "Bearer {key}") and Content-Type headers
        # - build the request body: model, instructions (self._system_prompt), input ([m.to_dict() ...])
        # - POST with requests to "{self._base_url}/responses"
        # - on 200: extract the text via _extract_output_text, print it, return Message(Role.ASSISTANT, content)
        # - on non-200: raise with the status code and response text
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - same url + headers; add "stream": True to the request body
        # - open an aiohttp ClientSession and POST
        # - on 200: track the current event type across lines. A "event: <name>" line sets it;
        #   a "data: {...}" line is parsed only when the event is "response.output_text.delta"
        #   (read its delta, print + accumulate); a blank line resets the event type
        # - on non-200: read and print the error text
        # - print() a newline, return Message(Role.ASSISTANT, joined content)
        raise NotImplementedError()

    @staticmethod
    def _extract_output_text(data: dict) -> str:
        #TODO:
        # - walk data["output"]; find the item with type == "message"
        # - within its content, return the text of the part with type == "output_text"
        # - raise ValueError if no output text is found
        raise NotImplementedError()
