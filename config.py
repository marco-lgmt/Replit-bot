"""
Configuration module for the forex trading bot.
Loads and provides access to configuration parameters.
"""

import os
import json
import logging
from typing import Dict, Any, List

# Default configuration
DEFAULT_CONFIG = {
    "demo_mode": True,  # Set to False for real trading
    "forex_pairs": ["GBP/USD", "USD/CHF", "USD/CAD"],
    "analysis_interval": "1h",  # 1h, 4h, 1d etc.
    "schedule_interval_minutes": 60,
    "trade_amount": 100,  # Amount in base currency
    "take_profit_pips": 20,
    "stop_loss_pips": 10,
    "max_trades_per_day": 5,
    "rsi_period": 14,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "ema_fast_period": 9,
    "ema_slow_period": 21,
    "log_level": "INFO"
}

CONFIG_FILE = "config.json"

def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.json file if it exists,
    otherwise return default configuration.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
                logging.info(f"Configuration loaded from {CONFIG_FILE}")
        else:
            logging.info(f"No config file found at {CONFIG_FILE}. Using default configuration.")
            # Create default config file for future use
            save_config(config)
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}. Using default configuration.")
    
    return config

def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to config.json file.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary to save
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logging.info(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        logging.error(f"Error saving configuration: {str(e)}")

def get_forex_pairs() -> List[str]:
    """
    Get the list of forex pairs from configuration.
    
    Returns:
        List[str]: List of forex pairs
    """
    config = load_config()
    return config.get("forex_pairs", ["GBP/USD", "USD/CHF", "USD/CAD"])

def update_config(key: str, value: Any) -> None:
    """
    Update a specific configuration parameter.
    
    Args:
        key (str): Configuration key to update
        value (Any): New value for the configuration key
    """
    config = load_config()
    config[key] = value
    save_config(config)
    logging.info(f"Configuration updated: {key} = {value}")
