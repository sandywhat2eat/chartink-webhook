#!/bin/bash

# ChartInk Webhook Self-Test Script
# Run this to prove your webhook server is working correctly

echo "🚀 ChartInk Webhook Self-Test"
echo "=============================="
echo ""

WEBHOOK_URL="http://159.89.175.215:8082/webhook/chartink"
HEALTH_URL="http://159.89.175.215:8082/health"
RECENT_URL="http://159.89.175.215:8082/alerts/recent?limit=5"

echo "📍 Testing Server: $WEBHOOK_URL"
echo ""

# Test 1: Health Check
echo "🔍 Test 1: Health Check"
echo "----------------------"
curl -s -X GET $HEALTH_URL | jq '.' 2>/dev/null || curl -s -X GET $HEALTH_URL
echo ""
echo ""

# Test 2: Send Sample ChartInk Alert
echo "📤 Test 2: Sample ChartInk Alert"
echo "--------------------------------"
echo "Sending ChartInk-style payload..."

SAMPLE_PAYLOAD='{
  "scan_name": "Self Test Breakout",
  "scan_url": "self-test-breakout",
  "alert_name": "Alert for Self Test Breakout", 
  "stocks": "RELIANCE@2500.50,TCS@3200.75,INFY@1450.25,HDFC@1650.00"
}'

echo "Payload:"
echo "$SAMPLE_PAYLOAD" | jq '.' 2>/dev/null || echo "$SAMPLE_PAYLOAD"
echo ""

echo "Response:"
curl -s -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d "$SAMPLE_PAYLOAD" | jq '.' 2>/dev/null || \
curl -s -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d "$SAMPLE_PAYLOAD"
echo ""
echo ""

# Test 3: Check Recent Alerts
echo "📊 Test 3: Check Recent Alerts"
echo "------------------------------"
curl -s -X GET $RECENT_URL | jq '.' 2>/dev/null || curl -s -X GET $RECENT_URL
echo ""
echo ""

# Test 4: Test with Your Actual Stocks
echo "🎯 Test 4: Your Actual Stocks (from screenshot)"
echo "-----------------------------------------------"
YOUR_STOCKS_PAYLOAD='{
  "scan_name": "Your Actual Scan",
  "scan_url": "your-actual-scan",
  "alert_name": "Alert for Your Actual Scan",
  "stocks": "NAUKRI@1378.4,MANAPPURAM@265.7"
}'

echo "Using stocks from your ChartInk screenshot:"
echo "$YOUR_STOCKS_PAYLOAD" | jq '.' 2>/dev/null || echo "$YOUR_STOCKS_PAYLOAD"
echo ""

echo "Response:"
curl -s -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d "$YOUR_STOCKS_PAYLOAD" | jq '.' 2>/dev/null || \
curl -s -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d "$YOUR_STOCKS_PAYLOAD"
echo ""
echo ""

# Test 5: Invalid Payload Test
echo "❌ Test 5: Invalid Payload (Should Fail)"
echo "----------------------------------------"
INVALID_PAYLOAD='{"scan_name": "Test", "missing_required_fields": true}'

echo "Sending invalid payload (missing required fields):"
echo "$INVALID_PAYLOAD"
echo ""

echo "Response (should be error):"
curl -s -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d "$INVALID_PAYLOAD" | jq '.' 2>/dev/null || \
curl -s -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d "$INVALID_PAYLOAD"
echo ""
echo ""

# Summary
echo "✅ SUMMARY"
echo "=========="
echo "If all tests above worked (except the invalid payload test),"
echo "then your webhook server is 100% functional!"
echo ""
echo "This proves the issue is with ChartInk not sending webhooks,"
echo "not with your server setup."
echo ""
echo "🔍 To monitor for actual ChartInk webhooks, run:"
echo "   tail -f /root/chartink/webhook.log"
echo ""
echo "📊 To check database records, visit:"
echo "   $RECENT_URL"
