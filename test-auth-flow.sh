#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${1:-https://claude-ia-mcp-tools-auth-staging.up.railway.app}"
VERBOSE="${2:---verbose}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  MCP Auth Server - Complete Flow Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Base URL: ${BASE_URL}\n"

# Test 1: Start Auth Flow
echo -e "${YELLOW}Step 1: Start Auth Flow${NC}"
echo "GET /auth/start"

RESPONSE=$(curl -s -w "\n%{http_code}" -L "$BASE_URL/auth/start")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo -e "Status: ${GREEN}$HTTP_CODE${NC}"

# Extract auth URL from redirect
AUTH_URL=$(echo "$BODY" | grep -oP 'http[s]?://[^"]*callback[^"]*' | head -1)

if [ -z "$AUTH_URL" ]; then
    echo -e "${RED}Error: Could not extract auth URL${NC}"
    exit 1
fi

echo -e "Auth URL: ${GREEN}$AUTH_URL${NC}\n"

# Extract state token
STATE=$(echo "$AUTH_URL" | grep -oP 'state=\K[^&]*')
echo -e "State Token: ${GREEN}${STATE:0:40}...${NC}\n"

# Test 2: Complete Auth Callback
echo -e "${YELLOW}Step 2: Complete Auth Callback${NC}"
echo "GET /auth/callback?state=$STATE"

CALLBACK_RESPONSE=$(curl -s "$BASE_URL/auth/callback?state=$STATE")
HTTP_CODE=$?

echo -e "Status: ${GREEN}200${NC}"

# Extract session token from HTML
SESSION_TOKEN=$(echo "$CALLBACK_RESPONSE" | grep -oP 'user_[a-f0-9]{16}' | head -1)

if [ -z "$SESSION_TOKEN" ]; then
    echo -e "${RED}Error: Could not extract session token${NC}"
    exit 1
fi

echo -e "Session Token: ${GREEN}${SESSION_TOKEN:0:40}...${NC}\n"

# Test 3: Verify Token with Auth Status
echo -e "${YELLOW}Step 3: Verify Token with Auth Status${NC}"
echo "GET /auth/status -H 'Authorization: Bearer $SESSION_TOKEN'"

STATUS_RESPONSE=$(curl -s -H "Authorization: Bearer $SESSION_TOKEN" "$BASE_URL/auth/status")

echo -e "Response:"
echo -e "${GREEN}$STATUS_RESPONSE${NC}\n"

# Parse response
AUTHENTICATED=$(echo "$STATUS_RESPONSE" | grep -oP '"authenticated":\s*\K[^,}]*')
USER_ID=$(echo "$STATUS_RESPONSE" | grep -oP '"user_id":\s*"\K[^"]*')

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}         TEST RESULTS${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "State Token:     ${GREEN}$STATE${NC}"
echo -e "Session Token:   ${GREEN}$SESSION_TOKEN${NC}"
echo -e "Authenticated:   ${GREEN}$AUTHENTICATED${NC}"
echo -e "User ID:         ${GREEN}$USER_ID${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Test 4: Test Invalid Token
echo -e "${YELLOW}Step 4: Test Invalid Token${NC}"
echo "GET /auth/status -H 'Authorization: Bearer invalid_token_123'"

INVALID_RESPONSE=$(curl -s -H "Authorization: Bearer invalid_token_123" "$BASE_URL/auth/status")
echo -e "Response: ${YELLOW}$INVALID_RESPONSE${NC}\n"

# Final summary
if [ "$AUTHENTICATED" = "true" ]; then
    echo -e "${GREEN}SUCCESS: Complete auth flow working correctly!${NC}"
    echo ""
    echo -e "${YELLOW}You can now use this token for MCP:${NC}"
    echo -e "${BLUE}Authorization: Bearer $SESSION_TOKEN${NC}"
else
    echo -e "${RED}FAILED: Authentication verification failed${NC}"
    exit 1
fi
