"""
Forex Trading Bot - Main Entry Point
This script initializes and runs the forex trading bot.
"""

import os
import logging
import time
from datetime import datetime

from config import load_config, save_config
from scheduler import Scheduler
from market_analyzer import MarketAnalyzer
from trade_executor import TradeExecutor
from broker_api import AllCashBrokerAPI
from logger import setup_logger

def main():
    """Main entry point for the forex trading bot."""
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting forex trading bot at %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Initialize broker API with API key
        api_key = os.environ.get("ALLCASH_API_KEY", config.get("api_key", "qrlwfzlxha"))
        if not api_key:
            logger.error("API key not found. Please set the ALLCASH_API_KEY environment variable or update config.py")
            return
        
        # Store API key in config for future use
        if config.get("api_key", "") != api_key:
            config["api_key"] = api_key
            save_config(config)
        
        broker_api = AllCashBrokerAPI(
            api_key=api_key,
            demo_mode=config.get("demo_mode", True)
        )
        logger.info("Broker API initialized. Demo mode: %s", config.get("demo_mode", True))
        
        # Initialize market analyzer
        market_analyzer = MarketAnalyzer(
            symbols=config.get("forex_pairs", ["GBP/USD", "USD/CHF", "USD/CAD"]),
            interval=config.get("analysis_interval", "1h"),
            rsi_period=config.get("rsi_period", 14),
            rsi_overbought=config.get("rsi_overbought", 70),
            rsi_oversold=config.get("rsi_oversold", 30),
            ema_fast_period=config.get("ema_fast_period", 9),
            ema_slow_period=config.get("ema_slow_period", 21)
        )
        logger.info("Market analyzer initialized with %d forex pairs", 
                   len(config.get("forex_pairs", ["GBP/USD", "USD/CHF", "USD/CAD"])))
        
        # Initialize trade executor
        trade_executor = TradeExecutor(
            broker_api=broker_api,
            trade_amount=config.get("trade_amount", 100),
            take_profit_pips=config.get("take_profit_pips", 20),
            stop_loss_pips=config.get("stop_loss_pips", 10),
            max_trades_per_day=config.get("max_trades_per_day", 5)
        )
        logger.info("Trade executor initialized")
        
        # Initialize scheduler
        scheduler = Scheduler(
            market_analyzer=market_analyzer,
            trade_executor=trade_executor,
            analysis_interval_minutes=config.get("schedule_interval_minutes", 1)
        )
        logger.info("Scheduler initialized with %d minute intervals", 
                   config.get("schedule_interval_minutes", 1))
        
        # Enviar una orden de prueba en modo demo probando diferentes pares y configuraciones
        logger.info("Enviando una orden de prueba en la cuenta demo...")

        # Probar con ETHUSDT como en el ejemplo proporcionado por el usuario
        logger.info("Probando con par ETHUSDT como en el ejemplo...")
        trade_id_crypto = broker_api.place_buy_order(
            symbol="ETHUSDT",
            amount=1.0,  # Una cantidad pequeña para prueba
            take_profit=0,
            stop_loss=0
        )
        
        if trade_id_crypto:
            logger.info(f"Orden de prueba para ETHUSDT enviada exitosamente! ID: {trade_id_crypto}")
        else:
            logger.warning("No se pudo enviar la orden de prueba para ETHUSDT.")
            
        # Probar con un par forex tradicional
        logger.info("Probando con par de forex EUR/USD...")
        trade_id = broker_api.place_buy_order(
            symbol="EUR/USD",
            amount=1.0,  # Una cantidad pequeña para prueba
            take_profit=0,
            stop_loss=0
        )
        
        if trade_id:
            logger.info(f"Orden de prueba para EUR/USD enviada exitosamente! ID: {trade_id}")
        else:
            logger.warning("No se pudo enviar la orden de prueba para EUR/USD.")
        
        # Start the bot
        logger.info("Starting the forex trading bot...")
        scheduler.start()
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt detected. Shutting down...")
            scheduler.stop()
            
    except Exception as e:
        logger.exception("Unexpected error occurred: %s", str(e))
    
    logger.info("Forex trading bot shutting down at %s", 
               datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    main()
