#!/usr/bin/env python3
"""
MCP Auth Server - Complete Flow Test
Tests the entire authentication flow end-to-end
"""

import sys
import requests
import re
import json
from urllib.parse import urlparse, parse_qs

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title):
    print(f"\n{Colors.BLUE}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.BLUE}{title}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.ENDC}\n")

def print_step(step_num, title):
    print(f"{Colors.YELLOW}Step {step_num}: {title}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.GREEN}+ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.RED}X {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.CYAN}  {msg}{Colors.ENDC}")

def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://claude-ia-mcp-tools-auth-staging.up.railway.app"

    print_section("MCP Auth Server - Complete Flow Test")
    print_info(f"Base URL: {base_url}\n")

    try:
        # Step 1: Start Auth Flow
        print_step(1, "Start Auth Flow")
        print_info(f"GET {base_url}/auth/start\n")

        response = requests.get(f"{base_url}/auth/start", allow_redirects=False, timeout=5)
        print_success(f"Status: {response.status_code}")

        location = response.headers.get('Location', '')
        if not location:
            print_error("No redirect location found")
            return 1

        print_success(f"Redirect: {location[:60]}...")

        # Extract state token
        state_match = re.search(r'state=([^&]*)', location)
        if not state_match:
            print_error("Could not extract state token")
            return 1

        state = state_match.group(1)
        print_success(f"State Token: {state[:40]}...\n")

        # Step 2: Complete Auth Callback
        print_step(2, "Complete Auth Callback")
        callback_url = f"{base_url}/auth/callback?state={state}"
        print_info(f"GET /auth/callback?state={state}\n")

        response = requests.get(callback_url, timeout=5)
        print_success(f"Status: {response.status_code}")

        # Extract session token from HTML token-box
        token_match = re.search(r'class="token-box">([A-Za-z0-9_-]+)</div>', response.text)
        if not token_match:
            print_error("Could not extract session token from response")
            print_info("Debugging: checking if token is in response...")
            if "user_" in response.text:
                # Try alternative pattern
                token_match = re.search(r'user_[A-Za-z0-9_-]+', response.text)
            if not token_match:
                return 1

        session_token = token_match.group(1) if '>' in token_match.group(0) else token_match.group(0)
        print_success(f"Session Token: {session_token[:40]}...\n")

        # Step 3: Verify Token with Auth Status
        print_step(3, "Verify Token with Auth Status")
        print_info(f"GET /auth/status -H 'Authorization: Bearer {session_token}'\n")

        headers = {"Authorization": f"Bearer {session_token}"}
        response = requests.get(f"{base_url}/auth/status", headers=headers, timeout=5)
        print_success(f"Status: {response.status_code}")

        status_data = response.json()
        print_info(f"Response: {json.dumps(status_data, indent=2)}\n")

        # Step 4: Test Invalid Token
        print_step(4, "Test Invalid Token")
        print_info(f"GET /auth/status -H 'Authorization: Bearer invalid_token_123'\n")

        invalid_headers = {"Authorization": "Bearer invalid_token_123"}
        response = requests.get(f"{base_url}/auth/status", headers=invalid_headers, timeout=5)
        invalid_data = response.json()
        print_info(f"Response: {json.dumps(invalid_data, indent=2)}\n")

        # Results Summary
        print_section("TEST RESULTS")
        print(f"{Colors.GREEN}State Token:     {state}{Colors.ENDC}")
        print(f"{Colors.GREEN}Session Token:   {session_token}{Colors.ENDC}")
        print(f"{Colors.GREEN}Authenticated:   {status_data.get('authenticated')}{Colors.ENDC}")
        print(f"{Colors.GREEN}User ID:         {status_data.get('user_id')}{Colors.ENDC}")

        if status_data.get('authenticated') == True:
            print(f"\n{Colors.GREEN}SUCCESS: Complete auth flow working correctly!{Colors.ENDC}\n")
            print(f"{Colors.YELLOW}You can now use this token for MCP:{Colors.ENDC}")
            print(f"{Colors.BLUE}Authorization: Bearer {session_token}{Colors.ENDC}\n")
            return 0
        else:
            print_error("Authentication verification failed")
            return 1

    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {base_url}")
        print_info("Make sure the auth server is running:")
        print_info("python -m src.example.http.auth_server")
        return 1
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
