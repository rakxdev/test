#!/usr/bin/env python3
"""
Phase 5 Test Script - Real-time Chart.js Visualization
Tests chart-handler.js utilities and dashboard.js chart integration
"""

import os
import re

def test_file_exists():
    """Test that all required Phase 5 files exist"""
    print("Testing file existence...")
    
    files = [
        'static/js/chart-handler.js',
        'PHASE5_IMPLEMENTATION.md'
    ]
    
    for file in files:
        if os.path.exists(file):
            print(f"  ✓ {file} exists")
        else:
            print(f"  ✗ {file} missing")
            return False
    
    return True

def test_chart_handler_content():
    """Test chart-handler.js has required functionality"""
    print("\nTesting chart-handler.js content...")
    
    with open('static/js/chart-handler.js', 'r') as f:
        content = f.read()
    
    required_features = [
        ('ChartHandler object', r'const ChartHandler\s*='),
        ('Color schemes', r'colors:\s*\{'),
        ('getChartOptions method', r'getChartOptions\s*\('),
        ('createDataset method', r'createDataset\s*\('),
        ('pruneOldData method', r'pruneOldData\s*\('),
        ('addDataPoint method', r'addDataPoint\s*\('),
        ('updateChart method', r'updateChart\s*\('),
        ('exportChartAsPNG method', r'exportChartAsPNG\s*\('),
        ('clearChartData method', r'clearChartData\s*\('),
        ('updateTimeRange method', r'updateTimeRange\s*\('),
        ('createRealtimeChart method', r'createRealtimeChart\s*\('),
        ('Smooth lines (tension)', r'tension:\s*0\.4'),
        ('Tooltips configuration', r'tooltip:\s*\{'),
        ('Legend configuration', r'legend:\s*\{'),
        ('Time-based X-axis', r"type:\s*['\"]time['\"]"),
        ('Mode colors', r'modeColors:\s*\{')
    ]
    
    all_passed = True
    for name, pattern in required_features:
        if re.search(pattern, content):
            print(f"  ✓ {name} found")
        else:
            print(f"  ✗ {name} missing")
            all_passed = False
    
    return all_passed

def test_dashboard_js_integration():
    """Test dashboard.js has chart integration"""
    print("\nTesting dashboard.js chart integration...")
    
    with open('static/js/dashboard.js', 'r') as f:
        content = f.read()
    
    required_features = [
        ('Chart property', r'this\.chart\s*='),
        ('chartPaused property', r'this\.chartPaused'),
        ('timeWindow property', r'this\.timeWindow'),
        ('initializeChart method', r'initializeChart\s*\(\)'),
        ('addDataToChart method', r'addDataToChart\s*\('),
        ('toggleChartPause method', r'toggleChartPause\s*\('),
        ('clearChart method', r'clearChart\s*\('),
        ('exportChart method', r'exportChart\s*\('),
        ('updateTimeWindow method', r'updateTimeWindow\s*\('),
        ('Chart button listeners', r'pauseResumeBtn'),
        ('Time range selector', r'timeRangeSelect'),
        ('Chart update in data handler', r'addDataToChart'),
        ('Chart cleanup in destroy', r'chart\.destroy')
    ]
    
    all_passed = True
    for name, pattern in required_features:
        if re.search(pattern, content):
            print(f"  ✓ {name} found")
        else:
            print(f"  ✗ {name} missing")
            all_passed = False
    
    return all_passed

def test_template_updates():
    """Test mode-dashboard.html has chart elements"""
    print("\nTesting mode-dashboard.html template...")
    
    with open('templates/mode-dashboard.html', 'r') as f:
        content = f.read()
    
    required_elements = [
        ('Chart.js CDN', r'chart\.js'),
        ('Date-fns adapter', r'chartjs-adapter-date-fns'),
        ('chart-handler.js script', r'chart-handler\.js'),
        ('Chart container', r'chart-container'),
        ('Chart canvas', r'<canvas[^>]*id=["\']realtimeChart["\']'),
        ('Pause/Resume button', r'id=["\']pauseResumeBtn["\']'),
        ('Clear button', r'id=["\']clearChartBtn["\']'),
        ('Export button', r'id=["\']exportChartBtn["\']'),
        ('Time range selector', r'id=["\']timeRangeSelect["\']'),
        ('30s option', r'value=["\']30["\']'),
        ('60s option', r'value=["\']60["\']'),
        ('Chart controls div', r'chart-controls')
    ]
    
    all_passed = True
    for name, pattern in required_elements:
        if re.search(pattern, content):
            print(f"  ✓ {name} found")
        else:
            print(f"  ✗ {name} missing")
            all_passed = False
    
    return all_passed

def test_css_styles():
    """Test dashboard.css has chart styles"""
    print("\nTesting dashboard.css styles...")
    
    with open('static/css/dashboard.css', 'r') as f:
        content = f.read()
    
    required_styles = [
        ('Chart container', r'\.chart-container'),
        ('Chart header', r'\.chart-header'),
        ('Chart controls', r'\.chart-controls'),
        ('Chart button control', r'\.btn-chart-control'),
        ('Time range select', r'\.time-range-select'),
        ('Chart canvas wrapper', r'\.chart-canvas-wrapper'),
        ('Paused state', r'\.paused'),
        ('Responsive chart (tablet)', r'@media.*max-width:\s*1024px.*chart'),
        ('Responsive chart (mobile)', r'@media.*max-width:\s*768px.*chart')
    ]
    
    all_passed = True
    for name, pattern in required_styles:
        if re.search(pattern, content, re.DOTALL):
            print(f"  ✓ {name} found")
        else:
            print(f"  ✗ {name} missing")
            all_passed = False
    
    return all_passed

def test_documentation():
    """Test Phase 5 documentation"""
    print("\nTesting Phase 5 documentation...")
    
    with open('PHASE5_IMPLEMENTATION.md', 'r') as f:
        content = f.read()
    
    required_sections = [
        ('Overview section', r'## Overview'),
        ('Chart Handler section', r'chart-handler\.js'),
        ('Dashboard extension', r'dashboard\.js'),
        ('Template updates', r'mode-dashboard\.html'),
        ('CSS updates', r'dashboard\.css'),
        ('Features list', r'Features Implemented'),
        ('Technical details', r'Technical Details'),
        ('Usage guide', r'Usage'),
        ('Performance considerations', r'Performance'),
        ('Dataset configuration', r'Dataset')
    ]
    
    all_passed = True
    for name, pattern in required_sections:
        if re.search(pattern, content):
            print(f"  ✓ {name} found")
        else:
            print(f"  ✗ {name} missing")
            all_passed = False
    
    # Check README updates
    with open('README.md', 'r') as f:
        readme = f.read()
    
    if 'Phase 5' in readme or 'Chart.js' in readme:
        print(f"  ✓ README.md updated with Phase 5 info")
    else:
        print(f"  ✗ README.md not updated")
        all_passed = False
    
    return all_passed

def main():
    """Run all Phase 5 tests"""
    print("=" * 60)
    print("Phase 5 Test Suite - Real-time Chart.js Visualization")
    print("=" * 60)
    
    tests = [
        test_file_exists,
        test_chart_handler_content,
        test_dashboard_js_integration,
        test_template_updates,
        test_css_styles,
        test_documentation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n  ✗ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All Phase 5 tests passed!")
        return 0
    else:
        print("\n✗ Some Phase 5 tests failed")
        return 1

if __name__ == '__main__':
    exit(main())
