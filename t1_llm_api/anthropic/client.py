from anthropic import Anthropic, AsyncAnthropic

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.base_client import AIClient


class AnthropicAIClient(AIClient):

    def __init__(self, base_url: str, model_name: str, api_key: str, system_prompt: str):
        super().__init__(base_url, model_name, api_key, system_prompt)
        self._client = Anthropic(api_key=api_key, base_url=base_url)
        self._async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)

    def response(self, messages: list[Message], **kwargs) -> Message:
        response = self._client.messages.create(
            system=self._system_prompt,
            max_tokens=1024,
            model=self._model_name,
            messages=[msg.to_dict() for msg in messages]
        )

        content = ""
        for block in response.content:
            if block.type == 'text':
                content += block.text

        print(content)
        return Message(role=Role.ASSISTANT, content=content)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        content = []

        stream = await self._async_client.messages.create(
            system=self._system_prompt,
            max_tokens=1024,
            model=self._model_name,
            stream=True,
            messages=[msg.to_dict() for msg in messages]
        )

        async for chunk in stream:
            if chunk.type == "content_block_delta":
                if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                    delta_content = chunk.delta.text
                    content.append(delta_content)
                    print(delta_content, end='')

        print()
        return Message(role=Role.ASSISTANT, content="".join(content))
