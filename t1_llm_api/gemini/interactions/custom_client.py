import json
import aiohttp
import requests

from commons.constants import GEMINI_API_REVISION
from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.gemini.base import BaseGeminiClient


class CustomGeminiInteractionsAIClient(BaseGeminiClient):

    def _to_input(self, messages: list[Message]) -> list[dict]:
        steps = []
        for msg in messages:
            step_type = "model_output" if msg.role == Role.ASSISTANT else "user_input"
            steps.append({
                "type": step_type,
                "content": [{"type": "text", "text": msg.content}],
            })
        return steps

    def _headers(self) -> dict:
        return {
            **self._auth_headers(),
            "Api-Revision": GEMINI_API_REVISION,
        }

    def _request_body(self, messages: list[Message], stream: bool, **kwargs) -> dict:
        body = {
            "model": self._model_name,
            "input": self._to_input(messages),
            "system_instruction": self._system_prompt,
            "generation_config": {
                "max_output_tokens": kwargs.get("max_tokens", 1024)
            },
        }
        if stream:
            body["stream"] = True
        return body

    @staticmethod
    def _extract_text(interaction: dict) -> str:
        texts = []
        for step in interaction.get("steps", []):
            if step.get("type") == "model_output":
                for block in step.get("content", []):
                    if block.get("type") == "text":
                        texts.append(block.get("text", ""))
        return "".join(texts)

    def response(self, messages: list[Message], **kwargs) -> Message:
        url = f"{self._base_url}/v1beta/interactions"
        response = requests.post(
            url=url,
            headers=self._headers(),
            json=self._request_body(messages, stream=False, **kwargs),
        )

        if response.status_code == 200:
            content = self._extract_text(response.json())
            print(content)
            return Message(Role.ASSISTANT, content)
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        url = f"{self._base_url}/v1beta/interactions?alt=sse"
        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=url,
                    headers=self._headers(),
                    json=self._request_body(messages, stream=True, **kwargs),
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data = line_str[6:].strip()
                            if not data or data == "[DONE]":
                                continue
                            event = json.loads(data)
                            if event.get("event_type") == "step.delta":
                                delta = event.get("delta", {})
                                if delta.get("type") == "text":
                                    text_content = delta.get("text", "")
                                    if text_content:
                                        print(text_content, end='')
                                        contents.append(text_content)
                else:
                    error_text = await response.text()
                    print(f"{response.status} {error_text}")

                print()
                return Message(role=Role.ASSISTANT, content=''.join(contents))
