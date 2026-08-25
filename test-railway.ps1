# MCP Auth Server - Complete Flow Test for Railway
# Usage: .\test-railway.ps1 -RailwayUrl "https://claude-ia-mcp-tools-auth-staging.up.railway.app"

param(
    [string]$RailwayUrl = "https://claude-ia-mcp-tools-auth-staging.up.railway.app"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Railway Auth Server - Complete Test" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "URL: $RailwayUrl" -ForegroundColor Green
Write-Host ""

# Step 1: Start auth flow and extract state
Write-Host "Step 1: Start Auth Flow" -ForegroundColor Yellow
Write-Host "Command: curl -L $RailwayUrl/auth/start" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "$RailwayUrl/auth/start" -MaximumRedirection 0 -ErrorAction SilentlyContinue
    $redirect = $response.Headers.Location

    Write-Host "Redirect URL: $redirect" -ForegroundColor Green

    # Extract state token
    if ($redirect -match 'state=([^&]*)') {
        $state = $matches[1]
        Write-Host "Extracted State: $state" -ForegroundColor Green
        Write-Host ""
    }
    else {
        Write-Host "ERROR: Could not extract state token" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Complete auth callback and extract token
Write-Host "Step 2: Complete Auth Callback" -ForegroundColor Yellow
$callbackUrl = "$RailwayUrl/auth/callback?state=$state"
Write-Host "Command: curl $callbackUrl" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri $callbackUrl
    $responseText = $response.Content

    # Extract token from HTML token-box
    if ($responseText -match 'class="token-box">([A-Za-z0-9_-]+)</div>') {
        $sessionToken = $matches[1]
        Write-Host "Extracted Session Token: $sessionToken" -ForegroundColor Green
        Write-Host ""
    }
    else {
        Write-Host "ERROR: Could not extract session token" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Verify token
Write-Host "Step 3: Verify Token" -ForegroundColor Yellow
Write-Host "Command: curl -H 'Authorization: Bearer $sessionToken' $RailwayUrl/auth/status" -ForegroundColor Gray
Write-Host ""

try {
    $headers = @{
        "Authorization" = "Bearer $sessionToken"
    }
    $response = Invoke-WebRequest -Uri "$RailwayUrl/auth/status" -Headers $headers
    $statusResponse = $response.Content
    Write-Host "Response: $statusResponse" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Test invalid token
Write-Host "Step 4: Test Invalid Token" -ForegroundColor Yellow
Write-Host "Command: curl -H 'Authorization: Bearer invalid_token' $RailwayUrl/auth/status" -ForegroundColor Gray
Write-Host ""

try {
    $headers = @{
        "Authorization" = "Bearer invalid_token_123"
    }
    $response = Invoke-WebRequest -Uri "$RailwayUrl/auth/status" -Headers $headers
    $invalidResponse = $response.Content
    Write-Host "Response: $invalidResponse" -ForegroundColor Yellow
    Write-Host ""
}
catch {
    Write-Host "Response: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
}

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "         TEST SUMMARY" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "State Token:     $state" -ForegroundColor Green
Write-Host "Session Token:   $sessionToken" -ForegroundColor Green
Write-Host ""

if ($statusResponse -like '*"authenticated": true*') {
    Write-Host "SUCCESS: Auth flow working on Railway!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now use this token:" -ForegroundColor Yellow
    Write-Host "  Authorization: Bearer $sessionToken" -ForegroundColor Cyan
}
else {
    Write-Host "FAILED: Authentication not working" -ForegroundColor Red
    exit 1
}
