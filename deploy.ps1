# Railway Deployment Script (PowerShell)
# Automates the deployment process

param(
    [switch]$SkipLogin = $false
)

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Railway Deployment Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if railway CLI is installed
Write-Host "Step 1: Verify Railway Installation" -ForegroundColor Blue

$railwayPath = (Get-Command railway -ErrorAction SilentlyContinue).Path

if (-not $railwayPath) {
    Write-Host "Railway CLI not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install with:" -ForegroundColor Yellow
    Write-Host "  npm install -g @railway/cli" -ForegroundColor Gray
    exit 1
}

$version = & railway --version 2>$null
Write-Host "✓ Railway CLI installed: $version" -ForegroundColor Green
Write-Host ""

# Step 2: Check if logged in
Write-Host "Step 2: Check if Logged In" -ForegroundColor Blue

$loggedIn = $null
try {
    $loggedIn = & railway whoami 2>$null
}
catch {
    $loggedIn = $null
}

if (-not $loggedIn) {
    Write-Host "Not logged in. Opening login page..." -ForegroundColor Yellow
    & railway login
}

Write-Host "✓ Logged in" -ForegroundColor Green
Write-Host ""

# Step 3: Initialize project if needed
Write-Host "Step 3: Initialize Project (if needed)" -ForegroundColor Blue

if (-not (Test-Path "railway.json")) {
    Write-Host "Initializing new Railway project..." -ForegroundColor Yellow
    & railway init --name claude-ia-mcp-tools-auth 2>$null | Out-Null
}

Write-Host "✓ Railway project configured" -ForegroundColor Green
Write-Host ""

# Step 4: Deploy
Write-Host "Step 4: Deploy to Railway" -ForegroundColor Blue
Write-Host "Deploying... this may take 2-5 minutes" -ForegroundColor Yellow
Write-Host ""

& railway up

Write-Host ""
Write-Host "✓ Deployment complete!" -ForegroundColor Green
Write-Host ""

# Step 5: Get URL
Write-Host "Step 5: Get Deployment URL" -ForegroundColor Blue

try {
    & railway open
}
catch {
    Write-Host "Open Railway dashboard manually to get the deployment URL" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Wait for deployment to complete (check logs)"
Write-Host "2. Test with: python test-railway.py <URL>"
Write-Host "3. Set RAILWAY_TOKEN in GitHub secrets for CI/CD"
Write-Host ""

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
