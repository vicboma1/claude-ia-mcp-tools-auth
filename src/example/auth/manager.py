"""OAuth authentication manager for MCP server."""

import os
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages OAuth authentication state and tokens."""

    def __init__(self, tokens_file: str = ".auth_tokens.json"):
        self.tokens_file = tokens_file
        self.tokens = self._load_tokens()
        self.pending_auths = {}  # state -> {redirect_uri, created_at}

    def _load_tokens(self) -> dict:
        """Load tokens from file."""
        if os.path.exists(self.tokens_file):
            try:
                with open(self.tokens_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load tokens: {e}")
        return {}

    def _save_tokens(self):
        """Save tokens to file."""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(self.tokens, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")

    def generate_auth_url(self, redirect_uri: str) -> tuple[str, str]:
        """
        Generate an authentication URL and state token.

        Returns:
            (auth_url, state) - The OAuth URL to visit and the state token to verify
        """
        state = secrets.token_urlsafe(32)
        self.pending_auths[state] = {
            "redirect_uri": redirect_uri,
            "created_at": datetime.now().isoformat()
        }

        # Simple OAuth flow - user clicks link to authenticate
        auth_url = f"http://localhost:5000/auth/callback?state={state}"
        return auth_url, state

    def authenticate(self, state: str) -> tuple[bool, Optional[str]]:
        """
        Authenticate with the given state token.
        Validates state and creates a session token.

        Returns:
            (success: bool, session_token: str | None)
        """
        if state not in self.pending_auths:
            logger.warning(f"Invalid state token: {state}")
            return False, None

        auth_data = self.pending_auths.pop(state)

        # Check if state is not expired (10 minutes)
        created_at = datetime.fromisoformat(auth_data["created_at"])
        if datetime.now() - created_at > timedelta(minutes=10):
            logger.warning(f"State token expired: {state}")
            return False, None

        # Create session token
        session_token = secrets.token_urlsafe(32)
        self.tokens[session_token] = {
            "created_at": datetime.now().isoformat(),
            "user_id": "user_" + secrets.token_hex(8)
        }
        self._save_tokens()

        logger.info(f"Authentication successful with session token")
        return True, session_token

    def get_session_token(self, state: str) -> Optional[str]:
        """Get the session token for a state after authentication.

        Note: This is deprecated. Use the return value from authenticate() instead.
        """
        if state not in self.pending_auths:
            return None

        # Find the session token that was just created
        # (This is a simplified version - in production, link state to session)
        latest_token = max(
            self.tokens.items(),
            key=lambda x: x[1]["created_at"],
            default=(None, None)
        )[0]
        return latest_token

    def is_authenticated(self, token: str) -> bool:
        """Check if a token is valid."""
        if token not in self.tokens:
            return False

        token_data = self.tokens[token]
        created_at = datetime.fromisoformat(token_data["created_at"])
        # Token valid for 24 hours
        if datetime.now() - created_at > timedelta(hours=24):
            del self.tokens[token]
            self._save_tokens()
            return False

        return True

    def get_user_id(self, token: str) -> Optional[str]:
        """Get the user ID associated with a token."""
        if self.is_authenticated(token):
            return self.tokens[token].get("user_id")
        return None
