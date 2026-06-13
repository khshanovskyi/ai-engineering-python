import json
import aiohttp
import requests

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.base_client import AIClient


class CustomAnthropicAIClient(AIClient):

    def response(self, messages: list[Message], **kwargs) -> Message:
        url = f"{self._base_url}/v1/messages"
        headers = {
            "x-api-key": self._api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        request_data = {
            "model": self._model_name,
            "system": self._system_prompt,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "messages": [message.to_dict() for message in messages]
        }

        response = requests.post(url=url, headers=headers, json=request_data)

        if response.status_code == 200:
            data = response.json()
            content_blocks = data.get("content", [])
            if content_blocks:
                content = "".join(block.get("text", "") for block in content_blocks if block.get("type") == "text")
                print(content)
                return Message(Role.ASSISTANT, content)
            raise ValueError("No content blocks present in the response")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        url = f"{self._base_url}/v1/messages"
        headers = {
            "x-api-key": self._api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        request_data = {
            "model": self._model_name,
            "system": self._system_prompt,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "stream": True,
            "messages": [msg.to_dict() for msg in messages]
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
                            event_type = parsed_data.get("type")

                            if event_type == "content_block_delta":
                                delta = parsed_data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    text_content = delta.get("text", "")
                                    if text_content:
                                        print(text_content, end='')
                                        contents.append(text_content)
                            elif event_type == "message_stop":
                                break
                else:
                    error_text = await response.text()
                    print(f"{response.status} {error_text}")

                print()
                return Message(role=Role.ASSISTANT, content=''.join(contents))

