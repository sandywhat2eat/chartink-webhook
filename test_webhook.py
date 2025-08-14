#!/usr/bin/env python3
"""
Test script for ChartInk Webhook Server
"""

import requests
import json
import time

# Server URL (adjust if running on different host/port)
BASE_URL = "http://localhost:8082"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_sample_webhook():
    """Test webhook with sample data"""
    print("\nTesting sample webhook...")
    
    sample_payload = {
        "scan_name": "Short term breakouts",
        "scan_url": "short-term-breakouts", 
        "alert_name": "Alert for Short term breakouts",
        "stocks": "SEPOWER@3.75,ASTEC@541.8,EDUCOMP@2.1,KSERASERA@0.2"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/chartink",
            json=sample_payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Webhook test failed: {e}")
        return False

def test_built_in_test_endpoint():
    """Test the built-in test endpoint"""
    print("\nTesting built-in test endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/test")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Built-in test failed: {e}")
        return False

def test_recent_alerts():
    """Test recent alerts endpoint"""
    print("\nTesting recent alerts...")
    try:
        response = requests.get(f"{BASE_URL}/alerts/recent?limit=5")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Recent alerts test failed: {e}")
        return False

def test_invalid_payload():
    """Test webhook with invalid payload"""
    print("\nTesting invalid payload...")
    
    invalid_payload = {
        "scan_name": "Test scan",
        # Missing required fields
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/chartink",
            json=invalid_payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400  # Should return error
    except Exception as e:
        print(f"Invalid payload test failed: {e}")
        return False

if __name__ == "__main__":
    print("ChartInk Webhook Server Test Suite")
    print("=" * 40)
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health_check),
        ("Sample Webhook", test_sample_webhook),
        ("Built-in Test", test_built_in_test_endpoint),
        ("Recent Alerts", test_recent_alerts),
        ("Invalid Payload", test_invalid_payload)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        result = test_func()
        results.append((test_name, result))
        print(f"{test_name}: {'PASS' if result else 'FAIL'}")
    
    print(f"\n{'='*40}")
    print("Test Results Summary:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
