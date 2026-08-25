#!/usr/bin/env python3
"""HTTP server wrapper for MCP stdio server."""

import json
import subprocess
import os
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MCPHandler(BaseHTTPRequestHandler):
    """HTTP handler that forwards requests to MCP server via stdio."""

    def do_POST(self):
        """Handle POST requests to MCP."""
        if self.path != "/mcp":
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')
            return

        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            logger.info(f"MCP Request: {body[:100]}")

            # Send to MCP server via stdin
            process = subprocess.Popen(
                [sys.executable, "-m", "src.example.mcp.server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd(),
            )

            stdout, stderr = process.communicate(input=body, timeout=5)

            if stderr:
                logger.warning(f"MCP stderr: {stderr}")

            # Send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(stdout.encode("utf-8"))
            logger.info("MCP Response sent")

        except subprocess.TimeoutExpired:
            logger.error("MCP server timeout")
            self.send_response(504)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Gateway Timeout"}')
        except Exception as e:
            logger.error(f"MCP Error: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def do_GET(self):
        """Handle GET requests for health check."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "service": "mcp-server"}')
            logger.info("Health check OK")
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    def log_message(self, format, *args):
        """Log messages using logger."""
        logger.info(format % args)


def run_server():
    """Start the HTTP server."""
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    server = HTTPServer((host, port), MCPHandler)
    logger.info(f"Starting HTTP MCP Server on {host}:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
        server.shutdown()


if __name__ == "__main__":
    run_server()
