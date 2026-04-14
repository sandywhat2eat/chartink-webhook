# 📊 ChartInk Webhook Alert Integration

Complete webhook server to receive ChartInk alerts and store them in Supabase for analysis and tracking. Now with Digital Ocean deployment support!

## 🚀 Deployment Options

### 1. Digital Ocean App (Recommended)
**URL:** `https://starfish-app-khm7p.ondigitalocean.app`
- ✅ Automatic HTTPS
- ✅ Auto-scaling
- ✅ Production-ready
- ✅ Automatic deployments from GitHub

### 2. Self-Hosted (Manual)
Run on your own server with Docker or directly via Python.

## 🚀 Quick Start

### 1. Create Supabase Table
Run the SQL in `create_table.sql` in your Supabase SQL Editor:
```sql
-- Creates chartink_alerts table with all required fields
```

### 2. Start the Webhook Server
```bash
cd /root/chartink
./start_webhook.sh
```

### 3. Configure ChartInk
Use one of these webhook URLs in your ChartInk screener:

**Digital Ocean (Recommended):**
```
https://starfish-app-khm7p.ondigitalocean.app/webhook/chartink
```

**Self-Hosted:**
```
http://YOUR_SERVER_IP:8082/webhook/chartink
```

## 🔄 ChartInk Webhook Format

ChartInk sends alerts in this format:
```json
{
  "scan_name": "Your Scan Name",
  "scan_url": "scan-identifier",
  "alert_name": "Your Alert Name",
  "stocks": "STOCK1,STOCK2,STOCK3",
  "trigger_prices": "100.5,150.25,200.75"
}
```

> **Note:** The webhook now correctly handles both the old format (`STOCK@PRICE,STOCK@PRICE`) and ChartInk's actual format (separate `stocks` and `trigger_prices` fields).

## 📊 Database Schema

**Table:** `chartink_alerts`

| Field | Type | Description |
|-------|------|-------------|
| id | BIGSERIAL | Primary key |
| scan_name | TEXT | Name of the scan that triggered |
| scan_url | TEXT | URL identifier for the scan |
| alert_name | TEXT | Alert description |
| stocks | TEXT[] | Array of stock symbols |
| trigger_prices | NUMERIC[] | Array of corresponding trigger prices |
| total_stocks | INTEGER | Count of stocks in the alert |
| avg_trigger_price | NUMERIC(10,2) | Average trigger price |
| min_trigger_price | NUMERIC(10,2) | Minimum trigger price |
| max_trigger_price | NUMERIC(10,2) | Maximum trigger price |
| created_at | TIMESTAMP | Auto-generated timestamp |
| updated_at | TIMESTAMP | Auto-updated timestamp |

## 🔗 API Endpoints

### Webhook Endpoint
- **URL:** `POST /webhook/chartink`
- **Purpose:** Receives ChartInk webhook alerts
- **Content-Type:** `application/json`

### Health Check
- **URL:** `GET /health`
- **Purpose:** Server health status and database connectivity

### Recent Alerts
- **URL:** `GET /alerts/recent?limit=10`
- **Purpose:** Fetch recent alerts from database

### Test Endpoint
- **URL:** `POST /test`
- **Purpose:** Test with sample data

## 📝 Sample ChartInk Payload

```json
{
  "scan_name": "Short term breakouts",
  "scan_url": "short-term-breakouts",
  "alert_name": "Alert for Short term breakouts",
  "stocks": "SEPOWER@3.75,ASTEC@541.8,EDUCOMP@2.1,KSERASERA@0.2"
}
```

## 🧪 Testing

### 1. Test Webhook (cURL)
```bash
curl -X POST https://starfish-app-khm7p.ondigitalocean.app/webhook/chartink \
  -H "Content-Type: application/json" \
  -d '{
    "scan_name": "Test Alert",
    "scan_url": "test-alert",
    "alert_name": "My Test Alert",
    "stocks": "RELIANCE,TCS,INFY",
    "trigger_prices": "2500.50,3200.75,1450.25"
  }'
```

### 2. Check Recent Alerts
```bash
curl https://starfish-app-khm7p.ondigitalocean.app/alerts/recent
```

### 3. Health Check
```bash
curl https://starfish-app-khm7p.ondigitalocean.app/health
```

### 4. Local Test Suite
```bash
cd /root/chartink
python3 test_webhook.py
```

Tests include:
- ✅ Health check
- ✅ Webhook processing (both formats)
- ✅ Recent alerts retrieval
- ✅ Invalid payload handling

## 🔧 Configuration

### Environment Variables
Create a `.env` file or set in Digital Ocean dashboard:
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
PORT=8080  # For Digital Ocean, use 8080
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Digital Ocean App Spec
- **Build Command:** `pip install -r requirements.txt`
- **Run Command:** `gunicorn --worker-tmp-dir /dev/shm --workers 2 --threads 4 --worker-class=gthread --worker-tmp-dir /dev/shm --bind :8080 webhook_server:app`
- **HTTP Port:** 8080
- **Health Check Path:** `/health`

## 🚀 Deployment Workflow

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```

2. **Digital Ocean**
   - Auto-detects GitHub changes
   - Builds and deploys automatically
   - Updates live in 2-5 minutes

3. **Verify Deployment**
   ```bash
   curl https://starfish-app-khm7p.ondigitalocean.app/health
   ```

## 📈 Data Processing Logic

1. **Parse Stocks String:**
   ```
   "SEPOWER@3.75,ASTEC@541.8" → 
   stocks: ["SEPOWER", "ASTEC"]
   prices: [3.75, 541.8]
   ```

2. **Calculate Metrics:**
   - Total stocks count
   - Average, minimum, maximum trigger prices

3. **Store in Database:**
   - All data stored in single row per alert
   - Stocks grouped together for easy analysis

## 🚀 Production Deployment

For production, use gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8082 webhook_server:app
```

## 📊 Usage Examples

### Query Recent Breakouts
```sql
SELECT scan_name, total_stocks, avg_trigger_price, created_at 
FROM chartink_alerts 
WHERE scan_name LIKE '%breakout%' 
ORDER BY created_at DESC 
LIMIT 10;
```

### Find Most Active Scans
```sql
SELECT scan_name, COUNT(*) as alert_count, AVG(total_stocks) as avg_stocks
FROM chartink_alerts 
GROUP BY scan_name 
ORDER BY alert_count DESC;
```

## 🔍 Monitoring

Logs are written to:
- `/root/chartink/webhook.log`
- Console output

## 🛡️ Security Notes

- Server runs on port 8082
- Uses Supabase service role key for database access
- Validates all incoming payloads
- Handles malformed data gracefully

## 📞 Support

The webhook server is ready for production use with:
- ✅ Comprehensive error handling
- ✅ Input validation
- ✅ Database connection management
- ✅ Logging and monitoring
- ✅ Test suite for verification
