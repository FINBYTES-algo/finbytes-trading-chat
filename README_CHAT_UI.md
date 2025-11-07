# 💬 Chat Interface

We've created a chat interface similar to the CodeAct demo! This provides a conversational experience for trading analysis.

## 🚀 Running the Chat Interface

### Option 1: Chat UI (Recommended)
```bash
source venv/bin/activate
streamlit run chat_ui.py
```

Then open: **http://localhost:8501**

### Option 2: Legacy Form UI
```bash
source venv/bin/activate
streamlit run app.py
```

## ✨ Features

### Chat Interface (`chat_ui.py`)
- 💬 **Conversational UI** - Chat-like interface similar to CodeAct demo
- 📊 **Rich Results** - Displays metrics, charts, and analysis
- 💡 **Example Queries** - Quick access to common queries
- ⚙️ **Sidebar Configuration** - Easy access to settings
- 📈 **Real-time Analysis** - Get instant trading insights

### Legacy Form UI (`app.py`)
- 📝 Form-based interface
- All the same functionality
- Different user experience

## 🎯 Example Queries

Try these in the chat interface:

**Backtesting:**
- "Backtest RSI(14) strategy with oversold at 30 and overbought at 70"
- "Calculate SMA(20) and SMA(50) crossover strategy"
- "Backtest MACD crossover strategy"

**Analysis:**
- "Show me Bollinger Bands and identify squeeze periods"
- "Find support and resistance levels using pivot points"
- "Calculate and plot RSI(14) with the price chart"
- "Analyze volume patterns and show volume moving average"

## 📊 What You'll See

The chat interface displays:
- **Summary** - Quick overview of results
- **Performance Metrics** - Returns, Sharpe ratio, drawdown, etc.
- **Statistics** - Detailed statistical analysis
- **Support/Resistance** - Key price levels
- **Charts** - Visualizations when available

## 🔧 Configuration

All settings are in the sidebar:
- **API Endpoint** - Your FastAPI server URL
- **Symbol** - Stock symbol to analyze
- **Interval** - Time interval (1d, 1w, 1mo)
- **Date Range** - Start and end dates

## 🎨 Interface Comparison

### Chat UI (`chat_ui.py`)
- ✅ Modern chat interface
- ✅ Conversation history
- ✅ Rich message formatting
- ✅ Example queries sidebar
- ✅ Similar to CodeAct demo

### Form UI (`app.py`)
- ✅ Traditional form interface
- ✅ Single query at a time
- ✅ All features available
- ✅ Good for quick tests

## 🚀 Quick Start

1. **Start API** (if not running):
   ```bash
   source venv/bin/activate
   python3 api.py
   ```

2. **Start Chat UI**:
   ```bash
   source venv/bin/activate
   streamlit run chat_ui.py
   ```

3. **Open Browser**: http://localhost:8501

4. **Start Chatting**: Ask about trading strategies!

## 💡 Tips

- Use example queries for quick testing
- Adjust symbol and date range in sidebar
- Clear chat to start fresh
- Results are saved in conversation history

Enjoy your trading analysis chat! 🎉

