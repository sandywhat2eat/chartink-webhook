#!/usr/bin/env python3
"""
ChartInk Webhook Debug Tool
Real-time monitoring and testing for ChartInk webhook issues
"""

import requests
import json
import time
import threading
from datetime import datetime

# Server URL
BASE_URL = "http://159.89.175.215:8082"

def monitor_logs():
    """Monitor webhook logs in real-time"""
    print("🔍 Monitoring webhook logs (Press Ctrl+C to stop)...")
    print("=" * 60)
    
    try:
        import subprocess
        # Follow the log file
        process = subprocess.Popen(
            ['tail', '-f', '/root/chartink/webhook.log'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] {line.strip()}")
                
    except KeyboardInterrupt:
        print("\n📊 Log monitoring stopped")
    except Exception as e:
        print(f"❌ Error monitoring logs: {e}")

def test_webhook_connectivity():
    """Test all webhook endpoints"""
    print("🧪 Testing Webhook Connectivity")
    print("=" * 40)
    
    tests = [
        ("Health Check", "GET", "/health", None),
        ("Recent Alerts", "GET", "/alerts/recent?limit=3", None),
        ("Sample Webhook", "POST", "/webhook/chartink", {
            "scan_name": "Debug Test",
            "scan_url": "debug-test",
            "alert_name": "Debug Alert Test",
            "stocks": "TESTSTOCK@100.50,SAMPLE@200.75"
        })
    ]
    
    for test_name, method, endpoint, payload in tests:
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=payload, timeout=10)
            
            status = "✅ PASS" if response.status_code < 400 else "❌ FAIL"
            print(f"{status} {test_name}: {response.status_code}")
            
            if response.status_code < 400:
                try:
                    data = response.json()
                    if test_name == "Recent Alerts":
                        count = data.get('count', 0)
                        print(f"    📊 Found {count} recent alerts")
                    elif test_name == "Sample Webhook":
                        print(f"    💾 Alert stored with ID: {data.get('data', {}).get('id', 'N/A')}")
                except:
                    print(f"    📄 Response: {response.text[:100]}...")
            else:
                print(f"    ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ FAIL {test_name}: {e}")
        
        print()

def check_database_records():
    """Check recent database records"""
    print("📊 Checking Database Records")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/alerts/recent?limit=10")
        if response.status_code == 200:
            data = response.json()
            alerts = data.get('alerts', [])
            
            print(f"Total recent alerts: {len(alerts)}")
            print()
            
            for i, alert in enumerate(alerts[:5], 1):
                created_at = alert.get('created_at', 'N/A')
                scan_name = alert.get('scan_name', 'N/A')
                total_stocks = alert.get('total_stocks', 0)
                source = alert.get('source_platform', 'N/A')
                
                print(f"{i}. {scan_name}")
                print(f"   📅 Created: {created_at}")
                print(f"   📈 Stocks: {total_stocks}")
                print(f"   🔗 Source: {source}")
                print()
        else:
            print(f"❌ Failed to fetch records: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def simulate_chartink_webhook():
    """Simulate what ChartInk should send"""
    print("🎯 Simulating ChartInk Webhook")
    print("=" * 35)
    
    # This is the exact format ChartInk sends
    chartink_payload = {
        "scan_name": "Short term breakouts",
        "scan_url": "short-term-breakouts",
        "alert_name": "Alert for Short term breakouts",
        "stocks": "NAUKRI@1378.4,MANAPPURAM@265.7"  # From your screenshot
    }
    
    print("📤 Sending ChartInk-style payload:")
    print(json.dumps(chartink_payload, indent=2))
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/chartink",
            json=chartink_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Webhook simulation successful!")
        else:
            print("❌ Webhook simulation failed!")
            
    except Exception as e:
        print(f"❌ Error simulating webhook: {e}")

def main():
    """Main debug function"""
    print("🚀 ChartInk Webhook Debug Tool")
    print("=" * 50)
    print(f"🔗 Server URL: {BASE_URL}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    while True:
        print("\nChoose an option:")
        print("1. Test webhook connectivity")
        print("2. Check database records")
        print("3. Simulate ChartInk webhook")
        print("4. Monitor logs in real-time")
        print("5. Run all tests")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            test_webhook_connectivity()
        elif choice == "2":
            check_database_records()
        elif choice == "3":
            simulate_chartink_webhook()
        elif choice == "4":
            monitor_logs()
        elif choice == "5":
            test_webhook_connectivity()
            check_database_records()
            simulate_chartink_webhook()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
