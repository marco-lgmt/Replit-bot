"""
Forex Pairs module for trading bot.
Handles forex pair standardization and information.
"""

from typing import Dict, List

# Standard forex pairs supported by the bot
SUPPORTED_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", 
    "USD/CAD", "AUD/USD", "NZD/USD", "EUR/GBP",
    "EUR/JPY", "GBP/JPY", "USD/ZAR", "USD/MXN"
]

# Mapping between traditional notation and TradingView symbols
TRADINGVIEW_SYMBOL_MAPPING = {
    "EUR/USD": "EURUSD",
    "GBP/USD": "GBPUSD",
    "USD/JPY": "USDJPY",
    "USD/CHF": "USDCHF",
    "USD/CAD": "USDCAD",
    "AUD/USD": "AUDUSD",
    "NZD/USD": "NZDUSD",
    "EUR/GBP": "EURGBP",
    "EUR/JPY": "EURJPY",
    "GBP/JPY": "GBPJPY",
    "USD/ZAR": "USDZAR",
    "USD/MXN": "USDMXN"
}

# Pip size for each pair
PIP_SIZE = {
    "EUR/USD": 0.0001,
    "GBP/USD": 0.0001,
    "USD/JPY": 0.01,
    "USD/CHF": 0.0001,
    "USD/CAD": 0.0001,
    "AUD/USD": 0.0001,
    "NZD/USD": 0.0001,
    "EUR/GBP": 0.0001,
    "EUR/JPY": 0.01,
    "GBP/JPY": 0.01,
    "USD/ZAR": 0.0001,
    "USD/MXN": 0.0001
}

def standardize_pair_format(pair: str) -> str:
    """
    Convert traditional forex pair notation to TradingView format.
    
    Args:
        pair (str): Forex pair in traditional format (e.g., "GBP/USD")
        
    Returns:
        str: Forex pair in TradingView format (e.g., "GBPUSD")
    """
    # Check if the pair is already in the TradingView format
    if "/" not in pair:
        return pair
        
    # Convert traditional notation to TradingView format
    return TRADINGVIEW_SYMBOL_MAPPING.get(pair, pair.replace("/", ""))

def get_pip_value(pair: str) -> float:
    """
    Get the pip value for a forex pair.
    
    Args:
        pair (str): Forex pair (e.g., "GBP/USD")
        
    Returns:
        float: Value of 1 pip in price units
    """
    return PIP_SIZE.get(pair, 0.0001)

def get_supported_pairs() -> List[str]:
    """
    Get the list of supported forex pairs.
    
    Returns:
        List[str]: List of supported forex pairs
    """
    return SUPPORTED_PAIRS
