"""
Test script to verify Supabase connection, authentication, and table schemas.
Run: python tests/test_supabase_connection.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import settings

def test_connection():
    print("=" * 60)
    print("[TEST] Testing Supabase Connection for Gujarati Kisaan Mitra AI")
    print("=" * 60)

    url = settings.SUPABASE_URL
    key = settings.SUPABASE_ANON_KEY

    print(f"Supabase URL : {url}")
    if not key or "PASTE_" in key:
        print("[ERROR] SUPABASE_ANON_KEY is not set yet in .streamlit/secrets.toml!")
        print("Please paste your actual anon public key into .streamlit/secrets.toml and retry.")
        return False

    print(f"Anon Key     : {key[:12]}...{key[-6:] if len(key) > 18 else ''}")

    try:
        from supabase import create_client
        client = create_client(url, key)
        print("[OK] Supabase client initialized.")

        # Test querying tables created by schema.sql
        tables_to_check = ["document_chunks", "mandi_prices", "conversation_logs", "districts"]
        all_passed = True

        for table in tables_to_check:
            try:
                res = client.table(table).select("*", count="exact").limit(1).execute()
                print(f"  [OK] Table '{table}' is connected & accessible (Rows: {res.count if hasattr(res, 'count') else 0})")
            except Exception as e:
                print(f"  [FAIL] Table '{table}' check failed: {e}")
                all_passed = False

        if all_passed:
            print("\n*** SUCCESS! Your Supabase database is fully connected and ready to use! ***")
            return True
        else:
            print("\n[WARNING] Some tables could not be accessed. Make sure you ran db/schema.sql in the Supabase SQL Editor.")
            return False

    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
