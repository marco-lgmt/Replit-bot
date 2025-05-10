"""
Utility functions for forex trading bot.
"""

import time
from datetime import datetime
from typing import List, Dict, Any

def format_currency(value: float, precision: int = 2) -> str:
    """
    Format a value as currency.
    
    Args:
        value (float): Value to format
        precision (int): Decimal precision
        
    Returns:
        str: Formatted currency string
    """
    return f"${value:.{precision}f}"

def format_pip_value(value: float, with_jpy: bool = False) -> str:
    """
    Format a value in pips, handling JPY pairs correctly.
    
    Args:
        value (float): Value to format
        with_jpy (bool): Whether the value is for a JPY pair
        
    Returns:
        str: Formatted pip value string
    """
    if with_jpy:
        return f"{value * 100:.1f} pips"
    else:
        return f"{value * 10000:.1f} pips"

def calculate_profit_loss(entry_price: float, current_price: float, 
                         lot_size: float, is_buy: bool, with_jpy: bool = False) -> float:
    """
    Calculate profit/loss for a position.
    
    Args:
        entry_price (float): Entry price
        current_price (float): Current price
        lot_size (float): Lot size
        is_buy (bool): Whether the position is a buy (True) or sell (False)
        with_jpy (bool): Whether the pair involves JPY
        
    Returns:
        float: Profit/loss amount
    """
    pip_factor = 0.01 if with_jpy else 0.0001
    lot_factor = 100000  # Standard lot size
    
    if is_buy:
        pip_difference = (current_price - entry_price) / pip_factor
    else:
        pip_difference = (entry_price - current_price) / pip_factor
    
    return pip_difference * pip_factor * lot_factor * lot_size

def humanize_time_ago(timestamp: float) -> str:
    """
    Convert a timestamp to a human-readable time ago string.
    
    Args:
        timestamp (float): Unix timestamp
        
    Returns:
        str: Human-readable time ago string
    """
    now = time.time()
    diff = now - timestamp
    
    if diff < 60:
        return f"{int(diff)} seconds ago"
    elif diff < 3600:
        return f"{int(diff / 60)} minutes ago"
    elif diff < 86400:
        return f"{int(diff / 3600)} hours ago"
    else:
        return f"{int(diff / 86400)} days ago"

def is_market_open() -> bool:
    """
    Check if forex market is currently open.
    
    Returns:
        bool: True if market is open, False otherwise
    """
    # Forex market is typically open 24/5 starting Sunday 5 PM ET to Friday 5 PM ET
    now = datetime.now()
    
    # Check if it's a weekend (Saturday=5, Sunday=6)
    if now.weekday() == 5:
        return False  # Saturday - market closed
    
    if now.weekday() == 6 and now.hour < 17:
        return False  # Sunday before 5 PM - market closed
    
    if now.weekday() == 4 and now.hour >= 17:
        return False  # Friday after 5 PM - market closed
    
    return True  # Market is open

def validate_trade_parameters(symbol: str, amount: float, take_profit: float, 
                            stop_loss: float) -> Dict[str, Any]:
    """
    Validate trade parameters.
    
    Args:
        symbol (str): Forex pair symbol
        amount (float): Trade amount
        take_profit (float): Take profit level
        stop_loss (float): Stop loss level
        
    Returns:
        Dict[str, Any]: Dictionary with validation result and errors
    """
    errors = []
    
    # Check symbol
    if not symbol or "/" not in symbol:
        errors.append("Invalid symbol format")
    
    # Check amount
    if amount <= 0:
        errors.append("Trade amount must be positive")
    
    # Check take profit
    if take_profit < 0:
        errors.append("Take profit must be non-negative")
    
    # Check stop loss
    if stop_loss < 0:
        errors.append("Stop loss must be non-negative")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
