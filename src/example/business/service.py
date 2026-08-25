from typing import Any
from example.api.api_client import ApiClient


class UserService:
    """Business layer. Reusable by MCP, batch jobs, REST endpoints, tests, etc."""

    def __init__(self, api: ApiClient):
        self.api = api

    def get_user(self, user_id: int) -> dict[str, Any]:
        if user_id <= 0:
            raise ValueError("user_id must be greater than zero")

        user = self.api.get_user(user_id)
        return self._normalize_user(user)

    def list_users(self) -> list[dict[str, Any]]:
        users = self.api.list_users()
        return [self._normalize_user(user) for user in users]

    def create_user(self, name: str, email: str) -> dict[str, Any]:
        name = name.strip()
        email = email.strip().lower()

        if not name:
            raise ValueError("name is required")
        if "@" not in email:
            raise ValueError("email is invalid")

        user = self.api.create_user(name, email)
        return self._normalize_user(user)

    def update_user(
        self,
        user_id: int,
        name: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        if user_id <= 0:
            raise ValueError("user_id must be greater than zero")
        if name is None and email is None:
            raise ValueError("at least one field must be supplied")

        if name is not None:
            name = name.strip()
            if not name:
                raise ValueError("name cannot be empty")

        if email is not None:
            email = email.strip().lower()
            if "@" not in email:
                raise ValueError("email is invalid")

        user = self.api.update_user(user_id, name, email)
        return self._normalize_user(user)

    def delete_user(self, user_id: int) -> dict[str, Any]:
        if user_id <= 0:
            raise ValueError("user_id must be greater than zero")

        deleted = self.api.delete_user(user_id)
        return {"user_id": user_id, "deleted": deleted}

    @staticmethod
    def _normalize_user(user: dict[str, Any]) -> dict[str, Any]:
        """Example of business-level output shaping."""
        return {
            "id": user.get("id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "username": user.get("username"),
        }
