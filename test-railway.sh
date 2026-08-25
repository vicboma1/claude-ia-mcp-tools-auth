#!/bin/bash

# MCP Auth Server - Complete Flow Test for Railway
# Usage: ./test-railway.sh [URL]
# Example: ./test-railway.sh https://claude-ia-mcp-tools-auth-staging.up.railway.app

RAILWAY_URL="${1:-https://claude-ia-mcp-tools-auth-staging.up.railway.app}"

echo "=========================================="
echo "  Railway Auth Server - Complete Test"
echo "=========================================="
echo "URL: $RAILWAY_URL"
echo ""

# Step 1: Start auth flow and extract state
echo "Step 1: Start Auth Flow"
echo "Command: curl -L $RAILWAY_URL/auth/start"
echo ""

REDIRECT=$(curl -s -L -w "\n%{redirect_url}" "$RAILWAY_URL/auth/start" | tail -1)
echo "Redirect URL: $REDIRECT"

STATE=$(echo "$REDIRECT" | grep -oP 'state=\K[^&]*')
if [ -z "$STATE" ]; then
    echo "ERROR: Could not extract state token"
    exit 1
fi

echo "Extracted State: $STATE"
echo ""

# Step 2: Complete auth callback and extract token
echo "Step 2: Complete Auth Callback"
CALLBACK_URL="$RAILWAY_URL/auth/callback?state=$STATE"
echo "Command: curl $CALLBACK_URL"
echo ""

CALLBACK_RESPONSE=$(curl -s "$CALLBACK_URL")

# Extract token from HTML (look for the token in the token-box div)
SESSION_TOKEN=$(echo "$CALLBACK_RESPONSE" | grep -oP 'class="token-box">\K[A-Za-z0-9_-]+')

if [ -z "$SESSION_TOKEN" ]; then
    echo "ERROR: Could not extract session token"
    exit 1
fi

echo "Extracted Session Token: $SESSION_TOKEN"
echo ""

# Step 3: Verify token
echo "Step 3: Verify Token"
echo "Command: curl -H 'Authorization: Bearer $SESSION_TOKEN' $RAILWAY_URL/auth/status"
echo ""

STATUS_RESPONSE=$(curl -s -H "Authorization: Bearer $SESSION_TOKEN" "$RAILWAY_URL/auth/status")
echo "Response: $STATUS_RESPONSE"
echo ""

# Step 4: Test invalid token
echo "Step 4: Test Invalid Token"
echo "Command: curl -H 'Authorization: Bearer invalid_token' $RAILWAY_URL/auth/status"
echo ""

INVALID_RESPONSE=$(curl -s -H "Authorization: Bearer invalid_token_123" "$RAILWAY_URL/auth/status")
echo "Response: $INVALID_RESPONSE"
echo ""

# Summary
echo "=========================================="
echo "         TEST SUMMARY"
echo "=========================================="
echo "State Token:     $STATE"
echo "Session Token:   $SESSION_TOKEN"
echo ""

if echo "$STATUS_RESPONSE" | grep -q '"authenticated": true'; then
    echo "SUCCESS: Auth flow working on Railway!"
    echo ""
    echo "You can now use this token:"
    echo "  Authorization: Bearer $SESSION_TOKEN"
else
    echo "FAILED: Authentication not working"
    exit 1
fi
