import json

import requests

from commons.constants import GEMINI_API_KEY, GEMINI_API_REVISION, GEMINI_INTERACTIONS_ENDPOINT
from t2_llms_output_tuning._clients._base_client import AIClient
from t2_llms_output_tuning._models.message import Message
from t2_llms_output_tuning._models.role import Role


class GeminiInteractionsAIClient(AIClient):

    def __init__(self, model_name: str):
        super().__init__(
            endpoint=GEMINI_INTERACTIONS_ENDPOINT,
            model_name=model_name,
            api_key=GEMINI_API_KEY,
            api_key_header_name="x-goog-api-key"
        )

    def response(
            self,
            messages: list[Message],
            print_request: bool,
            print_only_content: bool,
            **kwargs
    ) -> Message:
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self._api_key,
            "Api-Revision": GEMINI_API_REVISION,
        }
        generation_config = kwargs.get("generation_config", {})
        generation_config.setdefault("max_output_tokens", 1024)
        request_data = {
            "model": self._model_name,
            "input": self._to_input(messages),
            "generation_config": generation_config,
        }

        if print_request:
            self._print_request(request_data, headers)

        response = requests.post(url=self._endpoint, headers=headers, json=request_data)

        if response.status_code == 200:
            data = response.json()
            content = self._extract_text(data)
            print("" + "=" * 50 + " RESPONSE " + "=" * 50)
            if print_only_content:
                print(content)
            else:
                print(json.dumps(data, indent=2, sort_keys=True))
            print("=" * 109)
            return Message(Role.ASSISTANT, content)
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    @staticmethod
    def _to_input(messages: list[Message]) -> list[dict]:
        steps = []
        for msg in messages:
            step_type = "model_output" if msg.role == Role.ASSISTANT else "user_input"
            steps.append({
                "type": step_type,
                "content": [{"type": "text", "text": msg.content}],
            })
        return steps

    @staticmethod
    def _extract_text(data: dict) -> str:
        texts = []
        for step in data.get("steps", []):
            if step.get("type") == "model_output":
                for block in step.get("content", []):
                    if block.get("type") == "text":
                        texts.append(block.get("text", ""))
        return "".join(texts)
