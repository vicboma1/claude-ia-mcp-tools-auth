"""Test suite for MCP server with authentication."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import tempfile
import pytest
from example.mcp.server import handle_request, TOOLS
from example.auth.manager import AuthManager


class TestMCPServerAuth:
    """Test MCP server authentication requirements."""

    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.token_file = os.path.join(self.temp_dir, ".auth_tokens.json")
        # Import fresh to use new token file
        from example.auth.manager import AuthManager
        self.auth_manager = AuthManager(tokens_file=self.token_file)

    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _get_valid_token(self):
        """Helper to create a valid auth token."""
        auth_url, state = self.auth_manager.generate_auth_url("http://localhost:5000/callback")
        self.auth_manager.authenticate(state)
        return list(self.auth_manager.tokens.keys())[0]

    def test_initialize_returns_server_info(self):
        """Test initialize returns server info with auth requirement."""
        print("\n[TEST] initialize - returns server info")

        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }

        response = handle_request(request)
        print(f"  [OK] Response: {json.dumps(response, indent=2)}")

        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert response["result"]["serverInfo"]["authRequired"] is True
        assert response["result"]["serverInfo"]["authUrl"] == "http://localhost:5000"
        print("  [PASS] Server info includes auth requirements")

    def test_tools_list_does_not_require_auth(self):
        """Test tools/list is public and doesn't require auth."""
        print("\n[TEST] tools/list - no auth required")

        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }

        response = handle_request(request)
        print(f"  [OK] Response keys: {list(response.keys())}")

        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) > 0
        print(f"  [PASS] Listed {len(response['result']['tools'])} tools without auth")

    def test_get_auth_url_tool_listed(self):
        """Test get_auth_url is available in tools list."""
        print("\n[TEST] get_auth_url - listed in tools")

        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }

        response = handle_request(request)
        tools = response["result"]["tools"]
        tool_names = [t["name"] for t in tools]

        print(f"  [OK] Available tools: {tool_names}")

        assert "get_auth_url" in tool_names
        print("  [PASS] get_auth_url tool is available")

    def test_tools_call_without_auth_fails(self):
        """Test protected tool call without auth fails."""
        print("\n[TEST] tools/call - fails without auth")

        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_user",
                "arguments": {"user_id": 1}
            },
            "id": 1
        }

        response = handle_request(request)
        print(f"  [OK] Response: {json.dumps(response, indent=2)}")

        assert "error" in response
        assert response["error"]["code"] == 401
        assert "Authentication required" in response["error"]["message"]
        print("  [PASS] Tool call rejected without auth")

    def test_tools_call_with_invalid_token_fails(self):
        """Test tool call with invalid token fails."""
        print("\n[TEST] tools/call - fails with invalid token")

        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_user",
                "arguments": {"user_id": 1},
                "auth_token": "invalid_token_123"
            },
            "id": 1
        }

        response = handle_request(request)
        print(f"  [OK] Response: {json.dumps(response, indent=2)}")

        assert "error" in response
        assert response["error"]["code"] == 401
        print("  [PASS] Tool call rejected with invalid token")

    def test_tools_call_with_valid_token_succeeds(self):
        """Test protected tool call with valid token succeeds."""
        print("\n[TEST] tools/call - succeeds with valid token")

        token = self._get_valid_token()
        print(f"  [OK] Created valid token: {token[:20]}...")

        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "list_users",
                "arguments": {},
                "auth_token": token
            },
            "id": 1
        }

        response = handle_request(request)
        print(f"  [OK] Response has result: {'result' in response}")

        assert "result" in response or "error" not in response
        assert "error" not in response or response.get("error", {}).get("code") != 401
        print("  [PASS] Tool call accepted with valid token")

    def test_get_auth_url_returns_valid_url(self):
        """Test get_auth_url tool returns valid URL."""
        print("\n[TEST] get_auth_url - returns valid URL")

        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_auth_url",
                "arguments": {}
            },
            "id": 1
        }

        response = handle_request(request)
        print(f"  [OK] Response: {json.dumps(response, indent=2)}")

        assert "result" in response
        content = response["result"]["content"][0]
        assert content["type"] == "text"

        result_data = json.loads(content["text"])
        print(f"  [OK] Auth URL: {result_data['auth_url']}")

        assert "auth_url" in result_data
        assert result_data["auth_url"].startswith("http://localhost:5000/auth/callback?state=")
        assert "message" in result_data
        print("  [PASS] get_auth_url returns valid URL")


class TestMCPServerErrorHandling:
    """Test MCP server error handling."""

    def test_unknown_method_error(self):
        """Test unknown method returns error."""
        print("\n[TEST] unknown method - returns error")

        request = {
            "jsonrpc": "2.0",
            "method": "unknown/method",
            "id": 1
        }

        response = handle_request(request)
        print(f"  [OK] Response: {json.dumps(response, indent=2)}")

        assert "error" in response
        assert response["error"]["code"] == -32601
        print("  [PASS] Unknown method error returned")

    def test_unknown_tool_error(self):
        """Test unknown tool returns error."""
        print("\n[TEST] unknown tool - returns error")

        temp_dir = tempfile.mkdtemp()
        token_file = os.path.join(temp_dir, ".auth_tokens.json")
        auth_manager = AuthManager(tokens_file=token_file)

        auth_url, state = auth_manager.generate_auth_url("http://localhost:5000/callback")
        auth_manager.authenticate(state)
        token = list(auth_manager.tokens.keys())[0]

        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {},
                "auth_token": token
            },
            "id": 1
        }

        response = handle_request(request)
        print(f"  [OK] Response: {json.dumps(response, indent=2)}")

        assert "error" in response
        assert "Unknown tool" in response["error"]["message"]
        print("  [PASS] Unknown tool error returned")

        import shutil
        shutil.rmtree(temp_dir)

    def test_malformed_request_handled(self):
        """Test malformed request is handled gracefully."""
        print("\n[TEST] malformed request - handled gracefully")

        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_user"
                # Missing required arguments
            },
            "id": 1
        }

        # This should trigger an error in the handler
        try:
            response = handle_request(request)
            print(f"  [OK] Response: {json.dumps(response, indent=2)}")
            assert "error" in response
            print("  [PASS] Malformed request handled")
        except Exception as e:
            print(f"  [FAIL] Unexpected exception: {e}")
            raise
