"""Flask HTTP server for OAuth authentication flow."""

import os
import sys
import logging
from flask import Flask, redirect, request, jsonify, render_template_string
from src.example.auth.manager import AuthManager

logger = logging.getLogger(__name__)

auth_manager = AuthManager()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")


@app.route("/", methods=["GET"])
def index():
    """Home page with authentication button."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCP OAuth Authentication</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 400px;
            }
            h1 {
                color: #333;
                margin: 0 0 10px 0;
            }
            p {
                color: #666;
                margin: 0 0 30px 0;
            }
            .auth-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: transform 0.2s;
            }
            .auth-btn:hover {
                transform: scale(1.05);
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                background: #f5f5f5;
                border-radius: 5px;
                font-size: 14px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 MCP Server</h1>
            <p>Authenticate to use MCP tools</p>
            <a href="/auth/start" class="auth-btn">Click to Authenticate</a>
            <div class="status">
                <p>This will generate a session token for MCP tool access.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/auth/start", methods=["GET"])
def auth_start():
    """Start authentication flow."""
    redirect_uri = request.base_url.replace("/auth/start", "/auth/callback")
    auth_url, state = auth_manager.generate_auth_url(redirect_uri)
    return redirect(auth_url)


@app.route("/auth/callback", methods=["GET"])
def auth_callback():
    """OAuth callback endpoint."""
    state = request.args.get("state")

    if not state:
        return jsonify({"error": "Missing state parameter"}), 400

    success, session_token = auth_manager.authenticate(state)
    if not success or not session_token:
        return jsonify({"error": "Authentication failed"}), 401

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authentication Successful</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 500px;
            }}
            h1 {{
                color: #28a745;
                margin: 0 0 10px 0;
            }}
            p {{
                color: #666;
                margin: 0 0 20px 0;
            }}
            .token-box {{
                background: #f5f5f5;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                word-break: break-all;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                color: #333;
                text-align: left;
            }}
            .copy-btn {{
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin-top: 10px;
            }}
            .copy-btn:hover {{
                background: #764ba2;
            }}
            .instruction {{
                background: #e7f3ff;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 20px 0;
                border-radius: 3px;
                text-align: left;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✓ Authentication Successful!</h1>
            <p>You can now use MCP tools with your session token.</p>

            <div class="instruction">
                <strong>Session Token:</strong>
                <div class="token-box">{session_token if session_token else 'Token generation in progress...'}</div>
                <button class="copy-btn" onclick="navigator.clipboard.writeText('{session_token}'); alert('Copied!')">
                    📋 Copy Token
                </button>
            </div>

            <div class="instruction">
                <strong>Next Steps:</strong>
                <ol style="text-align: left;">
                    <li>Copy your session token above</li>
                    <li>Use it in MCP tool calls via the Authorization header</li>
                    <li>Token is valid for 24 hours</li>
                </ol>
            </div>

            <p style="margin-top: 30px; color: #999; font-size: 12px;">
                You can close this window. Your authentication is complete.
            </p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/auth/status", methods=["GET"])
def auth_status():
    """Check authentication status."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"authenticated": False}), 200

    is_auth = auth_manager.is_authenticated(token)
    user_id = auth_manager.get_user_id(token) if is_auth else None

    return jsonify({
        "authenticated": is_auth,
        "user_id": user_id
    }), 200


def run_server():
    """Run the authentication server."""
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run_server()
