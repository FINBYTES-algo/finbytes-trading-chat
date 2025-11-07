#!/bin/bash
# Simple test script for local testing

echo "=========================================="
echo "FinBytes CodeAct - Local Testing"
echo "=========================================="
echo ""

# Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "   ✓ Python3 found: $(python3 --version)"
else
    echo "   ✗ Python3 not found"
    exit 1
fi

# Check pip
echo ""
echo "2. Checking pip..."
if command -v pip3 &> /dev/null; then
    echo "   ✓ pip3 found"
else
    echo "   ✗ pip3 not found"
    exit 1
fi

# Test imports
echo ""
echo "3. Testing basic imports..."
$PYTHON_CMD -c "import pandas, numpy, requests" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ Basic packages available"
else
    echo "   ✗ Missing packages. Run: pip3 install -r requirements.txt"
    exit 1
fi

# Test OHLC API
echo ""
echo "4. Testing OHLC API connection..."
$PYTHON_CMD -c "
from finbytes.ohlca_api import fetch_ohlc_data
try:
    df = fetch_ohlc_data('AAPL', '1w', '2024-01-01', '2024-03-31')
    print(f'   ✓ API connection successful ({len(df)} rows)')
except Exception as e:
    print(f'   ✗ API connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Basic tests passed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Start API: python3 api.py"
echo "  2. Start UI: streamlit run app.py"
echo "  3. Full test: python3 test_local.py"
echo ""

