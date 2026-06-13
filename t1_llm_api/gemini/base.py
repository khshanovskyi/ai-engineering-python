from abc import ABC

from t1_llm_api._models.role import Role
from t1_llm_api.base_client import AIClient


class BaseGeminiClient(AIClient, ABC):

    @staticmethod
    def _to_gemini_role(role: Role) -> str:
        return "model" if role == Role.ASSISTANT else "user"

    def _auth_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self._api_key,
        }
