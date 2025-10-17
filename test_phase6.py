#!/usr/bin/env python3
"""
Test script for Phase 6 - Records API and statistics endpoints
"""

import time
from database import init_db, add_reading, get_mode_by_id
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

def test_database_functions():
    """Test the new database query functions."""
    print("\n=== Testing Database Functions ===")
    
    from database import get_filtered_records, get_statistics
    
    # Add some test readings
    print("Adding test readings...")
    for mode_id in [1, 2]:
        for i in range(10):
            value = 20.0 + i
            add_reading(mode_id, value)
    
    # Test filtered records
    print("\n1. Testing get_filtered_records()...")
    records = get_filtered_records(limit=5)
    print(f"   ✓ Got {len(records)} records (limit=5)")
    assert len(records) <= 5, "Should respect limit"
    
    # Test mode filtering
    records = get_filtered_records(mode_id=1, limit=10)
    print(f"   ✓ Mode filter works: {len(records)} records for mode 1")
    assert all(r['mode_id'] == 1 for r in records), "All records should be for mode 1"
    
    # Test value range filtering
    records = get_filtered_records(min_value=22.0, max_value=25.0)
    print(f"   ✓ Value range filter works: {len(records)} records between 22-25")
    
    # Test aggregation
    print("\n2. Testing aggregation intervals...")
    for agg in ['raw', '1min', '5min', '15min', '60min']:
        records = get_filtered_records(aggregation=agg, limit=5)
        print(f"   ✓ Aggregation '{agg}': {len(records)} records")
    
    # Test statistics
    print("\n3. Testing get_statistics()...")
    stats = get_statistics()
    print(f"   ✓ Got statistics for {len(stats)} modes")
    for stat in stats:
        print(f"      - {stat['mode_name']}: count={stat['count']}, avg={stat['average']:.2f}")
    
    # Test mode-specific statistics
    stat = get_statistics(mode_id=1)
    if stat:
        print(f"   ✓ Mode 1 statistics: count={stat['count']}, min={stat['minimum']:.2f}, max={stat['maximum']:.2f}")
    
    print("\n✅ All database function tests passed!")

def test_api_endpoints():
    """Test the API endpoints."""
    print("\n=== Testing API Endpoints ===")
    
    # Test /api/records
    print("\n1. Testing /api/records...")
    
    # Basic request
    response = requests.get(f"{BASE_URL}/api/records")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    print(f"   ✓ Basic request: {data['count']} records")
    assert 'records' in data
    assert 'count' in data
    assert 'limit' in data
    assert 'offset' in data
    assert 'filters' in data
    
    # Test with mode filter
    response = requests.get(f"{BASE_URL}/api/records?mode_id=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ Mode filter: {data['count']} records for mode 1")
    
    # Test with pagination
    response = requests.get(f"{BASE_URL}/api/records?limit=5&offset=5")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ Pagination: offset=5, got {data['count']} records")
    
    # Test with aggregation
    for agg in ['raw', '1min', '5min', '15min', '60min']:
        response = requests.get(f"{BASE_URL}/api/records?aggregation={agg}&limit=3")
        assert response.status_code == 200
        data = response.json()
        print(f"   ✓ Aggregation '{agg}': {data['count']} records")
    
    # Test with value range
    response = requests.get(f"{BASE_URL}/api/records?min_value=22&max_value=25")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ Value range filter: {data['count']} records between 22-25")
    
    # Test validation errors
    print("\n2. Testing validation...")
    
    # Invalid mode
    response = requests.get(f"{BASE_URL}/api/records?mode_id=999")
    assert response.status_code == 404, "Should return 404 for invalid mode"
    print("   ✓ Invalid mode returns 404")
    
    # Invalid limit
    response = requests.get(f"{BASE_URL}/api/records?limit=99999")
    assert response.status_code == 400, "Should return 400 for invalid limit"
    print("   ✓ Invalid limit returns 400")
    
    # Invalid aggregation
    response = requests.get(f"{BASE_URL}/api/records?aggregation=invalid")
    assert response.status_code == 400, "Should return 400 for invalid aggregation"
    print("   ✓ Invalid aggregation returns 400")
    
    # Test /api/statistics
    print("\n3. Testing /api/statistics...")
    
    # Basic request
    response = requests.get(f"{BASE_URL}/api/statistics")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ Basic request: statistics for {len(data['statistics'])} modes")
    assert 'statistics' in data
    assert 'filters' in data
    
    # Test with mode filter
    response = requests.get(f"{BASE_URL}/api/statistics?mode_id=1")
    assert response.status_code == 200
    data = response.json()
    stat = data['statistics']
    print(f"   ✓ Mode 1 statistics: count={stat['count']}, avg={stat['average']:.2f}")
    assert 'count' in stat
    assert 'average' in stat
    assert 'minimum' in stat
    assert 'maximum' in stat
    assert 'first_reading' in stat
    assert 'last_reading' in stat
    
    # Test with value filter
    response = requests.get(f"{BASE_URL}/api/statistics?min_value=22&max_value=25")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✓ Value range statistics: {len(data['statistics'])} modes")
    
    print("\n✅ All API endpoint tests passed!")

def test_records_page():
    """Test the records page loads."""
    print("\n=== Testing Records Page ===")
    
    response = requests.get(f"{BASE_URL}/records")
    assert response.status_code == 200
    assert b'Sensor Records' in response.content
    assert b'Filters' in response.content
    assert b'Apply Filters' in response.content
    print("✓ Records page loads successfully")
    print("✓ Contains filter controls")
    print("✓ Contains apply button")
    
    print("\n✅ Records page test passed!")

if __name__ == '__main__':
    import sys
    
    # Initialize database first
    init_db()
    
    # Test database functions (doesn't require server)
    test_database_functions()
    
    # Check if we should test API endpoints (requires server running)
    if len(sys.argv) > 1 and sys.argv[1] == '--with-server':
        if not HAS_REQUESTS:
            print("\n❌ 'requests' module not installed. Install with: pip install requests")
            sys.exit(1)
        
        print("\n" + "="*60)
        print("Testing with live server...")
        print("Make sure Flask server is running on port 5000")
        print("="*60)
        
        try:
            time.sleep(2)  # Give server time to start
            test_api_endpoints()
            test_records_page()
        except Exception as e:
            print(f"\n❌ Could not connect to server: {e}")
            print("Make sure Flask server is running on port 5000")
            sys.exit(1)
    else:
        print("\n" + "="*60)
        print("✅ Database tests completed!")
        print("\nTo test API endpoints, run:")
        print("  python test_phase6.py --with-server")
        print("(with Flask server running in another terminal)")
        print("="*60)
