"""
Example usage of FinBytes CodeAct Trading Analysis System.
This script demonstrates how to use the system programmatically.
"""
import json
from finbytes.codeact_trader import TraderCodeAct
from finbytes.ohlca_api import fetch_ohlc_data

def example_1_fetch_data():
    """Example 1: Fetch OHLC data directly."""
    print("=" * 60)
    print("Example 1: Fetching OHLC Data")
    print("=" * 60)
    
    df = fetch_ohlc_data(
        symbol="AAPL",
        interval="1w",
        start_date="2024-01-01",
        end_date="2024-03-31"
    )
    
    print(f"\nFetched {len(df)} rows")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nLast 5 rows:")
    print(df.tail())
    print()


def example_2_simple_analysis():
    """Example 2: Simple analysis using CodeAct."""
    print("=" * 60)
    print("Example 2: Simple Analysis")
    print("=" * 60)
    
    trader = TraderCodeAct()
    
    result = trader.analyze(
        user_query="Calculate and plot the 20-day Simple Moving Average (SMA) and 50-day SMA on the close price.",
        symbol="AAPL",
        interval="1w",
        start_date="2024-01-01",
        end_date="2024-03-31"
    )
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    print()


def example_3_backtest_strategy():
    """Example 3: Backtest a trading strategy."""
    print("=" * 60)
    print("Example 3: Backtest Trading Strategy")
    print("=" * 60)
    
    trader = TraderCodeAct()
    
    query = """
    Backtest a simple moving average crossover strategy:
    - Calculate SMA(10) and SMA(20) on close price
    - Enter long when SMA(10) crosses above SMA(20)
    - Exit when SMA(10) crosses below SMA(20)
    - Use vectorbt for backtesting
    - Calculate and return: total return, Sharpe ratio, max drawdown, number of trades, win rate
    - Plot the equity curve
    """
    
    result = trader.analyze(
        user_query=query,
        symbol="AAPL",
        interval="1w",
        start_date="2024-01-01",
        end_date="2024-03-31"
    )
    
    print("\nBacktest Results:")
    if "error" not in result:
        print(f"Summary: {result.get('summary', 'N/A')}")
        print(f"Total Return: {result.get('total_return_pct', 'N/A')}%")
        print(f"Sharpe Ratio: {result.get('sharpe', 'N/A')}")
        print(f"Max Drawdown: {result.get('max_dd_pct', 'N/A')}%")
        print(f"Number of Trades: {result.get('trades', 'N/A')}")
        print(f"Win Rate: {result.get('win_rate_pct', 'N/A')}%")
    else:
        print(f"Error: {result.get('error')}")
    print()


def example_4_technical_indicators():
    """Example 4: Calculate technical indicators."""
    print("=" * 60)
    print("Example 4: Technical Indicators")
    print("=" * 60)
    
    trader = TraderCodeAct()
    
    query = """
    Calculate the following technical indicators:
    - RSI(14)
    - MACD (12, 26, 9)
    - Bollinger Bands (20, 2)
    - Volume Moving Average (20)
    
    Create a comprehensive chart showing:
    - Price with Bollinger Bands
    - RSI in a subplot
    - MACD in a subplot
    - Volume with volume MA in a subplot
    """
    
    result = trader.analyze(
        user_query=query,
        symbol="AAPL",
        interval="1w",
        start_date="2024-01-01",
        end_date="2024-03-31"
    )
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FinBytes CodeAct Trading Analysis - Examples")
    print("=" * 60 + "\n")
    
    # Run examples
    try:
        example_1_fetch_data()
        
        print("\n" + "=" * 60)
        print("Note: The following examples require CodeAct to be installed")
        print("and may take several minutes to execute.")
        print("=" * 60 + "\n")
        
        # Uncomment to run CodeAct examples
        # example_2_simple_analysis()
        # example_3_backtest_strategy()
        # example_4_technical_indicators()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

