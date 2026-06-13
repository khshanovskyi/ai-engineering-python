from google import genai
from google.genai import types

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.gemini.base import BaseGeminiClient


class GeminiInteractionsAIClient(BaseGeminiClient):

    def __init__(self, base_url: str, model_name: str, api_key: str, system_prompt: str):
        super().__init__(base_url, model_name, api_key, system_prompt)
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(base_url=base_url),
        )

    def _to_input(self, messages: list[Message]) -> list[dict]:
        steps = []
        for msg in messages:
            step_type = "model_output" if msg.role == Role.ASSISTANT else "user_input"
            steps.append({
                "type": step_type,
                "content": [{"type": "text", "text": msg.content}],
            })
        return steps

    def response(self, messages: list[Message], **kwargs) -> Message:
        interaction = self._client.interactions.create(
            model=self._model_name,
            input=self._to_input(messages),
            system_instruction=self._system_prompt,
            generation_config={"max_output_tokens": kwargs.get("max_tokens", 1024)},
        )

        content = interaction.output_text
        print(content)
        return Message(role=Role.ASSISTANT, content=content)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        content = []

        stream = await self._client.aio.interactions.create(
            model=self._model_name,
            input=self._to_input(messages),
            system_instruction=self._system_prompt,
            generation_config={"max_output_tokens": kwargs.get("max_tokens", 1024)},
            stream=True,
        )
        async for event in stream:
            if event.event_type == "step.delta" and event.delta.type == "text":
                content.append(event.delta.text)
                print(event.delta.text, end='')

        print()
        return Message(role=Role.ASSISTANT, content="".join(content))
