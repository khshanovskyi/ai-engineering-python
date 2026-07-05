from dataclasses import dataclass
from typing import Any

from t1_llm_api._models.role import Role


@dataclass
class Message:
    role: Role
    content: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role.value,
            "content": self.content
        }
