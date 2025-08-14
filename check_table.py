#!/usr/bin/env python3
"""
Check existing chartink_alerts table structure
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def check_table_structure():
    """Check the existing table structure"""
    try:
        # Try to get a sample record to see the structure
        result = supabase.table('chartink_alerts').select('*').limit(1).execute()
        
        print("✅ Table 'chartink_alerts' exists!")
        print(f"Sample data structure: {result.data}")
        
        # Try to insert a test record to verify schema
        test_data = {
            'scan_name': 'Test Scan',
            'scan_url': 'test-scan',
            'alert_name': 'Test Alert',
            'stocks': ['TEST@100.0'],
            'trigger_prices': [100.0],
            'total_stocks': 1
        }
        
        # This will show us what fields are missing if any
        print("\nTesting insert (will rollback)...")
        insert_result = supabase.table('chartink_alerts').insert(test_data).execute()
        
        if insert_result.data:
            print("✅ Test insert successful!")
            print(f"Inserted record: {insert_result.data[0]}")
            
            # Delete the test record
            record_id = insert_result.data[0]['id']
            supabase.table('chartink_alerts').delete().eq('id', record_id).execute()
            print("🗑️ Test record deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This will help us understand what fields are missing or different")

if __name__ == "__main__":
    check_table_structure()
