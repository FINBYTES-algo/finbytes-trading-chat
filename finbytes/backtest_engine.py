"""
Backtesting Engine
Provides strategy backtesting functionality using vectorbt.
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Callable, Tuple
import logging

try:
    import vectorbt as vbt
    VBT_AVAILABLE = True
except ImportError:
    VBT_AVAILABLE = False
    logging.warning("vectorbt not available. Backtesting will use simplified calculations.")

from .analysis_engine import AnalysisEngine

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Engine for backtesting trading strategies.
    """
    
    def __init__(self, df: pd.DataFrame, initial_capital: float = 10000.0):
        """
        Initialize backtesting engine.
        
        Args:
            df: DataFrame with OHLC data
            initial_capital: Starting capital for backtest
        """
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.analysis = AnalysisEngine(self.df)
        
        if not VBT_AVAILABLE:
            logger.warning("vectorbt not available. Using simplified backtesting.")
    
    def simple_backtest(
        self,
        signals: pd.Series,
        entry_price: Optional[pd.Series] = None,
        exit_price: Optional[pd.Series] = None
    ) -> Dict:
        """
        Simple backtest using buy/sell signals.
        
        Args:
            signals: Series with 1 for buy, -1 for sell, 0 for hold
            entry_price: Price to enter (default: Close)
            exit_price: Price to exit (default: Close)
        
        Returns:
            Dictionary with backtest results
        """
        if entry_price is None:
            entry_price = self.df['Close']
        if exit_price is None:
            exit_price = self.df['Close']
        
        # Calculate positions
        positions = signals.replace(0, np.nan).ffill().fillna(0)
        
        # Calculate returns
        returns = exit_price.pct_change()
        strategy_returns = positions.shift(1) * returns
        
        # Calculate equity curve
        equity = (1 + strategy_returns).cumprod() * self.initial_capital
        
        # Calculate metrics
        total_return = (equity.iloc[-1] / self.initial_capital - 1) * 100
        total_return_pct = total_return
        
        # Calculate trades
        trades = self._calculate_trades(positions, entry_price, exit_price)
        
        # Calculate performance metrics
        sharpe = self._calculate_sharpe(strategy_returns)
        max_drawdown = self._calculate_max_drawdown(equity)
        win_rate = self._calculate_win_rate(trades)
        
        # Calculate additional trade statistics
        if trades:
            winning_trades = [t for t in trades if t['win']]
            losing_trades = [t for t in trades if not t['win']]
            avg_win = sum(t['pnl_pct'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
            avg_loss = sum(t['pnl_pct'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
            largest_win = max((t['pnl_pct'] for t in trades), default=0)
            largest_loss = min((t['pnl_pct'] for t in trades), default=0)
        else:
            avg_win = avg_loss = largest_win = largest_loss = 0
        
        return {
            'total_return_pct': total_return_pct,
            'sharpe': sharpe,
            'max_dd_pct': max_drawdown,
            'trades': len(trades),
            'win_rate_pct': win_rate,
            'equity_curve': equity,
            'returns': strategy_returns,
            'trades_detail': trades,
            'final_equity': equity.iloc[-1],
            'avg_win_pct': round(avg_win, 2),
            'avg_loss_pct': round(avg_loss, 2),
            'largest_win_pct': round(largest_win, 2),
            'largest_loss_pct': round(largest_loss, 2),
            'winning_trades': len(winning_trades) if trades else 0,
            'losing_trades': len(losing_trades) if trades else 0
        }
    
    def sma_crossover_backtest(
        self,
        fast_period: int = 10,
        slow_period: int = 20
    ) -> Dict:
        """
        Backtest SMA crossover strategy.
        
        Args:
            fast_period: Fast SMA period
            slow_period: Slow SMA period
        
        Returns:
            Backtest results
        """
        fast_sma = self.analysis.sma(fast_period)
        slow_sma = self.analysis.sma(slow_period)
        
        # Generate signals: 1 when fast crosses above slow, -1 when below
        signals = pd.Series(0, index=self.df.index)
        signals[fast_sma > slow_sma] = 1
        signals[fast_sma < slow_sma] = -1
        
        # Only trade on crossovers
        crossover_up = (fast_sma > slow_sma) & (fast_sma.shift(1) <= slow_sma.shift(1))
        crossover_down = (fast_sma < slow_sma) & (fast_sma.shift(1) >= slow_sma.shift(1))
        
        signals = pd.Series(0, index=self.df.index)
        signals[crossover_up] = 1
        signals[crossover_down] = -1
        
        return self.simple_backtest(signals)
    
    def rsi_strategy_backtest(
        self,
        rsi_period: int = 14,
        oversold: float = 30,
        overbought: float = 70
    ) -> Dict:
        """
        Backtest RSI-based strategy.
        Buy when RSI < oversold, sell when RSI > overbought.
        
        Args:
            rsi_period: RSI period
            oversold: Oversold threshold
            overbought: Overbought threshold
        
        Returns:
            Backtest results
        """
        rsi = self.analysis.rsi(rsi_period)
        
        signals = pd.Series(0, index=self.df.index)
        signals[rsi < oversold] = 1  # Buy signal
        signals[rsi > overbought] = -1  # Sell signal
        
        return self.simple_backtest(signals)
    
    def macd_crossover_backtest(
        self,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict:
        """
        Backtest MACD crossover strategy.
        
        Args:
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
        
        Returns:
            Backtest results
        """
        macd_data = self.analysis.macd(fast, slow, signal)
        macd_line = macd_data['macd']
        signal_line = macd_data['signal']
        
        # Generate signals on crossovers
        signals = pd.Series(0, index=self.df.index)
        bullish_cross = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
        bearish_cross = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))
        
        signals[bullish_cross] = 1
        signals[bearish_cross] = -1
        
        return self.simple_backtest(signals)
    
    def custom_strategy_backtest(
        self,
        entry_condition: Callable,
        exit_condition: Callable
    ) -> Dict:
        """
        Backtest a custom strategy defined by entry/exit conditions.
        
        Args:
            entry_condition: Function that takes (df, i) and returns True to enter
            exit_condition: Function that takes (df, i) and returns True to exit
        
        Returns:
            Backtest results
        """
        signals = pd.Series(0, index=self.df.index)
        position = 0
        
        for i in range(1, len(self.df)):
            if position == 0 and entry_condition(self.df, i):
                signals.iloc[i] = 1
                position = 1
            elif position == 1 and exit_condition(self.df, i):
                signals.iloc[i] = -1
                position = 0
        
        return self.simple_backtest(signals)
    
    def _calculate_trades(
        self,
        positions: pd.Series,
        entry_price: pd.Series,
        exit_price: pd.Series
    ) -> list:
        """Calculate individual trades from positions."""
        trades = []
        in_position = False
        entry_idx = None
        entry_price_val = None
        entry_date = None
        
        for i in range(len(positions)):
            if positions.iloc[i] == 1 and not in_position:
                # Enter long
                in_position = True
                entry_idx = i
                entry_price_val = entry_price.iloc[i]
                entry_date = self.df.index[i] if hasattr(self.df.index[i], 'strftime') else str(self.df.index[i])
            elif positions.iloc[i] == -1 and in_position:
                # Exit long
                exit_price_val = exit_price.iloc[i]
                exit_date = self.df.index[i] if hasattr(self.df.index[i], 'strftime') else str(self.df.index[i])
                pnl = (exit_price_val - entry_price_val) / entry_price_val * 100
                pnl_amount = exit_price_val - entry_price_val
                duration = (i - entry_idx) if entry_idx is not None else 0
                
                # Ensure all values are JSON serializable
                entry_date_str = entry_date.strftime('%Y-%m-%d') if hasattr(entry_date, 'strftime') else str(entry_date)
                exit_date_str = exit_date.strftime('%Y-%m-%d') if hasattr(exit_date, 'strftime') else str(exit_date)
                
                trades.append({
                    'trade_number': int(len(trades) + 1),
                    'entry_date': str(entry_date_str),
                    'exit_date': str(exit_date_str),
                    'entry_price': float(round(entry_price_val, 2)),
                    'exit_price': float(round(exit_price_val, 2)),
                    'entry_idx': int(entry_idx) if entry_idx is not None else None,
                    'exit_idx': int(i),
                    'pnl_pct': float(round(pnl, 2)),
                    'pnl_amount': float(round(pnl_amount, 2)),
                    'duration_periods': int(duration),
                    'win': bool(pnl > 0)
                })
                in_position = False
        
        return trades
    
    def _calculate_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    def _calculate_max_drawdown(self, equity: pd.Series) -> float:
        """Calculate maximum drawdown percentage."""
        if len(equity) == 0:
            return 0.0
        
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max * 100
        return abs(drawdown.min())
    
    def _calculate_win_rate(self, trades: list) -> float:
        """Calculate win rate percentage."""
        if len(trades) == 0:
            return 0.0
        
        wins = sum(1 for trade in trades if trade['win'])
        return (wins / len(trades)) * 100
    
    def vectorbt_backtest(
        self,
        entries: pd.Series,
        exits: pd.Series,
        **kwargs
    ) -> Dict:
        """
        Backtest using vectorbt (if available).
        
        Args:
            entries: Boolean series for entry signals
            exits: Boolean series for exit signals
            **kwargs: Additional vectorbt parameters
        
        Returns:
            Backtest results
        """
        if not VBT_AVAILABLE:
            logger.warning("vectorbt not available, using simple backtest")
            signals = pd.Series(0, index=self.df.index)
            signals[entries] = 1
            signals[exits] = -1
            return self.simple_backtest(signals)
        
        try:
            # Use vectorbt for more sophisticated backtesting
            pf = vbt.Portfolio.from_signals(
                self.df['Close'],
                entries=entries,
                exits=exits,
                init_cash=self.initial_capital,
                **kwargs
            )
            
            stats = pf.stats()
            
            return {
                'total_return_pct': stats['Total Return [%]'],
                'sharpe': stats['Sharpe Ratio'],
                'max_dd_pct': abs(stats['Max Drawdown [%]']),
                'trades': stats['# Trades'],
                'win_rate_pct': stats['Win Rate [%]'],
                'equity_curve': pf.value(),
                'portfolio': pf
            }
        except Exception as e:
            logger.error(f"vectorbt backtest failed: {e}")
            # Fallback to simple backtest
            signals = pd.Series(0, index=self.df.index)
            signals[entries] = 1
            signals[exits] = -1
            return self.simple_backtest(signals)

