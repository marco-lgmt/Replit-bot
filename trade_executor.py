"""
Trade Executor module for forex trading bot.
Responsible for executing trades based on trading signals.
"""

import logging
import time
from datetime import datetime, date
from typing import Dict, List, Optional

from broker_api import AllCashBrokerAPI
from signals import TradingSignal

class TradeExecutor:
    """
    Executes trades based on trading signals.
    Manages trade parameters and limits.
    """
    
    def __init__(self, 
                 broker_api: AllCashBrokerAPI,
                 trade_amount: float = 100.0,
                 take_profit_pips: int = 20,
                 stop_loss_pips: int = 10,
                 max_trades_per_day: int = 5):
        """
        Initialize Trade Executor.
        
        Args:
            broker_api (AllCashBrokerAPI): Broker API instance for executing trades
            trade_amount (float): Standard amount to trade in base currency
            take_profit_pips (int): Take profit level in pips
            stop_loss_pips (int): Stop loss level in pips
            max_trades_per_day (int): Maximum number of trades allowed per day
        """
        self.logger = logging.getLogger(__name__)
        self.broker_api = broker_api
        self.trade_amount = trade_amount
        self.take_profit_pips = take_profit_pips
        self.stop_loss_pips = stop_loss_pips
        self.max_trades_per_day = max_trades_per_day
        
        # Track daily trades
        self.daily_trades = {}  # date -> count
        self.active_trades = {}  # symbol -> trade_id
        
        self.logger.info(f"TradeExecutor initialized with amount={trade_amount}, "
                         f"TP={take_profit_pips}pips, SL={stop_loss_pips}pips, "
                         f"max daily trades={max_trades_per_day}")
    
    def execute_trades(self, signals: Dict[str, TradingSignal]) -> List[str]:
        """
        Execute trades based on the provided trading signals.
        
        Args:
            signals (Dict[str, TradingSignal]): Dictionary of trading signals by symbol
            
        Returns:
            List[str]: List of trade IDs for successfully executed trades
        """
        executed_trades = []
        
        # Check if we've reached the daily trade limit
        today = date.today().isoformat()
        daily_count = self.daily_trades.get(today, 0)
        
        if daily_count >= self.max_trades_per_day:
            self.logger.warning(f"Daily trade limit reached ({self.max_trades_per_day}). No trades executed.")
            return executed_trades
        
        # Sort signals by strength (descending)
        sorted_signals = sorted(
            signals.values(),
            key=lambda s: s.strength,
            reverse=True
        )
        
        # Execute trades for the strongest signals first (up to the daily limit)
        trades_left = self.max_trades_per_day - daily_count
        for signal in sorted_signals[:trades_left]:
            # Skip weak signals
            if signal.strength < 0.5:
                self.logger.info(f"Skipping weak signal for {signal.symbol} (strength={signal.strength:.2f})")
                continue
                
            # Check if we already have an active trade for this symbol
            if signal.symbol in self.active_trades:
                self.logger.info(f"Already have an active trade for {signal.symbol}. Skipping.")
                continue
                
            # Execute the trade
            trade_id = self._execute_signal(signal)
            if trade_id:
                executed_trades.append(trade_id)
                self.active_trades[signal.symbol] = trade_id
                
                # Update daily trade count
                self.daily_trades[today] = daily_count + 1
                daily_count += 1
                
                self.logger.info(f"Trade executed for {signal.symbol} (ID: {trade_id})")
                
                # Don't exceed daily trade limit
                if daily_count >= self.max_trades_per_day:
                    self.logger.info(f"Daily trade limit reached ({self.max_trades_per_day}). Stopping execution.")
                    break
        
        return executed_trades
    
    def _execute_signal(self, signal: TradingSignal) -> Optional[str]:
        """
        Execute a single trading signal.
        
        Args:
            signal (TradingSignal): Trading signal to execute
            
        Returns:
            Optional[str]: Trade ID if successful, None otherwise
        """
        try:
            symbol = signal.symbol
            price = signal.price
            
            # Convert pips to price movement (depends on currency pair)
            pip_value = self._get_pip_value(symbol)
            take_profit = price + (self.take_profit_pips * pip_value) if signal.signal_type == "BUY" else \
                          price - (self.take_profit_pips * pip_value)
            stop_loss = price - (self.stop_loss_pips * pip_value) if signal.signal_type == "BUY" else \
                        price + (self.stop_loss_pips * pip_value)
            
            # Execute the trade
            if signal.signal_type == "BUY":
                trade_id = self.broker_api.place_buy_order(
                    symbol=symbol,
                    amount=self.trade_amount,
                    take_profit=take_profit,
                    stop_loss=stop_loss
                )
            elif signal.signal_type == "SELL":
                trade_id = self.broker_api.place_sell_order(
                    symbol=symbol,
                    amount=self.trade_amount,
                    take_profit=take_profit,
                    stop_loss=stop_loss
                )
            else:
                self.logger.warning(f"Invalid signal type: {signal.signal_type}")
                return None
            
            return trade_id
            
        except Exception as e:
            self.logger.error(f"Error executing trade for {signal.symbol}: {str(e)}")
            return None
    
    def _get_pip_value(self, symbol: str) -> float:
        """
        Get the pip value for a forex pair.
        
        Args:
            symbol (str): Forex pair (e.g., "GBP/USD")
            
        Returns:
            float: Value of 1 pip in price units
        """
        # Most forex pairs have a pip value of 0.0001, except for JPY pairs which use 0.01
        if "JPY" in symbol:
            return 0.01
        else:
            return 0.0001
    
    def close_trade(self, trade_id: str) -> bool:
        """
        Close a specific trade.
        
        Args:
            trade_id (str): ID of the trade to close
            
        Returns:
            bool: True if the trade was closed successfully, False otherwise
        """
        try:
            result = self.broker_api.close_order(trade_id)
            
            # Update our records if successful
            if result:
                for symbol, tid in list(self.active_trades.items()):
                    if tid == trade_id:
                        del self.active_trades[symbol]
                        self.logger.info(f"Removed {symbol} from active trades after closing")
                        break
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error closing trade {trade_id}: {str(e)}")
            return False
    
    def close_all_trades(self) -> int:
        """
        Close all active trades.
        
        Returns:
            int: Number of trades successfully closed
        """
        closed_count = 0
        
        for symbol, trade_id in list(self.active_trades.items()):
            try:
                if self.broker_api.close_order(trade_id):
                    del self.active_trades[symbol]
                    closed_count += 1
                    self.logger.info(f"Closed trade for {symbol} (ID: {trade_id})")
                else:
                    self.logger.warning(f"Failed to close trade for {symbol} (ID: {trade_id})")
            except Exception as e:
                self.logger.error(f"Error closing trade for {symbol} (ID: {trade_id}): {str(e)}")
        
        self.logger.info(f"Closed {closed_count} trades out of {len(self.active_trades)} active trades")
        return closed_count
    
    def update_active_trades(self) -> None:
        """
        Update the status of active trades and close any that hit take profit or stop loss.
        """
        for symbol, trade_id in list(self.active_trades.items()):
            try:
                # Get the current status of the trade
                trade_status = self.broker_api.get_order_status(trade_id)
                
                if trade_status.get("status") == "CLOSED":
                    # Trade was already closed (hit TP/SL or closed manually)
                    del self.active_trades[symbol]
                    self.logger.info(f"Trade for {symbol} (ID: {trade_id}) is already closed")
                    
                # Optionally, you could implement trailing stop-loss or other dynamic management here
                
            except Exception as e:
                self.logger.error(f"Error updating trade for {symbol} (ID: {trade_id}): {str(e)}")
    
    def reset_daily_counter(self) -> None:
        """
        Reset the daily trade counter if it's a new day.
        """
        today = date.today().isoformat()
        
        # Keep only today's counter, remove old dates
        self.daily_trades = {today: self.daily_trades.get(today, 0)}
