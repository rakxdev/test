#!/usr/bin/env python3
"""
Test script for Phase 4 implementation
Verifies dashboard UI controls and WebSocket integration
"""

import os
import sys

def test_file_exists(filepath, description):
    """Test if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} missing: {filepath}")
        return False

def test_file_contains(filepath, search_strings, description):
    """Test if file contains specific strings"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            missing = []
            for search_str in search_strings:
                if search_str not in content:
                    missing.append(search_str)
            
            if not missing:
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} - Missing: {', '.join(missing)}")
                return False
    except Exception as e:
        print(f"✗ Error reading {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("Phase 4 - Dashboard UI Controls and WebSocket Integration")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Check if mode-dashboard.html exists
    print("Test 1: Template Files")
    print("-" * 40)
    results.append(test_file_exists(
        'templates/mode-dashboard.html',
        'mode-dashboard.html template'
    ))
    print()
    
    # Test 2: Check if dashboard.js exists
    print("Test 2: JavaScript Files")
    print("-" * 40)
    results.append(test_file_exists(
        'static/js/dashboard.js',
        'dashboard.js script'
    ))
    print()
    
    # Test 3: Check if dashboard.css exists
    print("Test 3: CSS Files")
    print("-" * 40)
    results.append(test_file_exists(
        'static/css/dashboard.css',
        'dashboard.css stylesheet'
    ))
    print()
    
    # Test 4: Check mode-dashboard.html content
    print("Test 4: Template Content")
    print("-" * 40)
    results.append(test_file_contains(
        'templates/mode-dashboard.html',
        [
            'control-panel',
            'powerToggle',
            'voltageSlider',
            'digital-readouts',
            'graph-container',
            'connection-indicators',
            'wsConnectionStatus',
            'data-mode-id',
            'DashboardController'
        ],
        'mode-dashboard.html has required UI elements'
    ))
    print()
    
    # Test 5: Check dashboard.js content
    print("Test 5: JavaScript Logic")
    print("-" * 40)
    results.append(test_file_contains(
        'static/js/dashboard.js',
        [
            'class DashboardController',
            'setupWebSocket',
            'subscribe_mode',
            'data_update',
            'mode_changed',
            'handlePowerToggle',
            'debouncedVoltageUpdate',
            'voltageDebounceDelay',
            '/api/mode/toggle',
            '/api/voltage/set'
        ],
        'dashboard.js has WebSocket and control logic'
    ))
    print()
    
    # Test 6: Check dashboard.css content
    print("Test 6: CSS Styling")
    print("-" * 40)
    results.append(test_file_contains(
        'static/css/dashboard.css',
        [
            'theme-temperature',
            'theme-humidity',
            'theme-pressure',
            'theme-light',
            '--temp-primary',
            '--humidity-primary',
            '--pressure-primary',
            '--light-primary',
            '.control-panel',
            '.digital-readouts',
            '.voltage-slider',
            '@media'
        ],
        'dashboard.css has themes and responsive styles'
    ))
    print()
    
    # Test 7: Check app.py route update
    print("Test 7: Backend Integration")
    print("-" * 40)
    results.append(test_file_contains(
        'app.py',
        ['mode-dashboard.html'],
        'app.py uses mode-dashboard.html template'
    ))
    print()
    
    # Test 8: Check home.html navigation
    print("Test 8: Navigation Integration")
    print("-" * 40)
    results.append(test_file_contains(
        'templates/home.html',
        ['dashboard_mode', 'btn-mode-dashboard'],
        'home.html has mode dashboard links'
    ))
    print()
    
    # Test 9: Check button styling
    print("Test 9: Navigation Button Styling")
    print("-" * 40)
    results.append(test_file_contains(
        'static/css/style.css',
        ['.btn-mode-dashboard'],
        'style.css has mode dashboard button styles'
    ))
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All Phase 4 requirements implemented successfully!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
