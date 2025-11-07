"""
Test script for CodeAct trader functionality.
Run with: python test_trader.py
"""
import json
import logging
from finbytes.codeact_trader import TraderCodeAct

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Test the CodeAct trader with a sample query."""
    
    print("=" * 60)
    print("FinBytes CodeAct Trader - Test Script")
    print("=" * 60)
    print()
    
    # Initialize trader
    print("Initializing CodeAct agent...")
    try:
        trader = TraderCodeAct()
        print("✓ CodeAct agent initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize CodeAct agent: {e}")
        print("\nMake sure you have installed codeact:")
        print("  pip install codeact")
        return
    
    print()
    
    # Test query
    test_query = """
    Backtest RSI(14) + SMA(20) crossover strategy on AAPL weekly data.
    Enter long when RSI < 30 and Close > SMA(20).
    Exit when RSI > 70.
    Use vectorbt for backtesting. Plot equity curve.
    Calculate total return, Sharpe ratio, max drawdown, number of trades, and win rate.
    """
    
    print("Test Query:")
    print("-" * 60)
    print(test_query)
    print("-" * 60)
    print()
    
    # Execute analysis
    print("Executing analysis...")
    print("This may take a few minutes as CodeAct writes and executes code...")
    print()
    
    try:
        result = trader.analyze(
            user_query=test_query,
            symbol="AAPL",
            interval="1w",
            start_date="2024-01-01",
            end_date="2024-03-31"
        )
        
        print("=" * 60)
        print("Results:")
        print("=" * 60)
        print()
        print(json.dumps(result, indent=2))
        print()
        
        # Display key metrics
        if "error" not in result:
            print("Key Metrics:")
            print("-" * 60)
            if result.get("total_return_pct") is not None:
                print(f"Total Return: {result['total_return_pct']:.2f}%")
            if result.get("sharpe") is not None:
                print(f"Sharpe Ratio: {result['sharpe']:.2f}")
            if result.get("max_dd_pct") is not None:
                print(f"Max Drawdown: {result['max_dd_pct']:.2f}%")
            if result.get("trades") is not None:
                print(f"Number of Trades: {result['trades']}")
            if result.get("win_rate_pct") is not None:
                print(f"Win Rate: {result['win_rate_pct']:.2f}%")
            print()
            
            if result.get("plot"):
                print(f"Plot saved to: {result['plot']}")
        else:
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

