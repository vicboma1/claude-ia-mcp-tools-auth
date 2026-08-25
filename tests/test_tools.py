"""Test suite for MCP server tools with corner cases."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from example.business.service import UserService


class FakeApiClient:
    """Mock API client for testing."""

    def __init__(self):
        self.users = {
            1: {
                "id": 1,
                "name": "Victor",
                "email": "victor@example.com",
                "username": "victor",
            },
            2: {
                "id": 2,
                "name": "John Doe",
                "email": "john@example.com",
                "username": "john",
            }
        }
        self.next_id = 3

    def get_user(self, user_id):
        print(f"    [API] get_user({user_id})")
        if user_id not in self.users:
            raise KeyError(f"User {user_id} not found")
        return self.users[user_id].copy()

    def list_users(self):
        print(f"    [API] list_users() -> {len(self.users)} users")
        return list(self.users.values())

    def create_user(self, name, email):
        print(f"    [API] create_user('{name}', '{email}')")
        user_id = self.next_id
        self.next_id += 1
        user = {
            "id": user_id,
            "name": name,
            "email": email,
            "username": name.lower().replace(" ", ""),
        }
        self.users[user_id] = user
        return user

    def update_user(self, user_id, name, email):
        print(f"    [API] update_user({user_id}, '{name}', '{email}')")
        if user_id not in self.users:
            raise KeyError(f"User {user_id} not found")
        if name:
            self.users[user_id]["name"] = name
        if email:
            self.users[user_id]["email"] = email
        return self.users[user_id].copy()

    def delete_user(self, user_id):
        print(f"    [API] delete_user({user_id})")
        if user_id not in self.users:
            raise KeyError(f"User {user_id} not found")
        del self.users[user_id]
        return True


# ============================================================================
# TEST SUITE: get_user
# ============================================================================

class TestGetUser:
    """Test cases for get_user tool."""

    def test_get_user_success(self):
        """Test retrieving an existing user."""
        print("\n[TEST] get_user - success case")
        client = FakeApiClient()
        service = UserService(client)

        result = service.get_user(1)
        print(f"  [OK] Result: {result}")

        assert result["id"] == 1
        assert result["name"] == "Victor"
        assert result["email"] == "victor@example.com"
        print("  [PASS] User retrieved successfully")

    def test_get_user_not_found(self):
        """Test retrieving a non-existent user."""
        print("\n[TEST] get_user - user not found")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(KeyError):
            print("  [ACTION] Attempting to get user 999")
            service.get_user(999)
        print("  [PASS] Correctly raised KeyError for non-existent user")

    def test_get_user_zero_id(self):
        """Test with user ID 0."""
        print("\n[TEST] get_user - corner case: zero ID")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to get user 0")
            service.get_user(0)
        print("  [PASS] Correctly raised ValueError for ID 0")

    def test_get_user_negative_id(self):
        """Test with negative user ID."""
        print("\n[TEST] get_user - corner case: negative ID")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to get user -1")
            service.get_user(-1)
        print("  [PASS] Correctly raised ValueError for negative ID")

    def test_get_user_large_id(self):
        """Test with very large user ID."""
        print("\n[TEST] get_user - corner case: large ID")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(KeyError):
            print("  [ACTION] Attempting to get user 999999999")
            service.get_user(999999999)
        print("  [PASS] Correctly raised KeyError for large ID")


# ============================================================================
# TEST SUITE: list_users
# ============================================================================

class TestListUsers:
    """Test cases for list_users tool."""

    def test_list_users_success(self):
        """Test listing all users."""
        print("\n[TEST] list_users - success case")
        client = FakeApiClient()
        service = UserService(client)

        result = service.list_users()
        print(f"  [OK] Result count: {len(result)}")

        assert len(result) == 2
        assert any(u["name"] == "Victor" for u in result)
        assert any(u["name"] == "John Doe" for u in result)
        print("  [PASS] All users listed successfully")

    def test_list_users_empty(self):
        """Test listing users when database is empty."""
        print("\n[TEST] list_users - empty database")
        client = FakeApiClient()
        client.users = {}  # Empty database
        service = UserService(client)

        result = service.list_users()
        print(f"  [OK] Result count: {len(result)}")

        assert result == []
        assert len(result) == 0
        print("  [PASS] Empty list returned for empty database")

    def test_list_users_contains_all_fields(self):
        """Test that each user has all required fields."""
        print("\n[TEST] list_users - verify user fields")
        client = FakeApiClient()
        service = UserService(client)

        result = service.list_users()
        required_fields = {"id", "name", "email", "username"}

        for user in result:
            print(f"  [CHECK] User {user['id']}: {user}")
            assert all(field in user for field in required_fields)
        print("  [PASS] All users have required fields")

    def test_list_users_count(self):
        """Test that list returns correct count."""
        print("\n[TEST] list_users - verify count")
        client = FakeApiClient()
        service = UserService(client)

        result = service.list_users()
        print(f"  [OK] Result count: {len(result)}")

        assert len(result) == 2
        print("  [PASS] Correct count returned")


# ============================================================================
# TEST SUITE: create_user
# ============================================================================

class TestCreateUser:
    """Test cases for create_user tool."""

    def test_create_user_success(self):
        """Test creating a new user."""
        print("\n[TEST] create_user - success case")
        client = FakeApiClient()
        service = UserService(client)

        result = service.create_user("Alice", "alice@example.com")
        print(f"  [OK] Result: {result}")

        assert result["name"] == "Alice"
        assert result["email"] == "alice@example.com"
        assert result["id"] == 3
        print("  [PASS] User created successfully")

    def test_create_user_normalizes_input(self):
        """Test that create_user normalizes input data."""
        print("\n[TEST] create_user - normalize input")
        client = FakeApiClient()
        service = UserService(client)

        result = service.create_user("  Bob  ", "BOB@EXAMPLE.COM")
        print(f"  [OK] Result: {result}")

        assert result["name"] == "Bob"
        assert result["email"] == "bob@example.com"
        print("  [PASS] Input normalized correctly")

    def test_create_user_empty_name(self):
        """Test creating user with empty name."""
        print("\n[TEST] create_user - corner case: empty name")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to create user with empty name")
            service.create_user("", "empty@example.com")
        print("  [PASS] Correctly raised ValueError for empty name")

    def test_create_user_empty_email(self):
        """Test creating user with empty email."""
        print("\n[TEST] create_user - corner case: empty email")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to create user with empty email")
            service.create_user("Charlie", "")
        print("  [PASS] Correctly raised ValueError for empty email")

    def test_create_user_invalid_email(self):
        """Test creating user with invalid email (no @)."""
        print("\n[TEST] create_user - corner case: invalid email")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to create user with email without @")
            service.create_user("Dave", "invalid-email")
        print("  [PASS] Correctly raised ValueError for invalid email")

    def test_create_user_special_characters(self):
        """Test creating user with special characters."""
        print("\n[TEST] create_user - corner case: special characters")
        client = FakeApiClient()
        service = UserService(client)

        result = service.create_user("José García", "jose+test@example.com")
        print(f"  [OK] Result: {result}")

        assert "José" in result["name"]
        assert "+" in result["email"]
        print("  [PASS] Special characters handled")

    def test_create_user_long_input(self):
        """Test creating user with very long name/email."""
        print("\n[TEST] create_user - corner case: long input")
        client = FakeApiClient()
        service = UserService(client)

        long_name = "A" * 1000
        long_email = "a" * 100 + "@example.com"

        result = service.create_user(long_name, long_email)
        print(f"  [OK] Result name length: {len(result['name'])}")

        assert len(result["name"]) == 1000
        assert len(result["email"]) > 100
        print("  [PASS] Long input accepted")

    def test_create_user_incremental_ids(self):
        """Test that created users get incremental IDs."""
        print("\n[TEST] create_user - incremental IDs")
        client = FakeApiClient()
        service = UserService(client)

        user1 = service.create_user("User1", "user1@example.com")
        user2 = service.create_user("User2", "user2@example.com")
        user3 = service.create_user("User3", "user3@example.com")

        print(f"  [OK] User1 ID: {user1['id']}, User2 ID: {user2['id']}, User3 ID: {user3['id']}")

        assert user1["id"] == 3
        assert user2["id"] == 4
        assert user3["id"] == 5
        print("  [PASS] IDs incremented correctly")


# ============================================================================
# TEST SUITE: update_user
# ============================================================================

class TestUpdateUser:
    """Test cases for update_user tool."""

    def test_update_user_name_only(self):
        """Test updating only the name."""
        print("\n[TEST] update_user - update name only")
        client = FakeApiClient()
        service = UserService(client)

        result = service.update_user(1, "Victor Updated", None)
        print(f"  [OK] Result: {result}")

        assert result["name"] == "Victor Updated"
        assert result["email"] == "victor@example.com"
        print("  [PASS] Name updated, email unchanged")

    def test_update_user_email_only(self):
        """Test updating only the email."""
        print("\n[TEST] update_user - update email only")
        client = FakeApiClient()
        service = UserService(client)

        result = service.update_user(1, None, "newemail@example.com")
        print(f"  [OK] Result: {result}")

        assert result["name"] == "Victor"
        assert result["email"] == "newemail@example.com"
        print("  [PASS] Email updated, name unchanged")

    def test_update_user_both(self):
        """Test updating both name and email."""
        print("\n[TEST] update_user - update both")
        client = FakeApiClient()
        service = UserService(client)

        result = service.update_user(1, "New Name", "newemail@example.com")
        print(f"  [OK] Result: {result}")

        assert result["name"] == "New Name"
        assert result["email"] == "newemail@example.com"
        print("  [PASS] Both fields updated")

    def test_update_user_not_found(self):
        """Test updating a non-existent user."""
        print("\n[TEST] update_user - user not found")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(KeyError):
            print("  [ACTION] Attempting to update user 999")
            service.update_user(999, "New Name", "new@example.com")
        print("  [PASS] Correctly raised KeyError")

    def test_update_user_empty_name(self):
        """Test updating with empty name (after strip)."""
        print("\n[TEST] update_user - corner case: empty name")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to update with empty name")
            service.update_user(1, "", "test@example.com")
        print("  [PASS] Correctly raised ValueError for empty name")

    def test_update_user_empty_email(self):
        """Test updating with empty email (after strip)."""
        print("\n[TEST] update_user - corner case: empty email")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to update with empty email")
            service.update_user(1, "Test", "")
        print("  [PASS] Correctly raised ValueError for empty email")

    def test_update_user_zero_id(self):
        """Test updating user with ID 0."""
        print("\n[TEST] update_user - corner case: zero ID")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to update user 0")
            service.update_user(0, "New", "new@example.com")
        print("  [PASS] Correctly raised ValueError")

    def test_update_user_negative_id(self):
        """Test updating user with negative ID."""
        print("\n[TEST] update_user - corner case: negative ID")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to update user -1")
            service.update_user(-1, "New", "new@example.com")
        print("  [PASS] Correctly raised ValueError")

    def test_update_user_no_fields(self):
        """Test updating user without providing any fields."""
        print("\n[TEST] update_user - corner case: no fields supplied")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to update with no fields")
            service.update_user(1, None, None)
        print("  [PASS] Correctly raised ValueError")


# ============================================================================
# TEST SUITE: delete_user
# ============================================================================

class TestDeleteUser:
    """Test cases for delete_user tool."""

    def test_delete_user_success(self):
        """Test deleting an existing user."""
        print("\n[TEST] delete_user - success case")
        client = FakeApiClient()
        service = UserService(client)

        print(f"  [OK] Users before delete: {len(client.users)}")
        result = service.delete_user(1)
        print(f"  [OK] Delete result: {result}")
        print(f"  [OK] Users after delete: {len(client.users)}")

        assert result["deleted"] is True
        assert result["user_id"] == 1
        assert 1 not in client.users
        print("  [PASS] User deleted successfully")

    def test_delete_user_not_found(self):
        """Test deleting a non-existent user."""
        print("\n[TEST] delete_user - user not found")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(KeyError):
            print("  [ACTION] Attempting to delete user 999")
            service.delete_user(999)
        print("  [PASS] Correctly raised KeyError")

    def test_delete_user_zero_id(self):
        """Test deleting user with ID 0."""
        print("\n[TEST] delete_user - corner case: zero ID")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to delete user 0")
            service.delete_user(0)
        print("  [PASS] Correctly raised ValueError")

    def test_delete_user_negative_id(self):
        """Test deleting user with negative ID."""
        print("\n[TEST] delete_user - corner case: negative ID")
        client = FakeApiClient()
        service = UserService(client)

        with pytest.raises(ValueError):
            print("  [ACTION] Attempting to delete user -1")
            service.delete_user(-1)
        print("  [PASS] Correctly raised ValueError")

    def test_delete_user_twice(self):
        """Test deleting the same user twice."""
        print("\n[TEST] delete_user - corner case: delete twice")
        client = FakeApiClient()
        service = UserService(client)

        print("  [ACTION] First delete")
        result1 = service.delete_user(1)
        assert result1["deleted"] is True

        with pytest.raises(KeyError):
            print("  [ACTION] Second delete (should fail)")
            service.delete_user(1)
        print("  [PASS] Second delete correctly failed")

    def test_delete_user_reduces_count(self):
        """Test that delete reduces user count."""
        print("\n[TEST] delete_user - verify count reduction")
        client = FakeApiClient()
        service = UserService(client)

        initial_count = len(service.list_users())
        print(f"  [OK] Initial count: {initial_count}")

        service.delete_user(1)
        final_count = len(service.list_users())
        print(f"  [OK] Final count: {final_count}")

        assert final_count == initial_count - 1
        print("  [PASS] Count reduced by 1")
