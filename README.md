# MCP Tools with OAuth Authentication

A Python example demonstrating how to build an MCP (Model Context Protocol) server with OAuth authentication, combining an API client, business logic layer, and secured MCP tools.

## Features

- **OAuth Authentication Flow**: Click-to-authenticate in browser for session tokens
- **Layered Architecture**: API Client → Business Logic → MCP Tools
- **Secure Tool Access**: Requires valid auth token to call protected tools
- **Simple HTTP Server**: Flask-based auth server running on localhost:5000
- **Token Management**: 24-hour session tokens with persistence

## Architecture

```
src/example/
├── api/
│   ├── api_client.py      # HTTP API client (JSONPlaceholder)
│   └── http_server.py     # Local HTTP server
├── auth/
│   └── manager.py         # OAuth token & state management
├── business/
│   └── service.py         # Business logic layer
├── http/
│   └── auth_server.py     # Flask OAuth auth server
├── mcp/
│   └── server.py          # MCP server with auth
└── main.py
```

## Installation

```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## Quick Start

### 1. Start the Authentication Server

```bash
python -m src.example.http.auth_server
```

This starts a Flask server on `http://localhost:5000` with an OAuth flow:
- Visit the homepage
- Click "Click to Authenticate"
- Get your session token on the callback page
- Copy and save your token

### 2. Start the MCP Server

In another terminal:

```bash
python -m src.example.mcp.server
```

### 3. Use MCP Tools

The MCP server now requires authentication. First, get the auth URL:

```bash
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python -m src.example.mcp.server
```

Then authenticate and use tools with your token:

```bash
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_user","arguments":{"user_id":1},"auth_token":"YOUR_SESSION_TOKEN"},"id":1}' | python -m src.example.mcp.server
```

## Authentication Flow

1. **Get Auth URL**: Call `get_auth_url` tool (no auth required)
   ```json
   {"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_auth_url","arguments":{}},"id":1}
   ```

2. **Click in Browser**: User clicks the returned auth URL
   - Opens `http://localhost:5000/auth/callback?state=...`
   - Browser shows success page with session token
   - Token is valid for 24 hours

3. **Use Token**: Include `auth_token` in all tool calls
   ```json
   {"params":{"name":"get_user","arguments":{"user_id":1},"auth_token":"YOUR_TOKEN"}}
   ```

## Available Tools

### Public (No Auth Required)
- `get_auth_url` - Get OAuth authentication URL

### Protected (Auth Required)
- `get_user` - Get one user by ID
- `list_users` - List all users
- `create_user` - Create a new user
- `update_user` - Update user name/email
- `delete_user` - Delete a user

## Configuration

Set environment variables:

```bash
export PORT=5000                           # Auth server port
export FLASK_SECRET_KEY=your-secret-key    # Flask secret (change in production!)
```

## Testing

Run tests with pytest:

```bash
pytest -v
pytest --cov=src           # With coverage
pytest tests/test_auth.py  # Auth tests only
```

Run shell script

```
sh test-auth-railway.sh
========================================
  MCP Auth Server - Complete Flow Test
========================================
Base URL: https://claude-ia-mcp-tools-auth-staging.up.railway.app

Step 1: Start Auth Flow
GET /auth/start
Status: 401
Auth URL: https://claude-ia-mcp-tools-auth-staging.up.railway.app/auth/callback?state=Xukdt6MwHba0n0UfkOX3lAAanm7MJhSyzomyCJCxj1M

State Token: Xukdt6MwHba0n0UfkOX3lAAanm7MJhSyzomyCJCx...

Step 2: Complete Auth Callback
GET /auth/callback?state=Xukdt6MwHba0n0UfkOX3lAAanm7MJhSyzomyCJCxj1M
Status: 200
Session Token: 7Y6SaanfrLmiOXoE2kUvTbdEfawIMSJyGDaNFPf1...

Step 3: Verify Token with Auth Status
GET /auth/status -H 'Authorization: Bearer 7Y6SaanfrLmiOXoE2kUvTbdEfawIMSJyGDaNFPf1-Bg'
Response:
{"authenticated":true,"user_id":"user_1b25e4982c9904b8"}

========================================
         TEST RESULTS
========================================
State Token:     Xukdt6MwHba0n0UfkOX3lAAanm7MJhSyzomyCJCxj1M
Session Token:   7Y6SaanfrLmiOXoE2kUvTbdEfawIMSJyGDaNFPf1-Bg
Authenticated:   true
User ID:         user_1b25e4982c9904b8
========================================

Step 4: Test Invalid Token
GET /auth/status -H 'Authorization: Bearer invalid_token_123'
Response: {"authenticated":false,"user_id":null}

SUCCESS: Complete auth flow working correctly!

You can now use this token for MCP:
Authorization: Bearer 7Y6SaanfrLmiOXoE2kUvTbdEfawIMSJyGDaNFPf1-Bg

```
## Deployment

For production, update:

1. **FLASK_SECRET_KEY** - Use a strong random key
2. **OAuth Provider** - Replace with real OAuth (Google, GitHub, etc.)
3. **Token Storage** - Use database instead of `.auth_tokens.json`
4. **HTTPS** - Enable SSL/TLS for auth endpoints

## Architecture Notes

This example demonstrates:
- **Separation of Concerns**: API client, business logic, and MCP layer are independent
- **Layered Design**: Easy to test and replace components
- **Authentication Integration**: Auth tokens are passed through params, not headers
- **Error Handling**: Proper error responses for auth failures

The API client uses `https://jsonplaceholder.typicode.com` as a demo API.
Replace with your own API implementation without changing MCP/business interfaces.
