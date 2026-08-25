"""Test suite for OAuth authentication manager."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import tempfile
import time
from datetime import datetime, timedelta
from example.auth.manager import AuthManager


class TestAuthManager:
    """Test cases for OAuth authentication manager."""

    def setup_method(self):
        """Setup for each test - use temporary token file."""
        self.temp_dir = tempfile.mkdtemp()
        self.token_file = os.path.join(self.temp_dir, ".auth_tokens.json")
        self.auth_manager = AuthManager(tokens_file=self.token_file)

    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_generate_auth_url_returns_valid_url_and_state(self):
        """Test generating authentication URL."""
        print("\n[TEST] generate_auth_url - returns valid URL and state")

        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        print(f"  [OK] Generated URL: {auth_url}")
        print(f"  [OK] Generated state: {state[:20]}...")

        assert auth_url.startswith("http://localhost:5000/auth/callback?state=")
        assert state is not None
        assert len(state) > 20
        print("  [PASS] Auth URL and state are valid")

    def test_generate_auth_url_stores_pending_auth(self):
        """Test that pending auth is stored."""
        print("\n[TEST] generate_auth_url - stores pending auth")

        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        print(f"  [OK] Generated state: {state[:20]}...")

        assert state in self.auth_manager.pending_auths
        assert self.auth_manager.pending_auths[state]["redirect_uri"] == "http://localhost:5000/callback"
        print("  [PASS] Pending auth stored correctly")

    def test_authenticate_with_valid_state(self):
        """Test successful authentication."""
        print("\n[TEST] authenticate - valid state")

        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        print(f"  [OK] Generated state: {state[:20]}...")

        result = self.auth_manager.authenticate(state)
        print(f"  [OK] Authentication result: {result}")

        assert result is True
        assert state not in self.auth_manager.pending_auths  # State should be consumed
        print("  [PASS] Authentication successful")

    def test_authenticate_with_invalid_state(self):
        """Test authentication with invalid state."""
        print("\n[TEST] authenticate - invalid state")

        result = self.auth_manager.authenticate("invalid_state_123")
        print(f"  [OK] Authentication result: {result}")

        assert result is False
        print("  [PASS] Invalid state rejected")

    def test_authenticate_creates_session_token(self):
        """Test that authentication creates a session token."""
        print("\n[TEST] authenticate - creates session token")

        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        initial_token_count = len(self.auth_manager.tokens)
        print(f"  [OK] Initial tokens: {initial_token_count}")

        self.auth_manager.authenticate(state)
        final_token_count = len(self.auth_manager.tokens)
        print(f"  [OK] Final tokens: {final_token_count}")

        assert final_token_count == initial_token_count + 1
        print("  [PASS] Session token created")

    def test_is_authenticated_with_valid_token(self):
        """Test checking authentication with valid token."""
        print("\n[TEST] is_authenticated - valid token")

        # Create a valid token
        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        self.auth_manager.authenticate(state)
        token = list(self.auth_manager.tokens.keys())[0]
        print(f"  [OK] Created token: {token[:20]}...")

        result = self.auth_manager.is_authenticated(token)
        print(f"  [OK] Authentication check: {result}")

        assert result is True
        print("  [PASS] Valid token authenticated")

    def test_is_authenticated_with_invalid_token(self):
        """Test checking authentication with invalid token."""
        print("\n[TEST] is_authenticated - invalid token")

        result = self.auth_manager.is_authenticated("invalid_token_123")
        print(f"  [OK] Authentication check: {result}")

        assert result is False
        print("  [PASS] Invalid token rejected")

    def test_is_authenticated_with_expired_token(self):
        """Test that expired tokens are rejected."""
        print("\n[TEST] is_authenticated - expired token")

        # Create a token and manually expire it
        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        self.auth_manager.authenticate(state)
        token = list(self.auth_manager.tokens.keys())[0]

        # Manually set token to be old (25 hours)
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        self.auth_manager.tokens[token]["created_at"] = old_time
        print(f"  [OK] Set token created_at to 25 hours ago")

        result = self.auth_manager.is_authenticated(token)
        print(f"  [OK] Authentication check: {result}")

        assert result is False
        assert token not in self.auth_manager.tokens  # Expired token should be deleted
        print("  [PASS] Expired token rejected and deleted")

    def test_get_user_id_returns_user_for_valid_token(self):
        """Test retrieving user ID from valid token."""
        print("\n[TEST] get_user_id - valid token")

        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        self.auth_manager.authenticate(state)
        token = list(self.auth_manager.tokens.keys())[0]
        print(f"  [OK] Created token: {token[:20]}...")

        user_id = self.auth_manager.get_user_id(token)
        print(f"  [OK] User ID: {user_id}")

        assert user_id is not None
        assert user_id.startswith("user_")
        print("  [PASS] User ID retrieved")

    def test_get_user_id_returns_none_for_invalid_token(self):
        """Test that invalid tokens return None."""
        print("\n[TEST] get_user_id - invalid token")

        user_id = self.auth_manager.get_user_id("invalid_token_123")
        print(f"  [OK] User ID: {user_id}")

        assert user_id is None
        print("  [PASS] None returned for invalid token")

    def test_state_expiration(self):
        """Test that auth states expire after 10 minutes."""
        print("\n[TEST] state expiration - expires after 10 minutes")

        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        print(f"  [OK] Generated state: {state[:20]}...")

        # Manually set state creation time to 11 minutes ago
        old_time = (datetime.now() - timedelta(minutes=11)).isoformat()
        self.auth_manager.pending_auths[state]["created_at"] = old_time
        print(f"  [OK] Set state created_at to 11 minutes ago")

        result = self.auth_manager.authenticate(state)
        print(f"  [OK] Authentication result: {result}")

        assert result is False
        print("  [PASS] Expired state rejected")

    def test_tokens_persistence(self):
        """Test that tokens are saved and loaded from file."""
        print("\n[TEST] tokens persistence - saved and loaded")

        # Create a token in first manager
        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        self.auth_manager.authenticate(state)
        token1 = list(self.auth_manager.tokens.keys())[0]
        print(f"  [OK] Created token: {token1[:20]}...")

        # Create second manager that loads from same file
        auth_manager2 = AuthManager(tokens_file=self.token_file)
        print(f"  [OK] Created second manager")

        # Token should be available in second manager
        result = auth_manager2.is_authenticated(token1)
        print(f"  [OK] Token authenticated in second manager: {result}")

        assert result is True
        print("  [PASS] Tokens persisted and loaded correctly")


class TestAuthIntegration:
    """Integration tests for authentication flow."""

    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.token_file = os.path.join(self.temp_dir, ".auth_tokens.json")
        self.auth_manager = AuthManager(tokens_file=self.token_file)

    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_full_auth_flow(self):
        """Test complete authentication flow."""
        print("\n[TEST] full auth flow - complete cycle")

        # Step 1: Generate auth URL
        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        print(f"  [OK] Step 1 - Generated auth URL")

        # Step 2: User clicks and authenticates
        result = self.auth_manager.authenticate(state)
        assert result is True
        print(f"  [OK] Step 2 - Authentication successful")

        # Step 3: Get session token
        token = self.auth_manager.get_session_token(state)
        print(f"  [OK] Step 3 - Got session token")

        # Step 4: Use token to authenticate requests
        is_auth = self.auth_manager.is_authenticated(token)
        assert is_auth is True
        print(f"  [OK] Step 4 - Token authenticated")

        # Step 5: Get user info
        user_id = self.auth_manager.get_user_id(token)
        assert user_id is not None
        print(f"  [OK] Step 5 - Got user ID: {user_id}")

        print("  [PASS] Full auth flow completed successfully")

    def test_multiple_users(self):
        """Test multiple users with different tokens."""
        print("\n[TEST] multiple users - different tokens")

        # Create first user
        auth_url1, state1 = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        self.auth_manager.authenticate(state1)
        token1 = list(self.auth_manager.tokens.keys())[0]
        user1 = self.auth_manager.get_user_id(token1)
        print(f"  [OK] User 1 token: {token1[:20]}... -> {user1}")

        # Create second user
        auth_url2, state2 = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        self.auth_manager.authenticate(state2)
        token2 = list(self.auth_manager.tokens.keys())[-1]
        user2 = self.auth_manager.get_user_id(token2)
        print(f"  [OK] User 2 token: {token2[:20]}... -> {user2}")

        # Verify both tokens work and have different user IDs
        assert self.auth_manager.is_authenticated(token1) is True
        assert self.auth_manager.is_authenticated(token2) is True
        assert user1 != user2
        print("  [PASS] Multiple users have separate tokens")
