# Deploy to Railway - Step by Step Guide

## Prerequisites

- Railway account: https://railway.app
- GitHub account connected to Railway
- Repository: vicboma1/claude-ia-mcp-tools-auth

## Option 1: Deploy via Railway Web Dashboard (Easiest)

### Step 1: Go to Railway Dashboard

1. Visit https://railway.app
2. Log in with your GitHub account
3. Click "New Project"

### Step 2: Select GitHub Repository

1. Click "Deploy from GitHub repo"
2. Search for: `claude-ia-mcp-tools-auth`
3. Select the repository
4. Click "Deploy"

### Step 3: Configure Environment

Railway will automatically:
- Detect the Dockerfile
- Build the Docker image
- Deploy the container

The deployment will be visible on the dashboard with:
- Service name: `mcp-auth-server`
- Domain: `claude-ia-mcp-tools-auth-staging.up.railway.app`
- Status: Running ✓

### Step 4: Verify Deployment

Once deployed, test with:

```bash
# Test home page
curl https://claude-ia-mcp-tools-auth-staging.up.railway.app/

# Test auth flow
python test-railway.py https://claude-ia-mcp-tools-auth-staging.up.railway.app
```

---

## Option 2: Deploy via Railway CLI

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

Or use:

```bash
curl -fsSL https://railway.app/install.sh | bash
```

### Step 2: Login to Railway

```bash
railway login
```

This opens a browser to authenticate with GitHub.

### Step 3: Initialize Project

```bash
cd claude-ia-mcp-tools-auth
railway init
```

Select:
- Create new project
- Name: `claude-ia-mcp-tools-auth`
- Link to GitHub repo: Yes

### Step 4: Deploy

```bash
railway up
```

This will:
- Build Docker image
- Push to Railway
- Deploy container
- Show you the deployment URL

### Step 5: Get Your URL

```bash
railway open
```

Or check the Railway dashboard.

---

## Option 3: Automatic Deployment via GitHub Actions

Once deployed, every push to `main` triggers automatic deployment:

### Step 1: Set GitHub Secret

In your GitHub repository:

1. Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `RAILWAY_TOKEN`
4. Value: Get from Railway → Account → API Tokens
5. Click "Add secret"

### Step 2: Push to Main

```bash
git push origin main
```

### Step 3: Watch Deployment

1. Go to your repository
2. Actions tab
3. Select "Deploy to Railway" workflow
4. Watch progress

---

## Configuration

### Environment Variables

Railway automatically sets from `railway.json`:

```json
{
  "PORT": 5000,
  "FLASK_ENV": "production",
  "FLASK_SECRET_KEY": "auto-generated"
}
```

You can override in Railway Dashboard → Variables

### Health Check

Railway pings every 30 seconds:

```
GET / → 200 OK
```

If health check fails, deployment will restart.

---

## Testing After Deployment

### Quick Test

```bash
curl https://claude-ia-mcp-tools-auth-staging.up.railway.app/
```

### Full Auth Flow Test

```bash
# Option 1: Python
python test-railway.py https://claude-ia-mcp-tools-auth-staging.up.railway.app

# Option 2: Bash
bash test-railway.sh https://claude-ia-mcp-tools-auth-staging.up.railway.app

# Option 3: PowerShell
powershell -File test-railway.ps1 -RailwayUrl "https://claude-ia-mcp-tools-auth-staging.up.railway.app"
```

---

## Logs and Monitoring

### View Logs

In Railway Dashboard:
1. Select your project
2. Select "mcp-auth-server"
3. Click "Logs"
4. See real-time logs

Or via CLI:

```bash
railway logs --follow
```

### Monitor Status

```bash
railway status
```

Shows:
- Deployment status
- Container health
- Resource usage

---

## Troubleshooting

### Issue: Deployment Failed

Check logs:
```bash
railway logs --tail 50
```

Common causes:
- Missing dependencies
- Port conflict
- Environment variable missing
- Dockerfile issue

### Issue: Health Check Failing

Verify endpoint:
```bash
curl https://your-app.up.railway.app/
```

Should return 200 OK with HTML.

### Issue: Container Crashes on Startup

Check:
1. Flask startup logs
2. Port configuration
3. Python version compatibility

---

## Production Deployment

For production (`*.up.railway.app` domain):

1. Update FLASK_SECRET_KEY to production value
2. Set FLASK_ENV = production
3. Configure custom domain if needed
4. Set up monitoring and alerts

---

## URLs After Deployment

- **Auth Server**: https://claude-ia-mcp-tools-auth-staging.up.railway.app
- **Test Script**: Use `test-railway.py` with the above URL
- **Status Endpoint**: `/auth/status`
- **Logs**: Railway Dashboard → Logs

---

## Next Steps

1. ✓ Deploy via web dashboard
2. ✓ Run test-railway.py
3. ✓ Verify auth flow works
4. ✓ Setup RAILWAY_TOKEN secret for CI/CD
5. ✓ Monitor logs regularly
