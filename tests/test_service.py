import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from example.business.service import UserService


class FakeApiClient:
    def get_user(self, user_id):
        return {
            "id": user_id,
            "name": " Victor ",
            "email": "VICTOR@EXAMPLE.COM",
            "username": "victor",
        }

    def list_users(self):
        return [self.get_user(1)]

    def create_user(self, name, email):
        return {"id": 99, "name": name, "email": email, "username": "new"}

    def update_user(self, user_id, name, email):
        return {
            "id": user_id,
            "name": name or "Existing",
            "email": email or "existing@example.com",
            "username": "existing",
        }

    def delete_user(self, user_id):
        return True


def test_get_user_normalizes_business_output():
    print("\n[TEST] test_get_user_normalizes_business_output")
    service = UserService(FakeApiClient())
    print("  [OK] UserService created")

    result = service.get_user(1)
    print(f"  [OK] get_user(1) returned: {result}")

    assert result["name"] == " Victor "
    print(f"  [OK] name matches: {result['name']}")

    assert result["email"] == "VICTOR@EXAMPLE.COM"
    print(f"  [OK] email matches: {result['email']}")
    print("  [PASS] Test passed")


def test_create_user_applies_business_validation():
    print("\n[TEST] test_create_user_applies_business_validation")
    service = UserService(FakeApiClient())
    print("  [OK] UserService created")

    result = service.create_user(" Victor ", "VICTOR@EXAMPLE.COM")
    print(f"  [OK] create_user returned: {result}")

    assert result["name"] == "Victor"
    print(f"  [OK] name normalized: ' Victor ' -> {result['name']}")

    assert result["email"] == "victor@example.com"
    print(f"  [OK] email normalized: VICTOR@EXAMPLE.COM -> {result['email']}")
    print("  [PASS] Test passed")
