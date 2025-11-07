# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Important Note**: If `codeact` is not available on PyPI, install from source:

```bash
git clone https://github.com/xingyaoww/code-act.git
cd code-act
pip install -e .
cd ..
```

### Step 2: Test the API Connection

```bash
python example_usage.py
```

This will test fetching data from your OHLC API.

### Step 3: Run the Application

**Option A: FastAPI Backend Only**
```bash
python api.py
```
Visit: http://localhost:8080/docs for API documentation

**Option B: Streamlit UI (Recommended)**
```bash
streamlit run app.py
```
Visit: http://localhost:8501

**Option C: Test Script**
```bash
python test_trader.py
```

## 📝 First Query Example

In the Streamlit UI or via API, try:

```
Calculate RSI(14) and plot it along with the price chart.
```

Or for a backtest:

```
Backtest a simple strategy: buy when close price is above SMA(20), sell when below.
Calculate total return and Sharpe ratio.
```

## 🔧 Configuration

### Change API Endpoint

Edit `finbytes/ohlca_api.py`:
```python
api_url = "https://your-api-endpoint.com/data"
```

### Change CodeAct Model

Edit `finbytes/codeact_trader.py`:
```python
model_name = "your-model-name"
```

## 🐳 Docker Quick Start

```bash
# Build
docker build -t finbytes-codeact .

# Run
docker run -p 8080:8080 finbytes-codeact
```

## ☁️ Deploy to Cloud Run

```bash
# Set your project ID
export GCP_PROJECT_ID=your-project-id

# Deploy
./deploy.sh
```

## ❓ Troubleshooting

**Problem**: `ImportError: No module named 'codeact'`
**Solution**: Install codeact from source (see Step 1)

**Problem**: API connection fails
**Solution**: Check your OHLC API endpoint in `finbytes/ohlca_api.py`

**Problem**: Model loading fails
**Solution**: Ensure you have internet connection and sufficient disk space

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [example_usage.py](example_usage.py) for code examples
- Explore the Streamlit UI for interactive analysis

