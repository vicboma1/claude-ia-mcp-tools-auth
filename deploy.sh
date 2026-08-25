#!/bin/bash

# Railway Deployment Script
# Automates the deployment process

set -e

echo "=================================================="
echo "  Railway Deployment Script"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI not found!${NC}"
    echo ""
    echo "Install with:"
    echo "  npm install -g @railway/cli"
    echo ""
    echo "Or:"
    echo "  curl -fsSL https://railway.app/install.sh | bash"
    exit 1
fi

echo -e "${BLUE}Step 1: Verify Railway Installation${NC}"
railway --version
echo -e "${GREEN}✓ Railway CLI installed${NC}"
echo ""

echo -e "${BLUE}Step 2: Check if Logged In${NC}"
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}Not logged in. Opening login page...${NC}"
    railway login
fi
echo -e "${GREEN}✓ Logged in${NC}"
echo ""

echo -e "${BLUE}Step 3: Initialize Project (if needed)${NC}"
if [ ! -f "railway.json" ]; then
    echo "Initializing new Railway project..."
    railway init --name claude-ia-mcp-tools-auth || true
fi
echo -e "${GREEN}✓ Railway project configured${NC}"
echo ""

echo -e "${BLUE}Step 4: Deploy to Railway${NC}"
echo "Deploying... this may take 2-5 minutes"
railway up

echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo ""

echo -e "${BLUE}Step 5: Get Deployment URL${NC}"
railway open || echo "Open Railway dashboard manually to get URL"

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Wait for deployment to complete (check logs)"
echo "2. Test with: python test-railway.py <URL>"
echo "3. Set RAILWAY_TOKEN in GitHub secrets for CI/CD"
echo ""

echo "=================================================="
echo "  Deployment Complete!"
echo "=================================================="
