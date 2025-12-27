"""
Test Firestore Connection

Simple script to verify Firestore setup is working correctly.
Run this after setting up credentials to ensure everything is configured properly.

Usage:
    python tests/test_firestore_connection.py

Testing Pattern: Environment-based Collection Isolation
- Tests write to 'recommendations_test' collection (not production)
- Test data is cleaned up after each run
- Production data remains untouched

Teaching Note: This pattern prevents test pollution in production.
In larger systems, you might use Firebase Local Emulator instead.
"""

import os
import sys
from datetime import datetime

# Add parent directory to path so we can import from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT: Set test collection BEFORE importing recommendation_db
# This ensures the singleton is initialized with the test collection
os.environ['FIRESTORE_COLLECTION'] = 'recommendations_test'

from dotenv import load_dotenv
load_dotenv()

# Now import - the singleton will use 'recommendations_test'
from recommendation_db import get_db, save_recommendation, get_recently_visited_venues

# Track document IDs for cleanup
_test_doc_ids = []


def test_connection():
    """Test basic Firestore connection"""
    print("\n" + "="*60)
    print("🧪 Testing Firestore Connection")
    print("="*60 + "\n")

    try:
        db = get_db()
        print("✅ Successfully connected to Firestore!")
        print(f"📍 Project: {db.db.project}")
        print(f"📁 Collection: {db.collection_name}")

        # Verify we're using test collection
        if db.collection_name != 'recommendations_test':
            print(f"⚠️  WARNING: Using '{db.collection_name}' instead of test collection!")
            return False

        print("✅ Using test collection (production data protected)")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Tip: Make sure FIRESTORE_PROJECT_ID is set in .env")
        print("💡 Tip: Run 'gcloud auth application-default login' for ADC")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Tip: Check that your credentials are valid")
        return False


def test_write_operation():
    """Test writing a recommendation"""
    global _test_doc_ids

    print("\n" + "="*60)
    print("🧪 Testing Write Operation")
    print("="*60 + "\n")

    try:
        doc_id = save_recommendation(
            raw_suggestions="[TEST] Test recommendation - Test Venue A, Test Venue B",
            venues_mentioned=["Test Venue A", "Test Venue B"],
            events_mentioned=["Test Event 1", "Test Event 2"],
            weather_conditions="Test conditions"
        )
        _test_doc_ids.append(doc_id)  # Track for cleanup
        print(f"✅ Successfully saved test recommendation!")
        print(f"📄 Document ID: {doc_id}")
        return True
    except Exception as e:
        print(f"❌ Write operation failed: {e}")
        return False


def test_read_operation():
    """Test reading recommendations"""
    print("\n" + "="*60)
    print("🧪 Testing Read Operation")
    print("="*60 + "\n")

    try:
        venues = get_recently_visited_venues(days=30)
        print(f"✅ Successfully retrieved recent venues!")
        print(f"🏛️  Found {len(venues)} unique venues:")
        for venue in venues:
            print(f"   - {venue}")
        return True
    except Exception as e:
        print(f"❌ Read operation failed: {e}")
        return False


def cleanup_test_data():
    """
    Clean up test documents created during this test run.

    Pattern: Test Cleanup
    - Delete documents created during tests
    - Ensures test collection doesn't grow unbounded
    - Run at end of test suite
    """
    global _test_doc_ids

    print("\n" + "="*60)
    print("🧹 Cleaning Up Test Data")
    print("="*60 + "\n")

    if not _test_doc_ids:
        print("ℹ️  No test documents to clean up")
        return

    db = get_db()
    cleaned = 0
    for doc_id in _test_doc_ids:
        try:
            db.db.collection(db.collection_name).document(doc_id).delete()
            cleaned += 1
            print(f"🗑️  Deleted: {doc_id}")
        except Exception as e:
            print(f"⚠️  Failed to delete {doc_id}: {e}")

    print(f"\n✅ Cleaned up {cleaned}/{len(_test_doc_ids)} test documents")
    _test_doc_ids.clear()


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 Firestore Setup Verification")
    print("="*60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Using collection: recommendations_test (isolated from production)")

    results = {
        "Connection": test_connection(),
        "Write": test_write_operation(),
        "Read": test_read_operation()
    }

    # Always clean up, even if tests fail
    cleanup_test_data()

    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s} {status}")
        if not passed:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 All tests passed! Firestore is ready to use.")
        print("\n💡 Next step: Run 'python family_manager.py' to test the full pipeline")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        print("\n💡 Tip: Check docs/FIRESTORE_SETUP.md for troubleshooting")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
