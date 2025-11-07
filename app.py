"""
Streamlit UI for FinBytes CodeAct Trading Analysis (Legacy Form-based Interface).
For the new chat interface, use: streamlit run chat_ui.py
"""
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import os

# Page config
st.set_page_config(
    page_title="FinBytes AI Trader",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">📈 FinBytes AI Trader (CodeAct)</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# API endpoint configuration
api_url = st.sidebar.text_input(
    "API Endpoint",
    value=os.getenv("API_URL", "http://localhost:8080/analyze"),
    help="URL of the FastAPI endpoint"
)

# Symbol input
symbol = st.sidebar.text_input("Symbol", value="AAPL", help="Stock symbol (e.g., AAPL, TSLA)")

# Interval selection
interval = st.sidebar.selectbox(
    "Interval",
    options=["1d", "1w", "1mo"],
    index=1,
    help="Time interval for data"
)

# Date range
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=datetime(2024, 1, 1),
        max_value=datetime.now()
    )
with col2:
    end_date = st.date_input(
        "End Date",
        value=datetime(2024, 3, 31),
        max_value=datetime.now()
    )

# Validate dates
if start_date >= end_date:
    st.sidebar.error("Start date must be before end date")

# Example queries
st.sidebar.markdown("---")
st.sidebar.header("💡 Example Queries")
example_queries = [
    "Backtest RSI(14) + SMA(20) crossover. Enter long when RSI < 30 and Close > SMA(20). Exit when RSI > 70.",
    "Show me Bollinger Bands squeeze on this data. Plot the bands and identify squeeze periods.",
    "Find support and resistance levels using pivot points. Mark them on a chart.",
    "Backtest mean reversion strategy: buy when RSI(2) < 20, sell when RSI(2) > 80.",
    "Calculate MACD crossover strategy. Enter long on bullish crossover, exit on bearish crossover.",
    "Analyze volume patterns. Show volume moving average and identify unusual volume spikes.",
]

selected_example = st.sidebar.selectbox(
    "Load Example",
    options=["Custom Query"] + [f"Example {i+1}" for i in range(len(example_queries))],
    index=0
)

# Main content area
st.header("📝 Strategy Query")

# Query input
if selected_example != "Custom Query":
    example_idx = int(selected_example.split()[-1]) - 1
    default_query = example_queries[example_idx]
else:
    default_query = ""

query = st.text_area(
    "Enter your trading strategy or analysis request (Natural Language)",
    value=default_query,
    height=150,
    help="Describe what you want to analyze or backtest in natural language. CodeAct will write and execute the code for you."
)

# Run analysis button
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    run_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ Clear", use_container_width=True)

if clear_button:
    st.rerun()

# Execute analysis
if run_button:
    if not query.strip():
        st.error("Please enter a query")
    elif start_date >= end_date:
        st.error("Please fix the date range")
    else:
        # Prepare request
        payload = {
            "query": query,
            "symbol": symbol,
            "interval": interval,
            "start_date": str(start_date),
            "end_date": str(end_date)
        }
        
        # Show progress
        with st.spinner("🤖 CodeAct is analyzing your strategy..."):
            try:
                # Make API request
                response = requests.post(api_url, json=payload, timeout=300)
                response.raise_for_status()
                result = response.json()
                
                # Store result in session state
                st.session_state['last_result'] = result
                st.session_state['last_query'] = query
                
            except requests.exceptions.RequestException as e:
                st.error(f"API request failed: {str(e)}")
                st.info("Make sure the API is running. For local testing, run: `python api.py`")
                result = None

# Display results
if 'last_result' in st.session_state and st.session_state['last_result']:
    result = st.session_state['last_result']
    
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    # Summary
    if "summary" in result:
        st.subheader("Summary")
        st.info(result["summary"])
    
    # Metrics
    if any(key in result for key in ["total_return_pct", "sharpe", "max_dd_pct", "trades", "win_rate_pct"]):
        st.subheader("Key Metrics")
        
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
                    st.metric(label, f"{value:.2f}{unit}" if isinstance(value, (int, float)) else str(value))
    
    # Plot
    if "plot" in result and result["plot"]:
        plot_path = result["plot"]
        if os.path.exists(plot_path):
            st.subheader("Visualization")
            st.image(plot_path, use_container_width=True)
        else:
            st.warning(f"Plot file not found: {plot_path}")
    
    # Full JSON response
    with st.expander("📄 Full Response (JSON)"):
        st.json(result)
    
    # Metadata
    if "symbol" in result:
        st.caption(f"Symbol: {result.get('symbol')} | Interval: {result.get('interval')} | "
                  f"Date Range: {result.get('start_date')} to {result.get('end_date')} | "
                  f"Data Points: {result.get('data_points', 'N/A')}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Powered by CodeAct • Natural Language Trading Analysis</p>
        <p>Built with FastAPI, Streamlit, and CodeAct Agent</p>
    </div>
    """,
    unsafe_allow_html=True
)

