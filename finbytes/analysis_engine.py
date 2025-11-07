"""
Technical Analysis Engine
Provides functions for calculating technical indicators and performing analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging

try:
    import ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    logging.warning("ta library not available. Some indicators may not work.")

logger = logging.getLogger(__name__)


class AnalysisEngine:
    """
    Engine for technical analysis calculations.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with OHLC data.
        
        Args:
            df: DataFrame with columns: Open, High, Low, Close, Volume
                Index should be datetime
        """
        self.df = df.copy()
        self._validate_data()
    
    def _validate_data(self):
        """Validate that required columns exist."""
        required = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    # Moving Averages
    def sma(self, period: int = 20, column: str = 'Close') -> pd.Series:
        """Simple Moving Average"""
        return self.df[column].rolling(window=period).mean()
    
    def ema(self, period: int = 20, column: str = 'Close') -> pd.Series:
        """Exponential Moving Average"""
        return self.df[column].ewm(span=period, adjust=False).mean()
    
    def wma(self, period: int = 20, column: str = 'Close') -> pd.Series:
        """Weighted Moving Average"""
        weights = np.arange(1, period + 1)
        return self.df[column].rolling(window=period).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )
    
    # Momentum Indicators
    def rsi(self, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        if TA_AVAILABLE:
            from ta.momentum import RSIIndicator
            return RSIIndicator(self.df['Close'], window=period).rsi()
        else:
            # Manual calculation
            delta = self.df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
    
    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = self.ema(fast)
        ema_slow = self.ema(slow)
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def stochastic(self, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """Stochastic Oscillator"""
        low_min = self.df['Low'].rolling(window=k_period).min()
        high_max = self.df['High'].rolling(window=k_period).max()
        k_percent = 100 * ((self.df['Close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k': k_percent,
            'd': d_percent
        }
    
    # Volatility Indicators
    def bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """Bollinger Bands"""
        sma = self.sma(period)
        std = self.df['Close'].rolling(window=period).std()
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    def atr(self, period: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = self.df['High'] - self.df['Low']
        high_close = np.abs(self.df['High'] - self.df['Close'].shift())
        low_close = np.abs(self.df['Low'] - self.df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        return true_range.rolling(window=period).mean()
    
    # Volume Indicators
    def volume_sma(self, period: int = 20) -> pd.Series:
        """Volume Simple Moving Average"""
        return self.df['Volume'].rolling(window=period).mean()
    
    def obv(self) -> pd.Series:
        """On-Balance Volume"""
        obv = (np.sign(self.df['Close'].diff()) * self.df['Volume']).fillna(0).cumsum()
        return obv
    
    # Support and Resistance
    def find_support_resistance(self, window: int = 5, min_touches: int = 2) -> Dict[str, list]:
        """
        Find support and resistance levels.
        
        Args:
            window: Window size for local min/max detection
            min_touches: Minimum number of touches to consider a level
        
        Returns:
            Dictionary with 'support' and 'resistance' lists
        """
        highs = self.df['High'].rolling(window=window, center=True).max()
        lows = self.df['Low'].rolling(window=window, center=True).min()
        
        # Find local maxima (resistance)
        resistance_levels = []
        for i in range(window, len(self.df) - window):
            if self.df['High'].iloc[i] == highs.iloc[i]:
                level = self.df['High'].iloc[i]
                # Count touches
                touches = ((self.df['High'] >= level * 0.98) & 
                          (self.df['High'] <= level * 1.02)).sum()
                if touches >= min_touches:
                    resistance_levels.append(level)
        
        # Find local minima (support)
        support_levels = []
        for i in range(window, len(self.df) - window):
            if self.df['Low'].iloc[i] == lows.iloc[i]:
                level = self.df['Low'].iloc[i]
                # Count touches
                touches = ((self.df['Low'] >= level * 0.98) & 
                          (self.df['Low'] <= level * 1.02)).sum()
                if touches >= min_touches:
                    support_levels.append(level)
        
        # Remove duplicates and sort
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:5]
        support_levels = sorted(list(set(support_levels)))[:5]
        
        return {
            'support': support_levels,
            'resistance': resistance_levels
        }
    
    # Pattern Detection
    def detect_patterns(self) -> Dict[str, list]:
        """
        Detect common candlestick patterns.
        Returns dictionary with pattern names and indices where they occur.
        """
        patterns = {
            'doji': [],
            'hammer': [],
            'engulfing_bullish': [],
            'engulfing_bearish': []
        }
        
        for i in range(1, len(self.df)):
            open_price = self.df['Open'].iloc[i]
            close_price = self.df['Close'].iloc[i]
            high_price = self.df['High'].iloc[i]
            low_price = self.df['Low'].iloc[i]
            
            body = abs(close_price - open_price)
            upper_shadow = high_price - max(open_price, close_price)
            lower_shadow = min(open_price, close_price) - low_price
            total_range = high_price - low_price
            
            # Doji pattern
            if total_range > 0 and body / total_range < 0.1:
                patterns['doji'].append(i)
            
            # Hammer pattern
            if lower_shadow > 2 * body and upper_shadow < body and close_price > open_price:
                patterns['hammer'].append(i)
            
            # Engulfing patterns
            if i > 0:
                prev_open = self.df['Open'].iloc[i-1]
                prev_close = self.df['Close'].iloc[i-1]
                
                # Bullish engulfing
                if (prev_close < prev_open and  # Previous candle bearish
                    close_price > open_price and  # Current candle bullish
                    open_price < prev_close and
                    close_price > prev_open):
                    patterns['engulfing_bullish'].append(i)
                
                # Bearish engulfing
                if (prev_close > prev_open and  # Previous candle bullish
                    close_price < open_price and  # Current candle bearish
                    open_price > prev_close and
                    close_price < prev_open):
                    patterns['engulfing_bearish'].append(i)
        
        return patterns
    
    # Statistical Analysis
    def calculate_statistics(self) -> Dict[str, float]:
        """Calculate basic statistics."""
        returns = self.df['Close'].pct_change().dropna()
        
        return {
            'mean_return': returns.mean(),
            'std_return': returns.std(),
            'sharpe_ratio': (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
            'max_gain': returns.max(),
            'max_loss': returns.min(),
            'volatility': returns.std() * np.sqrt(252),
            'current_price': self.df['Close'].iloc[-1],
            'price_change_pct': ((self.df['Close'].iloc[-1] - self.df['Close'].iloc[0]) / self.df['Close'].iloc[0]) * 100
        }
    
    def get_summary(self) -> Dict:
        """Get comprehensive analysis summary."""
        return {
            'statistics': self.calculate_statistics(),
            'support_resistance': self.find_support_resistance(),
            'patterns': self.detect_patterns(),
            'indicators': {
                'rsi': self.rsi().iloc[-1] if len(self.df) >= 14 else None,
                'sma_20': self.sma(20).iloc[-1] if len(self.df) >= 20 else None,
                'sma_50': self.sma(50).iloc[-1] if len(self.df) >= 50 else None,
            }
        }


# Convenience functions
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate common indicators and add to DataFrame.
    
    Args:
        df: OHLC DataFrame
    
    Returns:
        DataFrame with added indicator columns
    """
    engine = AnalysisEngine(df)
    result = df.copy()
    
    # Add indicators
    result['SMA_20'] = engine.sma(20)
    result['SMA_50'] = engine.sma(50)
    result['EMA_20'] = engine.ema(20)
    result['RSI'] = engine.rsi()
    
    macd_data = engine.macd()
    result['MACD'] = macd_data['macd']
    result['MACD_Signal'] = macd_data['signal']
    result['MACD_Hist'] = macd_data['histogram']
    
    bb = engine.bollinger_bands()
    result['BB_Upper'] = bb['upper']
    result['BB_Middle'] = bb['middle']
    result['BB_Lower'] = bb['lower']
    
    return result

