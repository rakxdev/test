#!/bin/bash

echo "================================================"
echo "Phase 6 Implementation Verification"
echo "================================================"
echo ""

# Check Python files exist
echo "Checking files..."
FILES=(
    "app.py"
    "database.py"
    "templates/records.html"
    "test_phase6.py"
    "PHASE6_IMPLEMENTATION.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        exit 1
    fi
done

echo ""
echo "Checking Python syntax..."
python3 -m py_compile app.py database.py test_phase6.py
if [ $? -eq 0 ]; then
    echo "✓ All Python files compile successfully"
else
    echo "✗ Python syntax errors found"
    exit 1
fi

echo ""
echo "Initializing database..."
python3 database.py
if [ $? -eq 0 ]; then
    echo "✓ Database initialized successfully"
else
    echo "✗ Database initialization failed"
    exit 1
fi

echo ""
echo "Running database tests..."
python3 test_phase6.py
if [ $? -eq 0 ]; then
    echo "✓ Database tests passed"
else
    echo "✗ Database tests failed"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ Phase 6 verification complete!"
echo "================================================"
echo ""
echo "New features implemented:"
echo "  • /api/records endpoint with filtering and pagination"
echo "  • /api/statistics endpoint for metrics calculation"
echo "  • Aggregation intervals: raw, 1min, 5min, 15min, 60min"
echo "  • Interactive records page with filter controls"
echo "  • Composite database index for performance"
echo ""
echo "To test with live server:"
echo "  1. Start Flask: python3 app.py"
echo "  2. In another terminal: python3 test_phase6.py --with-server"
echo "  3. Or visit: http://localhost:5000/records"
echo ""
