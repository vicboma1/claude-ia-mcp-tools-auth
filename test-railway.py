#!/usr/bin/env python3
"""
MCP Auth Server - Complete Flow Test for Railway
Tests the entire authentication flow against a Railway deployment
Usage: python test-railway.py [URL]
Example: python test-railway.py https://claude-ia-mcp-tools-auth-staging.up.railway.app
"""

import sys
import requests
import re
import json

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def main():
    railway_url = sys.argv[1] if len(sys.argv) > 1 else "https://claude-ia-mcp-tools-auth-staging.up.railway.app"

    print(f"{Colors.CYAN}=========================================={Colors.ENDC}")
    print(f"{Colors.CYAN}  Railway Auth Server - Complete Test{Colors.ENDC}")
    print(f"{Colors.CYAN}=========================================={Colors.ENDC}")
    print(f"{Colors.GREEN}URL: {railway_url}{Colors.ENDC}")
    print()

    try:
        # Step 1: Start auth flow
        print(f"{Colors.YELLOW}Step 1: Start Auth Flow{Colors.ENDC}")
        print(f"{Colors.GRAY}Command: curl -L {railway_url}/auth/start{Colors.ENDC}")
        print()

        response = requests.get(f"{railway_url}/auth/start", allow_redirects=False, timeout=10)
        redirect_url = response.headers.get('Location', '')

        print(f"{Colors.GREEN}Redirect URL: {redirect_url}{Colors.ENDC}")

        # Extract state
        state_match = re.search(r'state=([^&]*)', redirect_url)
        if not state_match:
            print(f"{Colors.RED}ERROR: Could not extract state token{Colors.ENDC}")
            return 1

        state = state_match.group(1)
        print(f"{Colors.GREEN}Extracted State: {state}{Colors.ENDC}")
        print()

        # Step 2: Complete callback
        print(f"{Colors.YELLOW}Step 2: Complete Auth Callback{Colors.ENDC}")
        callback_url = f"{railway_url}/auth/callback?state={state}"
        print(f"{Colors.GRAY}Command: curl {callback_url}{Colors.ENDC}")
        print()

        response = requests.get(callback_url, timeout=10)
        response_text = response.text

        # Extract token
        token_match = re.search(r'class="token-box">([A-Za-z0-9_-]+)</div>', response_text)
        if not token_match:
            print(f"{Colors.RED}ERROR: Could not extract session token{Colors.ENDC}")
            return 1

        session_token = token_match.group(1)
        print(f"{Colors.GREEN}Extracted Session Token: {session_token}{Colors.ENDC}")
        print()

        # Step 3: Verify token
        print(f"{Colors.YELLOW}Step 3: Verify Token{Colors.ENDC}")
        print(f"{Colors.GRAY}Command: curl -H 'Authorization: Bearer {session_token}' {railway_url}/auth/status{Colors.ENDC}")
        print()

        headers = {"Authorization": f"Bearer {session_token}"}
        response = requests.get(f"{railway_url}/auth/status", headers=headers, timeout=10)
        status_data = response.json()
        status_response = json.dumps(status_data)

        print(f"{Colors.GREEN}Response: {status_response}{Colors.ENDC}")
        print()

        # Step 4: Test invalid token
        print(f"{Colors.YELLOW}Step 4: Test Invalid Token{Colors.ENDC}")
        print(f"{Colors.GRAY}Command: curl -H 'Authorization: Bearer invalid_token' {railway_url}/auth/status{Colors.ENDC}")
        print()

        invalid_headers = {"Authorization": "Bearer invalid_token_123"}
        response = requests.get(f"{railway_url}/auth/status", headers=invalid_headers, timeout=10)
        invalid_response = json.dumps(response.json())

        print(f"{Colors.YELLOW}Response: {invalid_response}{Colors.ENDC}")
        print()

        # Summary
        print(f"{Colors.CYAN}=========================================={Colors.ENDC}")
        print(f"{Colors.CYAN}         TEST SUMMARY{Colors.ENDC}")
        print(f"{Colors.CYAN}=========================================={Colors.ENDC}")
        print(f"{Colors.GREEN}State Token:     {state}{Colors.ENDC}")
        print(f"{Colors.GREEN}Session Token:   {session_token}{Colors.ENDC}")
        print()

        if status_data.get('authenticated') == True:
            print(f"{Colors.GREEN}SUCCESS: Auth flow working on Railway!{Colors.ENDC}")
            print()
            print(f"{Colors.YELLOW}You can now use this token:{Colors.ENDC}")
            print(f"{Colors.CYAN}  Authorization: Bearer {session_token}{Colors.ENDC}")
            return 0
        else:
            print(f"{Colors.RED}FAILED: Authentication not working{Colors.ENDC}")
            return 1

    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}ERROR: Cannot connect to {railway_url}{Colors.ENDC}")
        return 1
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}ERROR: Request timeout{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"{Colors.RED}ERROR: {str(e)}{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
