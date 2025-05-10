"""
Scheduler module for forex trading bot.
Schedules and manages regular market analysis and trading.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Optional

from market_analyzer import MarketAnalyzer
from trade_executor import TradeExecutor

class Scheduler:
    """
    Schedules regular market analysis and trade execution.
    """
    
    def __init__(self, market_analyzer: MarketAnalyzer, 
                 trade_executor: TradeExecutor,
                 analysis_interval_minutes: int = 60):
        """
        Initialize Scheduler.
        
        Args:
            market_analyzer (MarketAnalyzer): Market analyzer instance
            trade_executor (TradeExecutor): Trade executor instance
            analysis_interval_minutes (int): Interval between analyses in minutes
        """
        self.logger = logging.getLogger(__name__)
        self.market_analyzer = market_analyzer
        self.trade_executor = trade_executor
        self.analysis_interval_seconds = analysis_interval_minutes * 60
        
        self.running = False
        self.scheduler_thread = None
        self.last_run_time = None
        
        self.logger.info(f"Scheduler initialized with interval: {analysis_interval_minutes} minutes")
    
    def start(self) -> None:
        """
        Start the scheduler.
        """
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Scheduler started")
    
    def stop(self) -> None:
        """
        Stop the scheduler.
        """
        if not self.running:
            self.logger.warning("Scheduler is not running")
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=3.0)  # Wait up to 3 seconds for thread to finish
        
        self.logger.info("Scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """
        Main scheduler loop.
        """
        self.logger.info("Scheduler loop started")
        
        while self.running:
            try:
                # Run the analysis and trading cycle
                self._run_cycle()
                
                # Update last run time
                self.last_run_time = datetime.now()
                
                # Reset daily trade counter at midnight
                current_time = datetime.now()
                if current_time.hour == 0 and current_time.minute < self.analysis_interval_seconds // 60:
                    self.trade_executor.reset_daily_counter()
                    self.logger.info("Daily trade counter reset")
                
                # Sleep until next cycle
                interval_text = "minute" if self.analysis_interval_seconds == 60 else "minutes"
                self.logger.info(f"Next analysis in {self.analysis_interval_seconds // 60} {interval_text}")
                
                # Check if we should still be running every second
                for _ in range(self.analysis_interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {str(e)}")
                # Sleep for a short period before retrying
                time.sleep(30)
        
        self.logger.info("Scheduler loop stopped")
    
    def _run_cycle(self) -> None:
        """
        Run a single analysis and trading cycle.
        """
        cycle_start_time = datetime.now()
        self.logger.info(f"Starting analysis cycle at {cycle_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # First, update status of active trades
            self.trade_executor.update_active_trades()
            
            # Analyze the markets
            signals = self.market_analyzer.analyze_markets()
            self.logger.info(f"Analysis complete. Found {len(signals)} trading signals")
            
            # Execute trades based on signals
            if signals:
                executed_trades = self.trade_executor.execute_trades(signals)
                self.logger.info(f"Executed {len(executed_trades)} trades")
            else:
                self.logger.info("No trades executed - no valid signals")
            
        except Exception as e:
            self.logger.error(f"Error during analysis cycle: {str(e)}")
        
        cycle_end_time = datetime.now()
        duration = (cycle_end_time - cycle_start_time).total_seconds()
        self.logger.info(f"Analysis cycle completed in {duration:.2f} seconds")
    
    def run_now(self) -> None:
        """
        Run an analysis cycle immediately, outside of the normal schedule.
        """
        self.logger.info("Running immediate analysis cycle")
        
        # Run in a separate thread to avoid blocking
        threading.Thread(target=self._run_cycle, daemon=True).start()
