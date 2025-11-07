"""
Chat Interface for FinBytes Trading Analysis
Similar to CodeAct's chat interface, but for trading analysis.
"""
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import time

# Page config
st.set_page_config(
    page_title="FinBytes Trading Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for chat interface
st.markdown("""
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .message-content {
        flex: 1;
    }
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    .code-block {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Get API URL from environment variable (for Streamlit Cloud) or use default
env_api_url = os.getenv("API_URL", "")
if env_api_url:
    # If API_URL env var is set, use it (ensure it ends with /analyze)
    if not env_api_url.endswith("/analyze"):
        if env_api_url.endswith("/"):
            env_api_url = env_api_url + "analyze"
        else:
            env_api_url = env_api_url + "/analyze"
    default_api_url = env_api_url
else:
    # Default for local development
    default_api_url = "http://localhost:8080/analyze"

if "api_url" not in st.session_state:
    st.session_state.api_url = default_api_url

if "symbol" not in st.session_state:
    st.session_state.symbol = "AAPL"
if "interval" not in st.session_state:
    st.session_state.interval = "1w"
if "start_date" not in st.session_state:
    st.session_state.start_date = datetime(2024, 1, 1)
if "end_date" not in st.session_state:
    st.session_state.end_date = datetime(2024, 3, 31)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API endpoint - show as read-only if set via environment variable
    if env_api_url:
        st.text_input(
            "API Endpoint (from environment)",
            value=st.session_state.api_url,
            disabled=True,
            help="API URL is set via API_URL environment variable"
        )
        api_url = st.session_state.api_url
    else:
        api_url = st.text_input(
            "API Endpoint",
            value=st.session_state.api_url,
            help="URL of the FastAPI endpoint"
        )
        st.session_state.api_url = api_url
    
    st.markdown("---")
    st.header("📊 Data Settings")
    
    # Symbol input
    symbol = st.text_input("Symbol", value=st.session_state.symbol, help="Stock symbol (e.g., AAPL, TSLA)")
    st.session_state.symbol = symbol
    
    # Interval selection
    interval = st.selectbox(
        "Interval",
        options=["1d", "1w", "1mo"],
        index=["1d", "1w", "1mo"].index(st.session_state.interval) if st.session_state.interval in ["1d", "1w", "1mo"] else 1,
        help="Time interval for data"
    )
    st.session_state.interval = interval
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=st.session_state.start_date,
            max_value=datetime.now()
        )
        st.session_state.start_date = start_date
    with col2:
        end_date = st.date_input(
            "End Date",
            value=st.session_state.end_date,
            max_value=datetime.now()
        )
        st.session_state.end_date = end_date
    
    st.markdown("---")
    st.header("💡 Example Queries")
    
    example_queries = [
        "Backtest RSI(14) strategy with oversold at 30 and overbought at 70",
        "Calculate SMA(20) and SMA(50) crossover strategy",
        "Show me Bollinger Bands and identify squeeze periods",
        "Find support and resistance levels using pivot points",
        "Backtest MACD crossover strategy",
        "Calculate and plot RSI(14) with the price chart",
        "Analyze volume patterns and show volume moving average",
    ]
    
    for i, query in enumerate(example_queries):
        if st.button(f"📌 {query[:50]}...", key=f"example_{i}", use_container_width=True):
            st.session_state.example_query = query
            st.rerun()

# Main chat interface
st.title("💬 FinBytes Trading Chat")
st.markdown("Ask me anything about trading analysis! I can backtest strategies, calculate indicators, and analyze market data.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display additional data if available
        if "data" in message:
            data = message["data"]
            
            # Display metrics
            if any(key in data for key in ["total_return_pct", "sharpe", "max_dd_pct", "trades", "win_rate_pct"]):
                cols = st.columns(5)
                metrics = [
                    ("Total Return", data.get("total_return_pct"), "%"),
                    ("Sharpe", data.get("sharpe"), ""),
                    ("Max DD", data.get("max_dd_pct"), "%"),
                    ("Trades", data.get("trades"), ""),
                    ("Win Rate", data.get("win_rate_pct"), "%")
                ]
                
                for i, (label, value, unit) in enumerate(metrics):
                    if value is not None:
                        with cols[i]:
                            st.metric(label, f"{value:.2f}{unit}" if isinstance(value, (int, float)) else str(value))
            
            # Display statistics
            if "statistics" in data:
                with st.expander("📊 Statistics"):
                    st.json(data["statistics"])
            
            # Display support/resistance
            if "support_levels" in data or "resistance_levels" in data:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Support Levels:**")
                    st.write(data.get("support_levels", []))
                with col2:
                    st.write("**Resistance Levels:**")
                    st.write(data.get("resistance_levels", []))

# Handle example query
if "example_query" in st.session_state:
    query = st.session_state.example_query
    del st.session_state.example_query
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask me about trading strategies, indicators, or analysis..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        try:
            # Prepare request
            payload = {
                "query": prompt,
                "symbol": st.session_state.symbol,
                "interval": st.session_state.interval,
                "start_date": str(st.session_state.start_date),
                "end_date": str(st.session_state.end_date)
            }
            
            # Show loading spinner
            with st.spinner("🤖 Analyzing your query..."):
                # Make API request
                response = requests.post(
                    st.session_state.api_url,
                    json=payload,
                    timeout=300
                )
                response.raise_for_status()
                result = response.json()
            
            # Display summary immediately
            if "summary" in result:
                st.markdown(f"**{result['summary']}**")
            
            # Display metrics if available
            if any(key in result for key in ["total_return_pct", "sharpe", "max_dd_pct", "trades", "win_rate_pct"]):
                st.markdown("#### 📈 Performance Metrics")
                cols = st.columns(5)
                metrics = [
                    ("Total Return", result.get("total_return_pct"), "%"),
                    ("Sharpe Ratio", result.get("sharpe"), ""),
                    ("Max Drawdown", result.get("max_dd_pct"), "%"),
                    ("Trades", result.get("trades"), ""),
                    ("Win Rate", result.get("win_rate_pct"), "%")
                ]
                
                for i, (label, value, unit) in enumerate(metrics):
                    if value is not None:
                        with cols[i]:
                            st.metric(
                                label,
                                f"{value:.2f}{unit}" if isinstance(value, (int, float)) else str(value)
                            )
            
            # Display additional information
            if "statistics" in result:
                with st.expander("📊 Detailed Statistics"):
                    st.json(result["statistics"])
            
            if "support_levels" in result or "resistance_levels" in result:
                st.markdown("#### 🎯 Support & Resistance")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Support Levels:**")
                    st.write(result.get("support_levels", []))
                with col2:
                    st.write("**Resistance Levels:**")
                    st.write(result.get("resistance_levels", []))
            
            if "indicators" in result:
                with st.expander("📊 Indicators"):
                    st.json(result["indicators"])
            
            # Display detailed trades
            if "trades_detail" in result and result["trades_detail"]:
                st.markdown("#### 📋 Trade Details")
                
                # Trade statistics
                if result.get("winning_trades") is not None:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Winning Trades", result.get("winning_trades", 0))
                    with col2:
                        st.metric("Losing Trades", result.get("losing_trades", 0))
                    with col3:
                        st.metric("Avg Win", f"{result.get('avg_win_pct', 0):.2f}%")
                    with col4:
                        st.metric("Avg Loss", f"{result.get('avg_loss_pct', 0):.2f}%")
                
                # Create trades DataFrame
                trades_df = pd.DataFrame(result["trades_detail"])
                
                # Format the trades table
                if not trades_df.empty:
                    # Select and rename columns for display
                    display_cols = {
                        'trade_number': 'Trade #',
                        'entry_date': 'Entry Date',
                        'exit_date': 'Exit Date',
                        'entry_price': 'Entry Price',
                        'exit_price': 'exit_price',
                        'pnl_pct': 'P&L %',
                        'pnl_amount': 'P&L $',
                        'duration_periods': 'Duration',
                        'win': 'Win'
                    }
                    
                    # Create display dataframe
                    display_df = trades_df.copy()
                    if 'win' in display_df.columns:
                        display_df['Win'] = display_df['win'].map({True: '✅', False: '❌'})
                    
                    # Select columns to display
                    cols_to_show = ['trade_number', 'entry_date', 'exit_date', 'entry_price', 'exit_price', 'pnl_pct', 'pnl_amount', 'duration_periods', 'Win']
                    available_cols = [col for col in cols_to_show if col in display_df.columns]
                    display_df = display_df[available_cols]
                    
                    # Rename columns
                    rename_map = {
                        'trade_number': 'Trade #',
                        'entry_date': 'Entry Date',
                        'exit_date': 'Exit Date',
                        'entry_price': 'Entry Price',
                        'exit_price': 'Exit Price',
                        'pnl_pct': 'P&L %',
                        'pnl_amount': 'P&L $',
                        'duration_periods': 'Duration',
                        'Win': 'Result'
                    }
                    display_df = display_df.rename(columns=rename_map)
                    
                    # Style the dataframe
                    def color_pnl(val):
                        if isinstance(val, (int, float)):
                            color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
                            return f'color: {color}; font-weight: bold'
                        return ''
                    
                    # Apply styling
                    styled_df = display_df.style.applymap(
                        color_pnl,
                        subset=['P&L %', 'P&L $']
                    )
                    
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    
                    # Summary statistics
                    with st.expander("📊 Trade Statistics"):
                        if result.get("largest_win_pct") is not None:
                            st.write(f"**Largest Win:** {result.get('largest_win_pct', 0):.2f}%")
                        if result.get("largest_loss_pct") is not None:
                            st.write(f"**Largest Loss:** {result.get('largest_loss_pct', 0):.2f}%")
                        if result.get("avg_win_pct") is not None:
                            st.write(f"**Average Win:** {result.get('avg_win_pct', 0):.2f}%")
                        if result.get("avg_loss_pct") is not None:
                            st.write(f"**Average Loss:** {result.get('avg_loss_pct', 0):.2f}%")
            
            # Display plot if available
            if "plot" in result and result["plot"]:
                if os.path.exists(result["plot"]):
                    st.image(result["plot"], use_container_width=True)
            
            # Build full response text for chat history
            response_parts = []
            if "summary" in result:
                response_parts.append(result["summary"])
            if any(key in result for key in ["total_return_pct", "sharpe", "max_dd_pct", "trades", "win_rate_pct"]):
                metrics_text = []
                if result.get("total_return_pct") is not None:
                    metrics_text.append(f"Return: {result['total_return_pct']:.2f}%")
                if result.get("sharpe") is not None:
                    metrics_text.append(f"Sharpe: {result['sharpe']:.2f}")
                if result.get("trades") is not None:
                    metrics_text.append(f"Trades: {result['trades']}")
                if metrics_text:
                    response_parts.append(" | ".join(metrics_text))
            
            assistant_message = "\n\n".join(response_parts) if response_parts else "Analysis completed."
            
            # Add assistant message to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_message,
                "data": result
            })
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ API request failed: {str(e)}"
            st.error(error_msg)
            st.info("Make sure the API is running. For local testing, run: `python3 api.py`")
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.error(error_msg)
            import traceback
            st.code(traceback.format_exc())
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })

# Clear chat button
if st.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>💬 FinBytes Trading Chat • Powered by CodeAct & SimpleTrader</p>
        <p>Ask me about trading strategies, technical indicators, and market analysis</p>
    </div>
    """,
    unsafe_allow_html=True
)

