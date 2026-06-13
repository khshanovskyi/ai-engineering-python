from google import genai
from google.genai import types

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.gemini.base import BaseGeminiClient


class GeminiGenerateContentAIClient(BaseGeminiClient):

    def __init__(self, base_url: str, model_name: str, api_key: str, system_prompt: str):
        super().__init__(base_url, model_name, api_key, system_prompt)
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(base_url=base_url),
        )

    def _to_gemini_contents(self, messages: list[Message]) -> list[types.Content]:
        contents = []
        for msg in messages:
            contents.append(
                types.Content(
                    role=self._to_gemini_role(msg.role),
                    parts=[types.Part(text=msg.content)]
                )
            )
        return contents

    def response(self, messages: list[Message], **kwargs) -> Message:
        print(messages)
        response = self._client.models.generate_content(
            model=self._model_name,
            contents=self._to_gemini_contents(messages),
            config=types.GenerateContentConfig(
                system_instruction=self._system_prompt,
                max_output_tokens=kwargs.get("max_tokens", 1024),
            ),
        )

        content = response.text
        print(content)
        return Message(role=Role.ASSISTANT, content=content)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        content = []

        async for chunk in await self._client.aio.models.generate_content_stream(
                model=self._model_name,
                contents=self._to_gemini_contents(messages),
                config=types.GenerateContentConfig(
                    system_instruction=self._system_prompt,
                    max_output_tokens=kwargs.get("max_tokens", 1024),
                ),
        ):
            if chunk.text:
                content.append(chunk.text)
                print(chunk.text, end='')

        print()
        return Message(role=Role.ASSISTANT, content="".join(content))