from typing import Any
import httpx


class ApiClient:
    """HTTP-only client. No business decisions belong here."""

    def __init__(self, base_url: str = "https://jsonplaceholder.typicode.com"):
        self.base_url = base_url.rstrip("/")

    def get_user(self, user_id: int) -> dict[str, Any]:
        response = httpx.get(f"{self.base_url}/users/{user_id}", timeout=10)
        response.raise_for_status()
        return response.json()

    def list_users(self) -> list[dict[str, Any]]:
        response = httpx.get(f"{self.base_url}/users", timeout=10)
        response.raise_for_status()
        return response.json()

    def create_user(self, name: str, email: str) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/users",
            json={"name": name, "email": email},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def update_user(self, user_id: int, name: str | None, email: str | None) -> dict[str, Any]:
        payload = {}
        if name is not None:
            payload["name"] = name
        if email is not None:
            payload["email"] = email

        response = httpx.patch(
            f"{self.base_url}/users/{user_id}",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def delete_user(self, user_id: int) -> bool:
        response = httpx.delete(f"{self.base_url}/users/{user_id}", timeout=10)
        response.raise_for_status()
        return True
