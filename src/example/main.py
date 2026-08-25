from src.example.api.api_client import ApiClient
from src.example.business.service import UserService


def main() -> None:
    # The exact same business layer can be used without MCP.
    service = UserService(ApiClient())

    user = service.get_user(1)
    print("USER:", user)

    users = service.list_users()
    print("USERS:", len(users))


if __name__ == "__main__":
    main()
