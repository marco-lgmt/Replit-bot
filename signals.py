"""
Trading signals module for forex trading bot.
Defines trading signal structure and types.
"""

from dataclasses import dataclass
from typing import Literal, Dict, Any
import time

# Define signal type literal
SignalType = Literal["BUY", "SELL", "NEUTRAL"]

@dataclass
class TradingSignal:
    """
    Represents a trading signal with relevant information.
    """
    symbol: str  # Forex pair symbol
    signal_type: SignalType  # BUY, SELL, or NEUTRAL
    strength: float  # Signal strength (0.0 to 1.0)
    price: float  # Current price
    rsi: float  # RSI indicator value
    ema_fast: float  # Fast EMA value
    ema_slow: float  # Slow EMA value
    timestamp: float  # Unix timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert trading signal to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the signal
        """
        return {
            "symbol": self.symbol,
            "signal_type": self.signal_type,
            "strength": self.strength,
            "price": self.price,
            "rsi": self.rsi,
            "ema_fast": self.ema_fast,
            "ema_slow": self.ema_slow,
            "timestamp": self.timestamp,
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))
        }
    
    def __repr__(self) -> str:
        """
        String representation of the trading signal.
        
        Returns:
            str: String representation
        """
        return (f"Signal({self.symbol}, {self.signal_type}, strength={self.strength:.2f}, "
                f"RSI={self.rsi:.2f}, EMA_fast={self.ema_fast:.5f}, EMA_slow={self.ema_slow:.5f})")
    
    @property
    def is_actionable(self) -> bool:
        """
        Check if the signal is actionable (BUY or SELL with sufficient strength).
        
        Returns:
            bool: True if actionable, False otherwise
        """
        return self.signal_type in ("BUY", "SELL") and self.strength >= 0.5

def combine_signals(signals: Dict[str, SignalType], 
                   strengths: Dict[str, float]) -> Dict[str, TradingSignal]:
    """
    Combine multiple signal sources into a single set of trading signals.
    
    Args:
        signals (Dict[str, SignalType]): Dictionary of signal types by source
        strengths (Dict[str, float]): Dictionary of signal strengths by source
        
    Returns:
        Dict[str, TradingSignal]: Combined trading signals
    """
    # This is a placeholder implementation that would be expanded in a real system
    # to handle combining signals from different indicators with different weights
    return {}
