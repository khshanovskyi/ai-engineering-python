from openai import OpenAI, AsyncOpenAI

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class OpenAIResponsesClient(BaseOpenAIClient):

    def __init__(self, base_url: str, model_name: str, system_prompt: str, api_key: str):
        super().__init__(base_url, model_name, system_prompt, api_key)
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def response(self, messages: list[Message], **kwargs) -> Message:
        input_messages = [message.to_dict() for message in messages]

        response = self._client.responses.create(
            model=self._model_name,
            instructions=self._system_prompt,
            input=input_messages
        )

        content = response.output_text
        print(content)
        return Message(role=Role.ASSISTANT, content=content)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        input_messages = [message.to_dict() for message in messages]

        contents = []

        async with self._async_client.responses.stream(
                model=self._model_name,
                instructions=self._system_prompt,
                input=input_messages
        ) as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    contents.append(event.delta)
                    print(event.delta, end='')

        print()
        return Message(role=Role.ASSISTANT, content="".join(contents))