# Digital Ocean App Platform Deployment Guide

## 📋 Prerequisites

1. **GitHub Account** with repository access
2. **Digital Ocean Account** with App Platform access
3. **Supabase Project** with `chartink_alerts` table

## 🚀 Deployment Steps

### Step 1: Push to GitHub

```bash
cd /root/chartink
git init
git add .
git commit -m "Initial ChartInk webhook server"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/chartink-webhook.git
git push -u origin main
```

### Step 2: Create Digital Ocean App

1. **Login to Digital Ocean**
2. **Go to App Platform** → Create App
3. **Connect GitHub Repository**: `your-username/chartink-webhook`
4. **Configure Service**:
   - **Name**: `chartink-webhook`
   - **Source Directory**: `/` (root)
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `gunicorn --bind 0.0.0.0:$PORT webhook_server:app`
   - **Port**: `8080`

### Step 3: Environment Variables

Add these environment variables in Digital Ocean App settings:

```
SUPABASE_URL=https://aisqbjjpdztnuerniefl.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
PORT=8080
```

### Step 4: Deploy

1. **Review Configuration**
2. **Click "Create Resources"**
3. **Wait for deployment** (5-10 minutes)
4. **Get your app URL**: `https://your-app-name.ondigitalocean.app`

## 🔗 Webhook URL

Your new webhook URL will be:
```
https://your-app-name.ondigitalocean.app/webhook/chartink
```

## ✅ Testing

Test the deployed webhook:
```bash
curl -X POST https://your-app-name.ondigitalocean.app/webhook/chartink \
  -H "Content-Type: application/json" \
  -d '{
    "scan_name": "Digital Ocean Test",
    "scan_url": "do-test",
    "alert_name": "DO Test Alert",
    "stocks": "TEST@100.50,SAMPLE@200.75"
  }'
```

## 🎯 Benefits of Digital Ocean App

- ✅ **HTTPS by default** (more secure than HTTP)
- ✅ **Auto-scaling** based on traffic
- ✅ **Automatic deployments** from GitHub
- ✅ **Professional domain** (*.ondigitalocean.app)
- ✅ **Built-in monitoring** and logs
- ✅ **Zero server management**

## 🔍 Monitoring

- **App Logs**: Available in Digital Ocean dashboard
- **Health Check**: `https://your-app-name.ondigitalocean.app/health`
- **Recent Alerts**: `https://your-app-name.ondigitalocean.app/alerts/recent`

## 💰 Cost

- **Basic plan**: ~$5/month
- **Includes**: 512MB RAM, 1 vCPU, HTTPS, custom domains
- **Free tier**: Available for testing (limited resources)
