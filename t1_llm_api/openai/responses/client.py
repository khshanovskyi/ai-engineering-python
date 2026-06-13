from openai import OpenAI, AsyncOpenAI

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class OpenAIResponsesClient(BaseOpenAIClient):

    def __init__(self, base_url: str, model_name: str, system_prompt: str, api_key: str):
        super().__init__(base_url, model_name, system_prompt, api_key)
        #TODO:
        # https://developers.openai.com/api/reference/resources/responses/methods/create
        # - create the OpenAI SDK clients with the RAW api_key and base_url, storing them on
        #   self._client (OpenAI(...)) and self._async_client (AsyncOpenAI(...))

    def response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - build input as [message.to_dict() for message in messages] (no inlined system message)
        # - call self._client.responses.create(model=..., instructions=self._system_prompt, input=...)
        # - read response.output_text, print it
        # - return Message(Role.ASSISTANT, content)
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - build the same input list
        # - open the streaming context manager:
        #   `async with self._async_client.responses.stream(model=..., instructions=..., input=...) as stream`
        # - async-iterate events; when event.type == "response.output_text.delta", print event.delta
        #   (end='') and accumulate it
        # - print() a newline, return Message(Role.ASSISTANT, joined content)
        raise NotImplementedError()
