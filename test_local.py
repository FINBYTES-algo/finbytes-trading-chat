"""
Local testing script for FinBytes CodeAct Trading Analysis System.
Tests each component step by step.
"""
import sys
import requests
import json
from datetime import datetime

def test_1_imports():
    """Test 1: Check if all required packages are installed."""
    print("=" * 60)
    print("Test 1: Checking Imports")
    print("=" * 60)
    
    required_packages = [
        'pandas',
        'numpy',
        'requests',
        'fastapi',
        'streamlit',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    # Check codeact separately
    try:
        from codeact import CodeActAgent
        print("✓ codeact")
    except ImportError:
        print("✗ codeact - NOT INSTALLED")
        print("  Note: You may need to install from source:")
        print("  git clone https://github.com/xingyaoww/code-act.git")
        print("  cd code-act && pip install -e .")
        missing.append('codeact')
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required packages are installed!")
        return True


def test_2_ohlc_api():
    """Test 2: Test OHLC API connection."""
    print("\n" + "=" * 60)
    print("Test 2: Testing OHLC API Connection")
    print("=" * 60)
    
    try:
        from finbytes.ohlca_api import fetch_ohlc_data
        
        print("Fetching AAPL weekly data from 2024-01-01 to 2024-03-31...")
        df = fetch_ohlc_data(
            symbol="AAPL",
            interval="1w",
            start_date="2024-01-01",
            end_date="2024-03-31"
        )
        
        print(f"✅ Successfully fetched {len(df)} rows")
        print("\nFirst 3 rows:")
        print(df.head(3))
        print("\nData types:")
        print(df.dtypes)
        print("\nBasic stats:")
        print(df.describe())
        
        return True
        
    except Exception as e:
        print(f"❌ OHLC API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_direct_api_call():
    """Test 3: Test direct API call to OHLC endpoint."""
    print("\n" + "=" * 60)
    print("Test 3: Direct API Call to OHLC Endpoint")
    print("=" * 60)
    
    api_url = "https://ohlca-date-api-331576355022.us-central1.run.app/data"
    params = {
        "symbol": "AAPL",
        "interval": "1w",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31"
    }
    
    try:
        print(f"Calling: {api_url}")
        print(f"Params: {params}")
        
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ API call successful!")
        print(f"   Status code: {response.status_code}")
        print(f"   Data points: {len(data.get('data', []))}")
        
        if data.get('data'):
            print(f"\n   First data point:")
            print(f"   {json.dumps(data['data'][0], indent=6)}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_4_codeact_import():
    """Test 4: Test CodeAct import and initialization."""
    print("\n" + "=" * 60)
    print("Test 4: Testing CodeAct Import")
    print("=" * 60)
    
    try:
        from finbytes.codeact_trader import TraderCodeAct
        print("✅ TraderCodeAct class imported successfully")
        
        print("\nNote: Full CodeAct initialization will download the model.")
        print("This may take several minutes on first run.")
        
        response = input("\nDo you want to test full initialization? (y/n): ")
        if response.lower() == 'y':
            print("\nInitializing CodeAct agent (this may take a while)...")
            trader = TraderCodeAct()
            print("✅ CodeAct agent initialized successfully!")
            return True
        else:
            print("⏭️  Skipping full initialization")
            return True
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def test_5_fastapi_import():
    """Test 5: Test FastAPI import."""
    print("\n" + "=" * 60)
    print("Test 5: Testing FastAPI Import")
    print("=" * 60)
    
    try:
        import api
        print("✅ FastAPI module imported successfully")
        print("   To start the API server, run: python api.py")
        return True
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_6_streamlit_import():
    """Test 6: Test Streamlit import."""
    print("\n" + "=" * 60)
    print("Test 6: Testing Streamlit Import")
    print("=" * 60)
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
        print("   To start the UI, run: streamlit run app.py")
        return True
    except Exception as e:
        print(f"❌ Streamlit import failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("FinBytes CodeAct Trading Analysis - Local Testing")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_1_imports()))
    results.append(("OHLC API Module", test_2_ohlc_api()))
    results.append(("Direct API Call", test_3_direct_api_call()))
    results.append(("CodeAct Import", test_4_codeact_import()))
    results.append(("FastAPI Import", test_5_fastapi_import()))
    results.append(("Streamlit Import", test_6_streamlit_import()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to use the system.")
        print("\nNext steps:")
        print("  1. Start API: python api.py")
        print("  2. Start UI: streamlit run app.py")
        print("  3. Test trader: python test_trader.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

