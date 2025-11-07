# FinBytes CodeAct Trading Analysis System

A production-ready trading analysis platform that uses **CodeAct** to execute natural language trading strategies and analysis. Traders can describe strategies in plain English, and CodeAct automatically writes, executes, and debugs the code.

## 🚀 Features

- **Natural Language Trading**: Describe strategies in plain English
- **Automatic Code Generation**: CodeAct writes and executes Python code
- **Real Market Data**: Connects to your OHLC API
- **Full Backtesting**: Uses vectorbt for accurate strategy backtesting
- **Visualizations**: Automatic plot generation
- **Production Ready**: FastAPI backend + Streamlit UI
- **Cloud Deployable**: Docker + Cloud Run ready

## 📋 Prerequisites

- Python 3.11+
- pip
- (Optional) Docker for containerized deployment
- (Optional) Google Cloud SDK for Cloud Run deployment

## 🛠️ Installation

### 1. Clone or Download This Repository

```bash
cd CodeAct
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The `codeact` package may need to be installed from source if it's not available on PyPI. Check the [CodeAct repository](https://github.com/xingyaoww/code-act) for installation instructions.

### 3. Verify Installation

```bash
python test_trader.py
```

## 🏃 Quick Start

### Option 1: Test Script (CLI)

```bash
python test_trader.py
```

This will:
1. Initialize CodeAct agent
2. Fetch AAPL weekly data from your API
3. Execute a sample RSI + SMA crossover strategy
4. Display results

### Option 2: FastAPI Backend

Start the API server:

```bash
python api.py
```

The API will be available at `http://localhost:8080`

Test with curl:

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Backtest RSI(14) + SMA(20) crossover strategy",
    "symbol": "AAPL",
    "interval": "1w",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
  }'
```

### Option 3: Streamlit UI

Start the Streamlit app:

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

## 📁 Project Structure

```
CodeAct/
├── finbytes/
│   ├── __init__.py
│   ├── ohlca_api.py          # OHLC API client
│   └── codeact_trader.py     # CodeAct trader logic
├── api.py                    # FastAPI endpoint
├── app.py                    # Streamlit UI
├── test_trader.py           # Test script
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose for local dev
└── README.md               # This file
```

## 🔧 Configuration

### API Endpoint

The OHLC API endpoint is configured in `finbytes/ohlca_api.py`:

```python
api_url = "https://ohlca-date-api-331576355022.us-central1.run.app/data"
```

### CodeAct Model

Default model is set in `finbytes/codeact_trader.py`:

```python
model_name = "xingyaoww/CodeActAgent-Mistral-7b-v0.1"
```

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t finbytes-codeact-trader .
```

### Run Container

```bash
docker run -p 8080:8080 finbytes-codeact-trader
```

### Docker Compose (Local Development)

```bash
docker-compose up
```

## ☁️ Google Cloud Run Deployment

### 1. Build and Push to Container Registry

```bash
# Set your project ID
export PROJECT_ID=your-project-id
export SERVICE_NAME=finbytes-codeact-trader
export REGION=us-central1

# Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

### 3. Get Service URL

```bash
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
```

## 📊 Example Queries

Traders can use natural language to request various analyses:

### Backtesting Strategies

```
"Backtest RSI(14) + SMA(20) crossover. Enter long when RSI < 30 and Close > SMA(20). Exit when RSI > 70."
```

```
"Backtest mean reversion: buy when RSI(2) < 20, sell when RSI(2) > 80. Use vectorbt."
```

### Technical Analysis

```
"Show me Bollinger Bands squeeze on this data. Plot the bands and identify squeeze periods."
```

```
"Find support and resistance levels using pivot points. Mark them on a chart."
```

### Indicators

```
"Calculate MACD crossover strategy. Enter long on bullish crossover, exit on bearish crossover."
```

```
"Analyze volume patterns. Show volume moving average and identify unusual volume spikes."
```

## 🔌 API Reference

### POST /analyze

Execute trading analysis.

**Request Body:**
```json
{
  "query": "Your natural language query",
  "symbol": "AAPL",
  "interval": "1w",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31"
}
```

**Response:**
```json
{
  "summary": "Strategy returned 7.8% with Sharpe 1.4",
  "total_return_pct": 7.8,
  "sharpe": 1.41,
  "max_dd_pct": 3.2,
  "trades": 3,
  "win_rate_pct": 66.67,
  "plot": "/tmp/result.png",
  "symbol": "AAPL",
  "interval": "1w",
  "start_date": "2024-01-01",
  "end_date": "2024-03-31",
  "data_points": 13
}
```

### GET /health

Health check endpoint.

## 🛡️ Security Considerations

1. **API Authentication**: Add authentication to your OHLC API endpoint
2. **Rate Limiting**: Implement rate limiting in FastAPI
3. **Sandbox Execution**: CodeAct should run in a sandboxed environment
4. **Resource Limits**: Set memory and CPU limits in Cloud Run
5. **Input Validation**: Validate all user inputs

## 🐛 Troubleshooting

### CodeAct Not Found

If you get `ImportError: No module named 'codeact'`:

1. Check if codeact is installed: `pip list | grep codeact`
2. If not available on PyPI, install from source:
   ```bash
   git clone https://github.com/xingyaoww/code-act.git
   cd code-act
   pip install -e .
   ```

### API Connection Errors

- Verify your OHLC API is accessible
- Check network connectivity
- Verify API endpoint URL in `ohlca_api.py`

### Model Loading Issues

- Ensure you have sufficient disk space for model cache
- Check Hugging Face authentication if using private models
- Verify model name is correct

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions welcome! Please open issues or pull requests.

## 📧 Support

For issues or questions, please open an issue on the repository.

---

**Built with ❤️ using CodeAct, FastAPI, and Streamlit**

