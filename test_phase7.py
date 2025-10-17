#!/usr/bin/env python3
"""
Test script for Phase 7: Records page UI, filters, tables, and analytics visuals
"""

import os
import sys
import time
from pathlib import Path

def test_file_structure():
    """Test that all required files exist and are properly structured."""
    print("Testing file structure...")
    
    required_files = {
        'templates/records.html': 'Records HTML template',
        'static/css/records.css': 'Records CSS file',
        'static/js/records.js': 'Records JavaScript file',
    }
    
    for file_path, description in required_files.items():
        full_path = Path(file_path)
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  ✓ {description} exists ({size} bytes)")
        else:
            print(f"  ✗ {description} missing")
            return False
    
    return True


def test_html_structure():
    """Test HTML template structure and key elements."""
    print("\nTesting HTML structure...")
    
    with open('templates/records.html', 'r') as f:
        html = f.read()
    
    required_elements = {
        'records.css': 'CSS file link',
        'records.js': 'JavaScript file link',
        'chart.js': 'Chart.js CDN',
        'chartjs-adapter-date-fns': 'Chart.js date adapter',
        'id="recordsChart"': 'Chart canvas element',
        'id="chartSection"': 'Chart section container',
        'id="statisticsSection"': 'Statistics section',
        'class="sortable"': 'Sortable table headers',
        'id="applyFiltersBtn"': 'Apply filters button',
        'id="resetFiltersBtn"': 'Reset filters button',
        'id="loadStatisticsBtn"': 'Load statistics button',
        'empty-state': 'Empty state styling',
        'id="recordsTableBody"': 'Table body',
        'id="recordsPerPageSelect"': 'Records per page selector',
    }
    
    all_found = True
    for element, description in required_elements.items():
        if element in html:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} missing")
            all_found = False
    
    return all_found


def test_css_structure():
    """Test CSS file for key styles and responsive design."""
    print("\nTesting CSS structure...")
    
    with open('static/css/records.css', 'r') as f:
        css = f.read()
    
    required_styles = {
        '.records-container': 'Main container',
        '.filters-section': 'Filters section',
        '.chart-section': 'Chart section',
        '.chart-container': 'Chart container',
        '.records-table': 'Records table',
        '.sortable': 'Sortable headers',
        '.empty-state': 'Empty state',
        '.stat-card': 'Statistics cards',
        '.loading': 'Loading state',
        '.error-message': 'Error messages',
        '@media': 'Responsive design',
        '@keyframes': 'CSS animations',
    }
    
    all_found = True
    for style, description in required_styles.items():
        if style in css:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} missing")
            all_found = False
    
    # Check CSS syntax
    braces = css.count('{') - css.count('}')
    if braces == 0:
        print("  ✓ CSS braces balanced")
    else:
        print(f"  ✗ CSS braces unbalanced: {braces}")
        all_found = False
    
    return all_found


def test_javascript_structure():
    """Test JavaScript file for key functions and features."""
    print("\nTesting JavaScript structure...")
    
    with open('static/js/records.js', 'r') as f:
        js = f.read()
    
    required_functions = {
        'getFilters': 'Filter state management',
        'loadRecords': 'Load records from API',
        'applyFilters': 'Apply filters',
        'resetFilters': 'Reset filters',
        'loadStatistics': 'Load statistics',
        'loadChart': 'Load chart data',
        'renderChart': 'Render Chart.js graph',
        'sortTable': 'Table sorting',
        'previousPage': 'Previous page navigation',
        'nextPage': 'Next page navigation',
        'formatTimestamp': 'Timestamp formatting',
        'updatePagination': 'Update pagination UI',
        'changeRecordsPerPage': 'Change records per page',
        'showError': 'Error display',
        'initializeSortHandlers': 'Initialize sort handlers',
    }
    
    all_found = True
    for func, description in required_functions.items():
        if func in js:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} missing")
            all_found = False
    
    # Check for Chart.js usage
    if 'new Chart' in js:
        print("  ✓ Chart.js instantiation")
    else:
        print("  ✗ Chart.js instantiation missing")
        all_found = False
    
    # Check for event listeners
    if 'addEventListener' in js:
        print("  ✓ Event listeners")
    else:
        print("  ✗ Event listeners missing")
        all_found = False
    
    return all_found


def test_integration():
    """Test that HTML references CSS and JS correctly."""
    print("\nTesting integration...")
    
    with open('templates/records.html', 'r') as f:
        html = f.read()
    
    checks = [
        ("url_for('static', filename='css/records.css')" in html, "CSS linked via Flask url_for"),
        ("url_for('static', filename='js/records.js')" in html, "JS linked via Flask url_for"),
        ('https://cdn.jsdelivr.net/npm/chart.js' in html, "Chart.js CDN link"),
        ('chartjs-adapter-date-fns' in html, "Chart.js date adapter link"),
    ]
    
    all_passed = True
    for check, description in checks:
        if check:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} failed")
            all_passed = False
    
    return all_passed


def test_features():
    """Test that key features are implemented."""
    print("\nTesting features implementation...")
    
    with open('static/js/records.js', 'r') as f:
        js = f.read()
    
    features = {
        'Filter panel': 'getFilters',
        'Statistics display': 'loadStatistics',
        'Chart visualization': 'renderChart',
        'Table sorting': 'sortTable',
        'Pagination': 'updatePagination',
        'Loading states': 'loadingMessage',
        'Error handling': 'showError',
        'Empty states': 'empty-state',
        'Responsive design': '@media',
    }
    
    all_found = True
    for feature, keyword in features.items():
        # Check in both JS and CSS
        found = False
        if keyword in js:
            found = True
        else:
            with open('static/css/records.css', 'r') as f:
                if keyword in f.read():
                    found = True
        
        if found:
            print(f"  ✓ {feature}")
        else:
            print(f"  ✗ {feature} missing")
            all_found = False
    
    return all_found


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 7 Test Suite: Records Page UI and Analytics")
    print("=" * 60)
    
    tests = [
        test_file_structure,
        test_html_structure,
        test_css_structure,
        test_javascript_structure,
        test_integration,
        test_features,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total} test suites")
    
    if all(results):
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
