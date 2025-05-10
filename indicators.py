"""
Technical indicators module for forex trading bot.
Implements various technical analysis indicators.
"""

from typing import List, Tuple, Dict, Any
import numpy as np

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate the Relative Strength Index (RSI) indicator.
    
    Args:
        prices (List[float]): List of price values
        period (int): RSI period
        
    Returns:
        float: RSI value
    """
    if len(prices) < period + 1:
        return 50  # Default value if not enough data
    
    # Calculate price changes
    deltas = np.diff(prices)
    
    # Separate gains and losses
    gains = np.copy(deltas)
    losses = np.copy(deltas)
    
    gains[gains < 0] = 0
    losses[losses > 0] = 0
    losses = abs(losses)
    
    # Calculate average gains and losses
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    if avg_loss == 0:
        return 100  # No losses means RSI = 100
    
    # Calculate initial RS
    rs = avg_gain / avg_loss
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_ema(prices: List[float], period: int) -> float:
    """
    Calculate the Exponential Moving Average (EMA) indicator.
    
    Args:
        prices (List[float]): List of price values
        period (int): EMA period
        
    Returns:
        float: EMA value
    """
    if len(prices) < period:
        return sum(prices) / len(prices)  # Simple average if not enough data
    
    # Calculate the multiplier
    multiplier = 2 / (period + 1)
    
    # Calculate the initial SMA
    ema = sum(prices[:period]) / period
    
    # Calculate EMA for each period
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return ema

def detect_ema_crossover(fast_ema: List[float], slow_ema: List[float]) -> str:
    """
    Detect EMA crossover signal type.
    
    Args:
        fast_ema (List[float]): Fast EMA values (shorter period)
        slow_ema (List[float]): Slow EMA values (longer period)
        
    Returns:
        str: Signal type ("BUY", "SELL", or "NEUTRAL")
    """
    if len(fast_ema) < 2 or len(slow_ema) < 2:
        return "NEUTRAL"  # Not enough data
    
    # Check current relationship
    current_fast = fast_ema[-1]
    current_slow = slow_ema[-1]
    
    # Check previous relationship
    prev_fast = fast_ema[-2]
    prev_slow = slow_ema[-2]
    
    # Detect crossover
    if prev_fast < prev_slow and current_fast > current_slow:
        return "BUY"  # Bullish crossover
    elif prev_fast > prev_slow and current_fast < current_slow:
        return "SELL"  # Bearish crossover
    else:
        return "NEUTRAL"  # No crossover

def calculate_macd(prices: List[float], fast_period: int = 12, 
                 slow_period: int = 26, signal_period: int = 9) -> Tuple[float, float, float]:
    """
    Calculate the Moving Average Convergence Divergence (MACD) indicator.
    
    Args:
        prices (List[float]): List of price values
        fast_period (int): Fast EMA period
        slow_period (int): Slow EMA period
        signal_period (int): Signal EMA period
        
    Returns:
        Tuple[float, float, float]: MACD line, signal line, and histogram
    """
    # Calculate fast and slow EMAs
    fast_ema = calculate_ema(prices, fast_period)
    slow_ema = calculate_ema(prices, slow_period)
    
    # Calculate MACD line
    macd_line = fast_ema - slow_ema
    
    # Calculate signal line (EMA of MACD line)
    signal_line = calculate_ema([macd_line], signal_period)
    
    # Calculate histogram
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def detect_support_resistance(prices: List[float], window: int = 10, 
                            threshold: float = 0.01) -> Dict[str, List[float]]:
    """
    Detect support and resistance levels in price data.
    
    Args:
        prices (List[float]): List of price values
        window (int): Window size for detecting levels
        threshold (float): Percentage threshold for level significance
        
    Returns:
        Dict[str, List[float]]: Dictionary with support and resistance levels
    """
    if len(prices) < window * 2:
        return {"support": [], "resistance": []}
    
    support_levels = []
    resistance_levels = []
    
    for i in range(window, len(prices) - window):
        # Get window of prices
        left_window = prices[i-window:i]
        right_window = prices[i:i+window]
        current_price = prices[i]
        
        # Check for local minima (support)
        if current_price <= min(left_window) and current_price <= min(right_window):
            support_levels.append(current_price)
        
        # Check for local maxima (resistance)
        if current_price >= max(left_window) and current_price >= max(right_window):
            resistance_levels.append(current_price)
    
    # Filter out levels that are too close to each other
    filtered_support = []
    for level in support_levels:
        if not any(abs(level - s) / level < threshold for s in filtered_support):
            filtered_support.append(level)
    
    filtered_resistance = []
    for level in resistance_levels:
        if not any(abs(level - r) / level < threshold for r in filtered_resistance):
            filtered_resistance.append(level)
    
    return {
        "support": filtered_support,
        "resistance": filtered_resistance
    }
