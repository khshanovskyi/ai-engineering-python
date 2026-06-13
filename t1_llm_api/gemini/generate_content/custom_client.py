import json
import aiohttp
import requests

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.gemini.base import BaseGeminiClient


class CustomGeminiGenerateContentAIClient(BaseGeminiClient):

    def _to_gemini_contents(self, messages: list[Message]) -> list[dict]:
        contents = []
        for msg in messages:
            contents.append({
                "role": self._to_gemini_role(msg.role),
                "parts": [{"text": msg.content}]
            })
        return contents

    def response(self, messages: list[Message], **kwargs) -> Message:
        url = f"{self._base_url}/v1beta/models/{self._model_name}:generateContent"
        headers = self._auth_headers()

        request_data = {
            "system_instruction": {"parts": [{"text": self._system_prompt}]},
            "contents": self._to_gemini_contents(messages),
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 1024)
            }
        }

        response = requests.post(url=url, headers=headers, json=request_data)

        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                content = "".join(part.get("text", "") for part in parts)
                print(content)
                return Message(Role.ASSISTANT, content)
            raise ValueError("No candidates present in the response")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        url = f"{self._base_url}/v1beta/models/{self._model_name}:streamGenerateContent?alt=sse"
        headers = self._auth_headers()

        request_data = {
            "system_instruction": {"parts": [{"text": self._system_prompt}]},
            "contents": self._to_gemini_contents(messages),
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 1024)
            }
        }
        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=request_data) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data = line_str[6:].strip()
                            parsed_data = json.loads(data)
                            candidates = parsed_data.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for part in parts:
                                    text_content = part.get("text", "")
                                    if text_content:
                                        print(text_content, end='')
                                        contents.append(text_content)
                else:
                    error_text = await response.text()
                    print(f"{response.status} {error_text}")

                print()
                return Message(role=Role.ASSISTANT, content=''.join(contents))