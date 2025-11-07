"""
Simple Trader - Works without CodeAct
Provides basic trading analysis functionality that doesn't require CodeAct.
"""
import pandas as pd
import json
import logging
from typing import Dict, Optional
import tempfile
import os

from .ohlca_api import fetch_ohlc_data
from .analysis_engine import AnalysisEngine
from .backtest_engine import BacktestEngine

logger = logging.getLogger(__name__)


class SimpleTrader:
    """
    Simple trader that works without CodeAct.
    Provides basic analysis and backtesting capabilities.
    """
    
    def analyze(
        self,
        user_query: str,
        symbol: str,
        interval: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Analyze trading data based on query.
        Supports simple queries without CodeAct.
        
        Args:
            user_query: Natural language or simple query
            symbol: Stock symbol
            interval: Time interval
            start_date: Start date
            end_date: End date
        
        Returns:
            Analysis results
        """
        try:
            # Fetch data
            logger.info(f"Fetching OHLC data for {symbol}")
            df = fetch_ohlc_data(symbol, interval, start_date, end_date)
            
            # Initialize engines
            analysis = AnalysisEngine(df)
            backtest = BacktestEngine(df)
            
            # Parse query and execute
            query_lower = user_query.lower()
            
            # RSI strategy
            if 'rsi' in query_lower and ('backtest' in query_lower or 'strategy' in query_lower):
                return self._handle_rsi_backtest(analysis, backtest, query_lower, df)
            
            # SMA crossover
            elif 'sma' in query_lower and ('crossover' in query_lower or 'cross' in query_lower):
                return self._handle_sma_backtest(analysis, backtest, query_lower, df)
            
            # MACD strategy
            elif 'macd' in query_lower:
                return self._handle_macd_backtest(analysis, backtest, query_lower, df)
            
            # Bollinger Bands
            elif 'bollinger' in query_lower or 'bb' in query_lower:
                return self._handle_bollinger_analysis(analysis, df)
            
            # Support/Resistance
            elif 'support' in query_lower or 'resistance' in query_lower:
                return self._handle_support_resistance(analysis, df)
            
            # General analysis
            elif 'analyze' in query_lower or 'calculate' in query_lower or 'show' in query_lower:
                return self._handle_general_analysis(analysis, df, user_query)
            
            # Default: return summary
            else:
                return self._handle_default_analysis(analysis, df)
                
        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "summary": f"Analysis failed: {str(e)}",
                "symbol": symbol,
                "interval": interval,
                "start_date": start_date,
                "end_date": end_date
            }
    
    def _handle_rsi_backtest(self, analysis, backtest, query, df):
        """Handle RSI backtest query."""
        # Extract parameters
        rsi_period = 14
        oversold = 30
        overbought = 70
        
        if 'rsi(' in query:
            try:
                # Try to extract RSI period
                start = query.find('rsi(') + 4
                end = query.find(')', start)
                if end > start:
                    rsi_period = int(query[start:end])
            except:
                pass
        
        result = backtest.rsi_strategy_backtest(rsi_period, oversold, overbought)
        
        return {
            "summary": f"RSI({rsi_period}) strategy: {result['total_return_pct']:.2f}% return, "
                      f"Sharpe {result['sharpe']:.2f}, {result['trades']} trades",
            "total_return_pct": result['total_return_pct'],
            "sharpe": result['sharpe'],
            "max_dd_pct": result['max_dd_pct'],
            "trades": result['trades'],
            "win_rate_pct": result['win_rate_pct'],
            "trades_detail": result.get('trades_detail', []),
            "avg_win_pct": result.get('avg_win_pct', 0),
            "avg_loss_pct": result.get('avg_loss_pct', 0),
            "largest_win_pct": result.get('largest_win_pct', 0),
            "largest_loss_pct": result.get('largest_loss_pct', 0),
            "winning_trades": result.get('winning_trades', 0),
            "losing_trades": result.get('losing_trades', 0),
            "symbol": df.index[0] if len(df) > 0 else None,
            "data_points": len(df)
        }
    
    def _handle_sma_backtest(self, analysis, backtest, query, df):
        """Handle SMA crossover backtest."""
        fast = 10
        slow = 20
        
        # Try to extract periods
        if 'sma(' in query:
            try:
                start = query.find('sma(') + 4
                end = query.find(')', start)
                if end > start:
                    slow = int(query[start:end])
            except:
                pass
        
        result = backtest.sma_crossover_backtest(fast, slow)
        
        return {
            "summary": f"SMA({fast}/{slow}) crossover: {result['total_return_pct']:.2f}% return",
            "total_return_pct": result['total_return_pct'],
            "sharpe": result['sharpe'],
            "max_dd_pct": result['max_dd_pct'],
            "trades": result['trades'],
            "win_rate_pct": result['win_rate_pct'],
            "trades_detail": result.get('trades_detail', []),
            "avg_win_pct": result.get('avg_win_pct', 0),
            "avg_loss_pct": result.get('avg_loss_pct', 0),
            "largest_win_pct": result.get('largest_win_pct', 0),
            "largest_loss_pct": result.get('largest_loss_pct', 0),
            "winning_trades": result.get('winning_trades', 0),
            "losing_trades": result.get('losing_trades', 0),
            "data_points": len(df)
        }
    
    def _handle_macd_backtest(self, analysis, backtest, query, df):
        """Handle MACD backtest."""
        result = backtest.macd_crossover_backtest()
        
        return {
            "summary": f"MACD crossover: {result['total_return_pct']:.2f}% return",
            "total_return_pct": result['total_return_pct'],
            "sharpe": result['sharpe'],
            "max_dd_pct": result['max_dd_pct'],
            "trades": result['trades'],
            "win_rate_pct": result['win_rate_pct'],
            "trades_detail": result.get('trades_detail', []),
            "avg_win_pct": result.get('avg_win_pct', 0),
            "avg_loss_pct": result.get('avg_loss_pct', 0),
            "largest_win_pct": result.get('largest_win_pct', 0),
            "largest_loss_pct": result.get('largest_loss_pct', 0),
            "winning_trades": result.get('winning_trades', 0),
            "losing_trades": result.get('losing_trades', 0),
            "data_points": len(df)
        }
    
    def _handle_bollinger_analysis(self, analysis, df):
        """Handle Bollinger Bands analysis."""
        bb = analysis.bollinger_bands()
        current_price = df['Close'].iloc[-1]
        upper = bb['upper'].iloc[-1]
        lower = bb['lower'].iloc[-1]
        
        squeeze = (upper - lower) / current_price < 0.02
        
        return {
            "summary": f"Bollinger Bands: Upper={upper:.2f}, Lower={lower:.2f}, "
                      f"Current={current_price:.2f}. {'Squeeze detected!' if squeeze else ''}",
            "bollinger_upper": float(upper),
            "bollinger_lower": float(lower),
            "bollinger_middle": float(bb['middle'].iloc[-1]),
            "current_price": float(current_price),
            "squeeze": squeeze,
            "data_points": len(df)
        }
    
    def _handle_support_resistance(self, analysis, df):
        """Handle support/resistance analysis."""
        levels = analysis.find_support_resistance()
        
        return {
            "summary": f"Found {len(levels['support'])} support and {len(levels['resistance'])} resistance levels",
            "support_levels": levels['support'],
            "resistance_levels": levels['resistance'],
            "data_points": len(df)
        }
    
    def _handle_general_analysis(self, analysis, df, query):
        """Handle general analysis queries."""
        summary = analysis.get_summary()
        stats = summary['statistics']
        
        return {
            "summary": f"Analysis: {stats['price_change_pct']:.2f}% change, "
                      f"Volatility: {stats['volatility']:.2f}, Sharpe: {stats['sharpe_ratio']:.2f}",
            "statistics": stats,
            "indicators": summary['indicators'],
            "data_points": len(df)
        }
    
    def _handle_default_analysis(self, analysis, df):
        """Handle default analysis."""
        summary = analysis.get_summary()
        
        return {
            "summary": "Basic analysis completed",
            "statistics": summary['statistics'],
            "indicators": summary['indicators'],
            "data_points": len(df)
        }

