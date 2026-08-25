#!/usr/bin/env python3
"""WebSocket server for MCP protocol."""

import asyncio
import json
import logging
import os
import sys
from typing import Any

try:
    import websockets
except ImportError:
    print("Error: websockets library not found. Install with: pip install websockets")
    sys.exit(1)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from example.api.api_client import ApiClient
from example.business.service import UserService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize service
api_client = ApiClient()
user_service = UserService(api_client)


class MCPServer:
    """MCP (Model Context Protocol) server over WebSocket."""

    def __init__(self):
        self.request_id = 0
        self.tools = {
            "get_user": {
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
                "description": "List all users.",
                "inputSchema": {"type": "object", "properties": {}}
            },
            "create_user": {
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

    async def handle_request(self, request: dict) -> dict:
        """Handle MCP requests."""
        method = request.get("method")
        req_id = request.get("id")

        logger.info(f"Handling request: {method}")

        try:
            if method == "initialize":
                return self.handle_initialize(req_id)
            elif method == "tools/list":
                return self.handle_list_tools(req_id)
            elif method == "tools/call":
                return await self.handle_call_tool(request, req_id)
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": req_id
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": req_id
            }

    def handle_initialize(self, req_id: int) -> dict:
        """Handle initialize request."""
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "example-users-mcp",
                    "version": "1.0.0"
                }
            },
            "id": req_id
        }

    def handle_list_tools(self, req_id: int) -> dict:
        """Handle tools/list request."""
        tools = [
            {
                "name": name,
                "description": info["description"],
                "inputSchema": info["inputSchema"]
            }
            for name, info in self.tools.items()
        ]
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools},
            "id": req_id
        }

    async def handle_call_tool(self, request: dict, req_id: int) -> dict:
        """Handle tools/call request."""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"Calling tool: {tool_name} with args: {arguments}")

        if tool_name not in self.tools:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                },
                "id": req_id
            }

        try:
            if tool_name == "get_user":
                result = user_service.get_user(arguments["user_id"])
            elif tool_name == "list_users":
                result = user_service.list_users()
            elif tool_name == "create_user":
                result = user_service.create_user(arguments["name"], arguments["email"])
            elif tool_name == "update_user":
                result = user_service.update_user(
                    arguments["user_id"],
                    arguments.get("name"),
                    arguments.get("email")
                )
            elif tool_name == "delete_user":
                result = user_service.delete_user(arguments["user_id"])
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                    "id": req_id
                }

            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result)}]
                },
                "id": req_id
            }
        except Exception as e:
            logger.error(f"Tool error: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Error calling tool: {str(e)}"
                },
                "id": req_id
            }

    async def handle_client(self, websocket) -> None:
        """Handle client connections."""
        client_id = id(websocket)
        logger.info(f"Client {client_id} connected")

        try:
            async for message in websocket:
                logger.info(f"Received from {client_id}: {message[:100]}")

                try:
                    request = json.loads(message)
                    response = await self.handle_request(request)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    await websocket.send(json.dumps(error_response))
        except Exception as e:
            if "connection closed" not in str(e).lower():
                logger.error(f"Error handling client {client_id}: {e}")
            else:
                logger.info(f"Client {client_id} disconnected")


async def main():
    """Start the WebSocket MCP server."""
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    server = MCPServer()

    async with websockets.serve(server.handle_client, host, port):
        logger.info(f"WebSocket MCP Server running on ws://{host}:{port}")
        logger.info("Waiting for connections...")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
