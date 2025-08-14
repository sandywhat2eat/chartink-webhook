# ChartInk Webhook Alert Integration

Complete webhook server to receive ChartInk alerts and store them in Supabase for analysis and tracking.

## 🚀 Digital Ocean App Deployment

This project is ready for deployment on Digital Ocean App Platform with automatic scaling and HTTPS.

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
Use this webhook URL in your ChartInk screener:
```
http://YOUR_SERVER_IP:8082/webhook/chartink
```

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

Run the test suite:
```bash
cd /root/chartink
python3 test_webhook.py
```

Tests include:
- ✅ Health check
- ✅ Sample webhook processing
- ✅ Built-in test endpoint
- ✅ Recent alerts retrieval
- ✅ Invalid payload handling

## 🔧 Configuration

The server uses environment variables from `/root/.env`:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

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
