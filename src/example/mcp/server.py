#!/usr/bin/env python3
"""MCP server for managing users with OAuth authentication."""

import json
import sys
import logging

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from src.example.api.api_client import ApiClient
from src.example.business.service import UserService
from src.example.auth.manager import AuthManager


# Dependencies
api_client = ApiClient()
user_service = UserService(api_client)
auth_manager = AuthManager()


# Tool handlers
def handle_get_auth_url() -> dict:
    """Get the authentication URL to start OAuth flow."""
    auth_url, state = auth_manager.generate_auth_url("http://localhost:5000/auth/callback")
    return {
        "auth_url": auth_url,
        "message": "Click the auth_url to authenticate in your browser. You'll receive a session token.",
        "state": state
    }


def handle_get_user(user_id: int) -> dict:
    """Get one user by ID."""
    return user_service.get_user(user_id)


def handle_list_users() -> list[dict]:
    """List all users."""
    return user_service.list_users()


def handle_create_user(name: str, email: str) -> dict:
    """Create a user."""
    return user_service.create_user(name, email)


def handle_update_user(
    user_id: int,
    name: str | None = None,
    email: str | None = None,
) -> dict:
    """Update a user's name and/or email."""
    return user_service.update_user(user_id, name, email)


def handle_delete_user(user_id: int) -> dict:
    """Delete a user."""
    return user_service.delete_user(user_id)


# Tool registry
TOOLS = {
    "get_auth_url": {
        "handler": handle_get_auth_url,
        "description": "Get the OAuth authentication URL. Click it in your browser to authenticate and receive a session token.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "get_user": {
        "handler": handle_get_user,
        "description": "Get one user by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "The user ID"}
            },
            "required": ["user_id"]
        }
    },
    "list_users": {
        "handler": handle_list_users,
        "description": "List all users.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "create_user": {
        "handler": handle_create_user,
        "description": "Create a user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "User name"},
                "email": {"type": "string", "description": "User email"}
            },
            "required": ["name", "email"]
        }
    },
    "update_user": {
        "handler": handle_update_user,
        "description": "Update a user's name and/or email.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "The user ID"},
                "name": {"type": "string", "description": "New name (optional)"},
                "email": {"type": "string", "description": "New email (optional)"}
            },
            "required": ["user_id"]
        }
    },
    "delete_user": {
        "handler": handle_delete_user,
        "description": "Delete a user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "The user ID"}
            },
            "required": ["user_id"]
        }
    }
}


def create_tool_schema(name: str, tool_info: dict) -> dict:
    """Create a tool schema for MCP."""
    return {
        "name": name,
        "description": tool_info["description"],
        "inputSchema": tool_info["inputSchema"]
    }


def get_auth_token(request: dict) -> str | None:
    """Extract authentication token from request."""
    # Check for auth_token in params or in request metadata
    params = request.get("params", {})
    token = params.get("auth_token")
    if token:
        return token

    # Also check in a meta field if provided
    meta = request.get("meta", {})
    token = meta.get("auth_token")
    if token:
        return token

    return None


def handle_request(request: dict) -> dict:
    """Handle an MCP request."""
    method = request.get("method")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "example-users",
                    "version": "1.0.0",
                    "authRequired": True,
                    "authUrl": "http://localhost:5000"
                }
            },
            "id": req_id
        }

    elif method == "tools/list":
        tools = [create_tool_schema(name, info) for name, info in TOOLS.items()]
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools},
            "id": req_id
        }

    elif method == "tools/call":
        # Check authentication
        token = get_auth_token(request)
        if not token or not auth_manager.is_authenticated(token):
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": 401,
                    "message": "Authentication required. Please visit http://localhost:5000 to authenticate.",
                    "data": {"authUrl": "http://localhost:5000"}
                },
                "id": req_id
            }

        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                },
                "id": req_id
            }

        try:
            handler = TOOLS[tool_name]["handler"]
            result = handler(**arguments)
            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result)}]
                },
                "id": req_id
            }
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Error: {str(e)}"
                },
                "id": req_id
            }

    else:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": f"Unknown method: {method}"
            },
            "id": req_id
        }


def run_server():
    """Main server loop - reads JSON-RPC from stdin, writes to stdout."""
    logger.info("MCP Server starting on stdio...")

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_server()
