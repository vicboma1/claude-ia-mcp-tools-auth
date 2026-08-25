# MCP Auth Server - Complete Flow Test
# Usage: .\test-auth-flow.ps1 [-BaseUrl "http://localhost:5000"] [-Verbose]

param(
    [string]$BaseUrl = "http://localhost:5000",
    [switch]$Verbose
)

# Colors (using Write-Host color parameter)
$ErrorColor = "Red"
$SuccessColor = "Green"
$WarningColor = "Yellow"
$InfoColor = "Cyan"

Write-Host "========================================" -ForegroundColor $InfoColor
Write-Host "  MCP Auth Server - Complete Flow Test" -ForegroundColor $InfoColor
Write-Host "========================================" -ForegroundColor $InfoColor
Write-Host "Base URL: $BaseUrl`n" -ForegroundColor $InfoColor

# Step 1: Start Auth Flow
Write-Host "Step 1: Start Auth Flow" -ForegroundColor $WarningColor
Write-Host "GET /auth/start"

try {
    $Response = Invoke-WebRequest -Uri "$BaseUrl/auth/start" -MaximumRedirection 0 -ErrorAction SilentlyContinue
    $Location = $Response.Headers.Location

    Write-Host "Status: 302 Redirect" -ForegroundColor $SuccessColor
    Write-Host "Location: $Location`n" -ForegroundColor $SuccessColor

    # Extract state token
    if ($Location -match 'state=([^&]*)') {
        $State = $matches[1]
        Write-Host "State Token: $($State.Substring(0, [Math]::Min(40, $State.Length)))...`n" -ForegroundColor $SuccessColor
    }
    else {
        Write-Host "Error: Could not extract state token" -ForegroundColor $ErrorColor
        exit 1
    }
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor $ErrorColor
    exit 1
}

# Step 2: Complete Auth Callback
Write-Host "Step 2: Complete Auth Callback" -ForegroundColor $WarningColor
Write-Host "GET /auth/callback?state=$State"

try {
    $CallbackUrl = "$BaseUrl/auth/callback?state=$State"
    $CallbackResponse = Invoke-WebRequest -Uri $CallbackUrl
    $CallbackBody = $CallbackResponse.Content

    Write-Host "Status: 200 OK" -ForegroundColor $SuccessColor

    # Extract session token
    if ($CallbackBody -match 'user_[a-f0-9]{16}') {
        $SessionToken = $matches[0]
        Write-Host "Session Token: $($SessionToken.Substring(0, [Math]::Min(40, $SessionToken.Length)))...`n" -ForegroundColor $SuccessColor
    }
    else {
        Write-Host "Error: Could not extract session token" -ForegroundColor $ErrorColor
        exit 1
    }
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor $ErrorColor
    exit 1
}

# Step 3: Verify Token with Auth Status
Write-Host "Step 3: Verify Token with Auth Status" -ForegroundColor $WarningColor
Write-Host "GET /auth/status -H 'Authorization: Bearer $SessionToken'"

try {
    $Headers = @{
        "Authorization" = "Bearer $SessionToken"
    }

    $StatusResponse = Invoke-WebRequest -Uri "$BaseUrl/auth/status" -Headers $Headers
    $StatusJson = $StatusResponse.Content | ConvertFrom-Json

    Write-Host "Response:" -ForegroundColor $SuccessColor
    Write-Host ($StatusJson | ConvertTo-Json -Indent 2) -ForegroundColor $SuccessColor
    Write-Host ""
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor $ErrorColor
    exit 1
}

# Step 4: Test Invalid Token
Write-Host "Step 4: Test Invalid Token" -ForegroundColor $WarningColor
Write-Host "GET /auth/status -H 'Authorization: Bearer invalid_token_123'"

try {
    $InvalidHeaders = @{
        "Authorization" = "Bearer invalid_token_123"
    }

    $InvalidResponse = Invoke-WebRequest -Uri "$BaseUrl/auth/status" -Headers $InvalidHeaders
    $InvalidJson = $InvalidResponse.Content | ConvertFrom-Json

    Write-Host "Response:" -ForegroundColor $WarningColor
    Write-Host ($InvalidJson | ConvertTo-Json -Indent 2) -ForegroundColor $WarningColor
    Write-Host ""
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor $ErrorColor
}

# Results Summary
Write-Host "========================================" -ForegroundColor $InfoColor
Write-Host "         TEST RESULTS" -ForegroundColor $InfoColor
Write-Host "========================================" -ForegroundColor $InfoColor
Write-Host "State Token:     $State" -ForegroundColor $SuccessColor
Write-Host "Session Token:   $SessionToken" -ForegroundColor $SuccessColor
Write-Host "Authenticated:   $($StatusJson.authenticated)" -ForegroundColor $SuccessColor
Write-Host "User ID:         $($StatusJson.user_id)" -ForegroundColor $SuccessColor
Write-Host "========================================" -ForegroundColor $InfoColor
Write-Host ""

if ($StatusJson.authenticated -eq $true) {
    Write-Host "SUCCESS: Complete auth flow working correctly!" -ForegroundColor $SuccessColor
    Write-Host ""
    Write-Host "You can now use this token for MCP:" -ForegroundColor $WarningColor
    Write-Host "Authorization: Bearer $SessionToken" -ForegroundColor $InfoColor
}
else {
    Write-Host "FAILED: Authentication verification failed" -ForegroundColor $ErrorColor
    exit 1
}
