# 🚀 Quick Start Guide

## Services Started

### ✅ API Server
- **URL**: http://localhost:8080
- **Health Check**: http://localhost:8080/health
- **API Docs**: http://localhost:8080/docs
- **Status**: Running in background

### ✅ Streamlit UI
- **URL**: http://localhost:8501
- **Status**: Running in background

## 🎯 How to Use

### 1. Open Streamlit UI
Open your browser and go to: **http://localhost:8501**

### 2. Try These Queries

**Basic Analysis:**
- "Calculate RSI(14)"
- "Show me SMA(20) and SMA(50)"
- "Calculate Bollinger Bands"

**Backtesting:**
- "Backtest RSI strategy"
- "Backtest SMA crossover"
- "Backtest MACD strategy"

**Support/Resistance:**
- "Find support and resistance levels"
- "Show me pivot points"

### 3. Test API Directly

```bash
# Health check
curl http://localhost:8080/health

# Test analysis
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Backtest RSI strategy",
    "symbol": "AAPL",
    "interval": "1w",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
  }'
```

## 📊 Example Queries

### Technical Indicators
```
"Calculate RSI(14) and plot it"
"Show me MACD with signal line"
"Calculate Bollinger Bands with 20 period"
```

### Strategy Backtesting
```
"Backtest RSI strategy with oversold at 30 and overbought at 70"
"Backtest SMA crossover with fast=10 and slow=20"
"Backtest MACD crossover strategy"
```

### Analysis
```
"Find support and resistance levels"
"Show me candlestick patterns"
"Calculate volatility and Sharpe ratio"
```

## 🔧 Troubleshooting

### API Not Responding
```bash
# Check if API is running
ps aux | grep api.py

# Restart API
source venv/bin/activate
python3 api.py
```

### Streamlit Not Loading
```bash
# Check if Streamlit is running
ps aux | grep streamlit

# Restart Streamlit
source venv/bin/activate
streamlit run app.py
```

### Port Already in Use
```bash
# Find process using port
lsof -ti:8080  # API
lsof -ti:8501  # Streamlit

# Kill process if needed
kill -9 <PID>
```

## 📝 Next Steps

1. **Try the UI**: Open http://localhost:8501
2. **Test queries**: Try different trading strategies
3. **Check API docs**: Visit http://localhost:8080/docs
4. **Add CodeAct** (optional): See CODEACT_FULL_SETUP.md

## 🎉 You're Ready!

The system is running and ready to use. Start with the Streamlit UI at http://localhost:8501!

