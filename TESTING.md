# Local Testing Guide

This guide will help you test the FinBytes CodeAct Trading Analysis System locally.

## 🧪 Quick Test

Run the comprehensive test script:

```bash
python test_local.py
```

This will test:
1. ✅ All required packages are installed
2. ✅ OHLC API connection works
3. ✅ Direct API calls succeed
4. ✅ CodeAct can be imported
5. ✅ FastAPI module loads
6. ✅ Streamlit module loads

## 📋 Step-by-Step Testing

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**If codeact is not available on PyPI:**
```bash
git clone https://github.com/xingyaoww/code-act.git
cd code-act
pip install -e .
cd ..
```

### Step 2: Test API Connection

Test if you can fetch data from your OHLC API:

```bash
python -c "from finbytes.ohlca_api import fetch_ohlc_data; df = fetch_ohlc_data('AAPL', '1w', '2024-01-01', '2024-03-31'); print(f'Success! Fetched {len(df)} rows'); print(df.head())"
```

Or use the example script:

```bash
python example_usage.py
```

### Step 3: Test FastAPI Backend

**Terminal 1 - Start the API:**
```bash
python api.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
```

**Terminal 2 - Test the API:**

```bash
# Health check
curl http://localhost:8080/health

# Test analysis endpoint
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Calculate and plot the 20-day Simple Moving Average on close price",
    "symbol": "AAPL",
    "interval": "1w",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
  }'
```

Or visit the interactive docs:
- Open browser: http://localhost:8080/docs
- Click on `/analyze` endpoint
- Click "Try it out"
- Enter your request and click "Execute"

### Step 4: Test Streamlit UI

**Terminal 1 - Start the API (if not already running):**
```bash
python api.py
```

**Terminal 2 - Start Streamlit:**
```bash
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

**In the browser:**
1. Open http://localhost:8501
2. Enter a symbol (e.g., "AAPL")
3. Select interval (e.g., "1w")
4. Choose date range
5. Enter a query like: "Calculate RSI(14) and plot it"
6. Click "Run Analysis"

### Step 5: Test CodeAct Trader Directly

Test the trader with a simple query:

```bash
python test_trader.py
```

This will:
- Initialize CodeAct agent (may take a few minutes first time)
- Fetch AAPL data
- Execute a sample strategy
- Display results

## 🔍 Individual Component Tests

### Test OHLC API Only

```python
from finbytes.ohlca_api import fetch_ohlc_data

df = fetch_ohlc_data("AAPL", "1w", "2024-01-01", "2024-03-31")
print(df.head())
print(f"Rows: {len(df)}")
```

### Test CodeAct Trader Only

```python
from finbytes.codeact_trader import TraderCodeAct

trader = TraderCodeAct()
result = trader.analyze(
    user_query="Calculate SMA(20) on close price",
    symbol="AAPL",
    interval="1w",
    start_date="2024-01-01",
    end_date="2024-03-31"
)
print(result)
```

### Test FastAPI Endpoint Only

```python
import requests

response = requests.post(
    "http://localhost:8080/analyze",
    json={
        "query": "Calculate RSI(14)",
        "symbol": "AAPL",
        "interval": "1w",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31"
    }
)
print(response.json())
```

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'codeact'"

**Solution:**
```bash
# Install from source
git clone https://github.com/xingyaoww/code-act.git
cd code-act
pip install -e .
```

### Problem: "Connection refused" when calling API

**Solution:**
- Make sure the API is running: `python api.py`
- Check the port (default: 8080)
- Verify the API URL in Streamlit UI settings

### Problem: "API request failed" in Streamlit

**Solution:**
1. Check if API is running: `curl http://localhost:8080/health`
2. Update API URL in Streamlit sidebar to: `http://localhost:8080/analyze`
3. Check API logs for errors

### Problem: "Model loading failed" in CodeAct

**Solution:**
- Ensure internet connection (model downloads from Hugging Face)
- Check disk space (models can be large)
- Verify model name in `finbytes/codeact_trader.py`

### Problem: OHLC API returns empty data

**Solution:**
- Verify API endpoint URL in `finbytes/ohlca_api.py`
- Test API directly: `curl "https://ohlca-date-api-331576355022.us-central1.run.app/data?symbol=AAPL&interval=1w&start_date=2024-01-01&end_date=2024-03-31"`
- Check date range is valid
- Verify symbol exists

## ✅ Success Checklist

- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] `test_local.py` passes all tests
- [ ] OHLC API connection works
- [ ] FastAPI starts without errors
- [ ] API responds to health check
- [ ] Streamlit UI loads
- [ ] Can submit a query in Streamlit
- [ ] CodeAct executes a simple query

## 🚀 Next Steps After Testing

Once all tests pass:

1. **For Development:**
   - Modify queries in Streamlit UI
   - Test different strategies
   - Experiment with CodeAct prompts

2. **For Production:**
   - Review `Dockerfile` for containerization
   - Run `./deploy.sh` for Cloud Run deployment
   - Set up monitoring and logging

3. **For Customization:**
   - Update API endpoint in `finbytes/ohlca_api.py`
   - Modify CodeAct prompts in `finbytes/codeact_trader.py`
   - Customize Streamlit UI in `app.py`

## 📞 Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review [QUICKSTART.md](QUICKSTART.md) for quick setup
- Check error logs in terminal output
- Verify all environment variables are set correctly

