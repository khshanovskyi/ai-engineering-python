import json
import aiohttp
import requests

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class CustomOpenAIChatCompletionsClient(BaseOpenAIClient):

    def response(self, messages: list[Message], **kwargs) -> Message:
        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json"
        }

        messages_dicts = [
            {"role": "system", "content": self._system_prompt},
            *[message.to_dict() for message in messages]
        ]

        request_data = {
            "model": self._model_name,
            "messages": messages_dicts
        }

        response = requests.post(url=url, headers=headers, json=request_data)

        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content")
                print(content)
                return Message(Role.ASSISTANT, content)
            raise ValueError("No Choice has been present in the response")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json"
        }
        messages_dicts = [
            {"role": "system", "content": self._system_prompt},
            *[message.to_dict() for message in messages]
        ]
        request_data = {
            "model": self._model_name,
            "stream": True,
            "messages": messages_dicts
        }
        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=request_data) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data = line_str[6:].strip()
                            if data != "[DONE]":
                                content_snippet = self._get_content_snippet(data)
                                print(content_snippet, end='')
                                contents.append(content_snippet)
                            else:
                                print()
                else:
                    error_text = await response.text()
                    print(f"{response.status} {error_text}")
                return Message(role=Role.ASSISTANT, content=''.join(contents))

    def _get_content_snippet(self, data: str) -> str:
        data = json.loads(data)
        if choices := data.get("choices"):
            delta = choices[0].get("delta", {})
            return delta.get("content", '')
        return ''
