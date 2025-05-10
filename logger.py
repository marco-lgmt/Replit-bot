"""
Logger module for forex trading bot.
Configures and provides logging functionality.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional

def setup_logger(log_level: str = "INFO", 
                 log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure logger.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (Optional[str]): Path to log file (None for console logging only)
        
    Returns:
        logging.Logger: Configured logger
    """
    # Map string log levels to logging constants
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    numeric_level = log_levels.get(log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Format for log messages
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Always add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
    else:
        # Create default log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        default_log_file = os.path.join(log_dir, f"forex_bot_{timestamp}.log")
        file_handler = logging.FileHandler(default_log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {default_log_file}")
    
    return logger

def log_trade(logger: logging.Logger, action: str, symbol: str, 
              price: float, amount: float, trade_id: Optional[str] = None) -> None:
    """
    Log trade information in a standardized format.
    
    Args:
        logger (logging.Logger): Logger instance
        action (str): Trade action (BUY, SELL, CLOSE)
        symbol (str): Trading symbol
        price (float): Trade price
        amount (float): Trade amount
        trade_id (Optional[str]): Trade ID (if available)
    """
    id_info = f" (ID: {trade_id})" if trade_id else ""
    logger.info(f"TRADE: {action} {symbol} @ {price:.5f} Amount: {amount:.2f}{id_info}")

def log_signal(logger: logging.Logger, symbol: str, signal_type: str, 
               strength: float, rsi: float, ema_fast: float, ema_slow: float) -> None:
    """
    Log trading signal information in a standardized format.
    
    Args:
        logger (logging.Logger): Logger instance
        symbol (str): Trading symbol
        signal_type (str): Signal type (BUY, SELL, NEUTRAL)
        strength (float): Signal strength
        rsi (float): RSI indicator value
        ema_fast (float): Fast EMA value
        ema_slow (float): Slow EMA value
    """
    logger.info(f"SIGNAL: {symbol} {signal_type} (strength: {strength:.2f}) "
                f"RSI: {rsi:.2f} EMA-fast: {ema_fast:.5f} EMA-slow: {ema_slow:.5f}")
