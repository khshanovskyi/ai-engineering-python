from openai import OpenAI, AsyncOpenAI

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class OpenAIChatCompletionsClient(BaseOpenAIClient):

    def __init__(self, base_url: str, model_name: str, system_prompt: str, api_key: str):
        super().__init__(base_url, model_name, system_prompt, api_key)
        #TODO:
        # Add OpenAI and AsyncOpenAI clients https://github.com/openai/openai-python?tab=readme-ov-file#usage for
        # ChatCompletions API
        # https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create
        # - create the OpenAI SDK clients with the RAW api_key (the SDK adds "Bearer " itself)
        #   and base_url, storing them on self._client (OpenAI(...)) and
        #   self._async_client (AsyncOpenAI(...))

    def response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - build the messages payload: a {"role": "system", ...} message with self._system_prompt,
        #   followed by each message.to_dict()
        # - call self._client.chat.completions.create(model=self._model_name, messages=...)
        # - read response.choices[0].message.content, print it
        # - return Message(Role.ASSISTANT, content)
        raise NotImplementedError()

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        #TODO:
        # - build the same messages payload (system prompt + history)
        # - call self._async_client.chat.completions.create(..., stream=True) and await it
        # - async-iterate the stream; for each chunk read chunk.choices[0].delta.content
        #   (skip None), print it with end='' and accumulate it
        # - print() a newline, return Message(Role.ASSISTANT, joined content)
        raise NotImplementedError()
