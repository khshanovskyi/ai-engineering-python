import json
import aiohttp
import requests

from t1_llm_api._models.message import Message
from t1_llm_api._models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class CustomOpenAIResponsesClient(BaseOpenAIClient):

    def response(self, messages: list[Message], **kwargs) -> Message:
        url = f"{self._base_url}/responses"
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json"
        }

        input_messages = [message.to_dict() for message in messages]

        request_data = {
            "model": self._model_name,
            "instructions": self._system_prompt,
            "input": input_messages
        }

        response = requests.post(url=url, headers=headers, json=request_data)

        if response.status_code == 200:
            data = response.json()
            content = self._extract_output_text(data)
            print(content)
            return Message(Role.ASSISTANT, content)
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        url = f"{self._base_url}/responses"
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json"
        }

        input_messages = [message.to_dict() for message in messages]

        request_data = {
            "model": self._model_name,
            "instructions": self._system_prompt,
            "input": input_messages,
            "stream": True
        }

        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=request_data) as response:
                if response.status == 200:
                    event_type = None
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()

                        if line_str.startswith("event: "):
                            event_type = line_str[7:].strip()
                        elif line_str.startswith("data: ") and event_type == "response.output_text.delta":
                            data = json.loads(line_str[6:])
                            delta = data.get("delta", "")
                            if delta:
                                print(delta, end='')
                                contents.append(delta)
                        elif line_str == "":
                            event_type = None
                else:
                    error_text = await response.text()
                    print(f"{response.status} {error_text}")

        print()
        return Message(role=Role.ASSISTANT, content=''.join(contents))

    @staticmethod
    def _extract_output_text(data: dict) -> str:
        output = data.get("output", [])
        for item in output:
            if item.get("type") == "message":
                for content_part in item.get("content", []):
                    if content_part.get("type") == "output_text":
                        return content_part.get("text", "")
        raise ValueError("No output text found in the response")