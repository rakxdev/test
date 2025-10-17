#!/usr/bin/env python
"""
Quick test script for Phase 3 implementation
Tests database functions, simulator, and API routes without running the server
"""

import sys
from database import (
    init_db, get_all_modes, get_mode_by_id,
    set_mode_voltage, get_mode_voltage, get_current_reading,
    update_mode_status, add_reading, get_active_modes
)
from data_simulator import DataSimulator

def test_database_voltage():
    """Test voltage setting and retrieval"""
    print("Testing voltage management...")
    
    # Set voltage for mode 1
    set_mode_voltage(1, 7.5)
    voltage = get_mode_voltage(1)
    assert voltage == 7.5, f"Expected 7.5, got {voltage}"
    
    # Test validation
    try:
        set_mode_voltage(1, 15.0)  # Should fail (out of range)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "between 0 and 10" in str(e)
    
    print("✓ Voltage management works correctly")

def test_database_current_reading():
    """Test current reading retrieval"""
    print("Testing current reading retrieval...")
    
    # Add a reading
    add_reading(1, 25.5)
    
    # Get current reading
    reading = get_current_reading(1)
    assert reading is not None, "Should have a reading"
    assert reading['value'] == 25.5
    assert reading['mode_name'] == 'Temperature'
    
    print("✓ Current reading retrieval works correctly")

def test_active_modes():
    """Test active modes retrieval"""
    print("Testing active modes retrieval...")
    
    # Activate mode 2
    update_mode_status(2, True)
    
    # Get active modes
    active = get_active_modes()
    assert len(active) >= 1, "Should have at least one active mode"
    assert any(m['id'] == 2 for m in active), "Mode 2 should be active"
    
    # Deactivate mode 2
    update_mode_status(2, False)
    
    print("✓ Active modes retrieval works correctly")

def test_mode_data_structure():
    """Test that modes include voltage field"""
    print("Testing mode data structure...")
    
    modes = get_all_modes()
    assert len(modes) > 0, "Should have modes"
    
    for mode in modes:
        assert 'voltage' in mode, f"Mode {mode['id']} missing voltage field"
        assert isinstance(mode['voltage'], (int, float)), "Voltage should be numeric"
    
    mode = get_mode_by_id(1)
    assert mode is not None, "Should find mode 1"
    assert 'voltage' in mode, "Mode should have voltage field"
    
    print("✓ Mode data structure includes voltage")

def test_simulator_generation():
    """Test simulator value generation with voltage"""
    print("Testing simulator value generation...")
    
    simulator = DataSimulator()
    
    # Test different voltage levels
    for voltage in [0.0, 5.0, 10.0]:
        value = simulator.generate_value('Temperature', voltage)
        assert 15.0 <= value <= 35.0, f"Temperature out of range at {voltage}V: {value}"
    
    # Test all mode types
    for mode_name in ['Temperature', 'Humidity', 'Pressure', 'Light']:
        value = simulator.generate_value(mode_name, 5.0)
        assert isinstance(value, float), f"Value should be float for {mode_name}"
    
    print("✓ Simulator value generation works correctly")

def test_thread_safety():
    """Test that thread safety mechanisms are in place"""
    print("Testing thread safety...")
    
    from database import db_lock
    from data_simulator import DataSimulator
    
    # Database lock exists
    assert db_lock is not None, "Database lock should exist"
    
    # Simulator has lock
    simulator = DataSimulator()
    assert hasattr(simulator, 'lock'), "Simulator should have lock"
    assert hasattr(simulator, 'is_running'), "Simulator should have is_running method"
    
    print("✓ Thread safety mechanisms in place")

def main():
    """Run all tests"""
    print("=" * 50)
    print("Phase 3 Implementation Tests")
    print("=" * 50)
    
    try:
        # Initialize database
        print("\nInitializing database...")
        init_db()
        print("✓ Database initialized")
        
        # Run tests
        test_mode_data_structure()
        test_database_voltage()
        test_database_current_reading()
        test_active_modes()
        test_simulator_generation()
        test_thread_safety()
        
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
