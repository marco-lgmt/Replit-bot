"""
Market Analyzer module for forex trading bot.
Analyzes forex market using TradingView technical indicators.
"""

import logging
from typing import Dict, List, Optional, Tuple
import time
from tradingview_ta import TA_Handler, Interval, Exchange

from signals import TradingSignal
from forex_pairs import standardize_pair_format

class MarketAnalyzer:
    """
    Analyzes forex market using TradingView technical indicators.
    Generates trading signals based on RSI and EMA crossover strategy.
    """
    
    def __init__(self, 
                 symbols: List[str], 
                 interval: str = "1h",
                 rsi_period: int = 14, 
                 rsi_overbought: int = 70, 
                 rsi_oversold: int = 30,
                 ema_fast_period: int = 9, 
                 ema_slow_period: int = 21):
        """
        Initialize MarketAnalyzer.
        
        Args:
            symbols (List[str]): List of forex pairs to analyze (e.g., ["GBP/USD", "USD/CHF"])
            interval (str): Time interval for analysis (e.g., "1m", "5m", "1h", "4h", "1d")
            rsi_period (int): RSI indicator period
            rsi_overbought (int): RSI overbought threshold
            rsi_oversold (int): RSI oversold threshold
            ema_fast_period (int): Fast EMA period
            ema_slow_period (int): Slow EMA period
        """
        self.logger = logging.getLogger(__name__)
        self.symbols = symbols
        self.interval_mapping = {
            "1m": Interval.INTERVAL_1_MINUTE,
            "5m": Interval.INTERVAL_5_MINUTES,
            "15m": Interval.INTERVAL_15_MINUTES,
            "30m": Interval.INTERVAL_30_MINUTES,
            "1h": Interval.INTERVAL_1_HOUR,
            "2h": Interval.INTERVAL_2_HOURS,
            "4h": Interval.INTERVAL_4_HOURS,
            "1d": Interval.INTERVAL_1_DAY,
            "1W": Interval.INTERVAL_1_WEEK,
            "1M": Interval.INTERVAL_1_MONTH
        }
        self.interval = self.interval_mapping.get(interval, Interval.INTERVAL_1_HOUR)
        
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.ema_fast_period = ema_fast_period
        self.ema_slow_period = ema_slow_period
        
        self.handlers = self._initialize_handlers()
        self.logger.info(f"MarketAnalyzer initialized with {len(symbols)} symbols")
    
    def _initialize_handlers(self) -> Dict[str, TA_Handler]:
        """
        Initialize TradingView TA handlers for each symbol.
        
        Returns:
            Dict[str, TA_Handler]: Dictionary of TradingView TA handlers
        """
        handlers = {}
        for symbol in self.symbols:
            try:
                # Convert traditional forex notation to TradingView format
                tv_symbol = standardize_pair_format(symbol)
                
                # Determine exchange and screener based on symbol type
                if symbol.endswith("USDT") or "USD" in symbol and "/" not in symbol:
                    # Crypto pairs use Binance exchange and crypto screener
                    exchange = "BINANCE"
                    screener = "crypto"
                    self.logger.info(f"Using crypto settings for {symbol}: {exchange}/{screener}")
                else:
                    # Forex pairs use FX_IDC exchange and forex screener
                    exchange = "FX_IDC"
                    screener = "forex"
                
                handler = TA_Handler(
                    symbol=tv_symbol,
                    exchange=exchange,
                    screener=screener,
                    interval=self.interval
                )
                handlers[symbol] = handler
                self.logger.debug(f"Initialized handler for {symbol} ({tv_symbol}) on {exchange}/{screener}")
            except Exception as e:
                self.logger.error(f"Error initializing handler for {symbol}: {str(e)}")
        
        return handlers
    
    def analyze_markets(self) -> Dict[str, TradingSignal]:
        """
        Analyze all forex pairs and generate trading signals.
        
        Returns:
            Dict[str, TradingSignal]: Dictionary mapping forex pairs to trading signals
        """
        signals = {}
        
        for symbol, handler in self.handlers.items():
            try:
                signal = self.analyze_symbol(symbol)
                if signal:
                    signals[symbol] = signal
                    self.logger.info(f"Generated {signal.signal_type} signal for {symbol}")
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {str(e)}")
            
            # Add a small delay to avoid hitting rate limits
            time.sleep(1)
        
        return signals
    
    def analyze_symbol(self, symbol: str) -> Optional[TradingSignal]:
        """
        Analyze a single forex pair or crypto pair and generate a trading signal.
        
        Args:
            symbol (str): Trading pair to analyze (e.g., "GBP/USD" or "BTCUSDT")
            
        Returns:
            Optional[TradingSignal]: Trading signal if conditions are met, None otherwise
        """
        if symbol not in self.handlers:
            self.logger.warning(f"No handler found for {symbol}")
            return None
        
        try:
            handler = self.handlers[symbol]
            # Add debug info
            self.logger.info(f"Analyzing {symbol} with handler: exchange={handler.exchange}, screener={handler.screener}, symbol={handler.symbol}")
            
            try:
                analysis = handler.get_analysis()
                if analysis is None:
                    self.logger.warning(f"Received None analysis for {symbol}")
                    return None
            except Exception as e:
                self.logger.error(f"Error getting analysis for {symbol}: {str(e)}")
                if "Exchange or symbol not found" in str(e):
                    # Try with different exchanges for crypto pairs
                    if symbol.endswith("USDT"):
                        alt_exchanges = ["KUCOIN", "COINBASE", "FTX"]
                        for alt_exchange in alt_exchanges:
                            try:
                                self.logger.info(f"Trying alternate exchange {alt_exchange} for {symbol}")
                                alt_handler = TA_Handler(
                                    symbol=handler.symbol,
                                    exchange=alt_exchange,
                                    screener="crypto",
                                    interval=handler.interval
                                )
                                analysis = alt_handler.get_analysis()
                                if analysis is not None:
                                    self.logger.info(f"Successfully got data from {alt_exchange} for {symbol}")
                                    handler = alt_handler
                                    self.handlers[symbol] = alt_handler  # Update the handler
                                    break
                            except Exception as inner_e:
                                self.logger.warning(f"Failed with {alt_exchange} for {symbol}: {str(inner_e)}")
                                continue
                if analysis is None:
                    raise Exception(f"Could not get data for {symbol} on any exchange")
                
            # Extract indicators
            indicators = analysis.indicators
            self.logger.info(f"Available indicators for {symbol}: {list(indicators.keys())}")
            
            # Get RSI value
            rsi = indicators.get("RSI", None)
            if rsi is None:
                rsi = indicators.get(f"RSI{self.rsi_period}", None)
                self.logger.debug(f"Using RSI{self.rsi_period} for {symbol}: {rsi}")
            
            # Get EMA values
            ema_fast = indicators.get(f"EMA{self.ema_fast_period}", None)
            ema_slow = indicators.get(f"EMA{self.ema_slow_period}", None)
            
            self.logger.debug(f"Indicators for {symbol}: RSI={rsi}, EMA{self.ema_fast_period}={ema_fast}, EMA{self.ema_slow_period}={ema_slow}")
            
            if rsi is None or ema_fast is None or ema_slow is None:
                self.logger.warning(f"Missing indicator data for {symbol}. RSI: {rsi}, EMA Fast: {ema_fast}, EMA Slow: {ema_slow}")
                return None
            
            # Get current price
            close_price = indicators.get("close", 0)
            
            # Check for signals
            signal_type, signal_strength = self._evaluate_signals(rsi, ema_fast, ema_slow)
            
            if signal_type != "NEUTRAL":
                # Create and return a signal
                # Ensure signal_type is one of the accepted literals
                valid_signal_type = "BUY" if signal_type == "BUY" else "SELL" if signal_type == "SELL" else "NEUTRAL"
                
                signal = TradingSignal(
                    symbol=symbol,
                    signal_type=valid_signal_type,  # "BUY", "SELL", or "NEUTRAL"
                    strength=signal_strength,  # 0.0 to 1.0
                    price=close_price,
                    rsi=rsi,
                    ema_fast=ema_fast,
                    ema_slow=ema_slow,
                    timestamp=time.time()
                )
                return signal
            
        except Exception as e:
            self.logger.error(f"Error in analyze_symbol for {symbol}: {str(e)}")
        
        return None
    
    def _evaluate_signals(self, rsi: float, ema_fast: float, ema_slow: float) -> Tuple[str, float]:
        """
        Evaluate RSI and EMA indicators to determine trading signal.
        
        Args:
            rsi (float): RSI indicator value
            ema_fast (float): Fast EMA value
            ema_slow (float): Slow EMA value
            
        Returns:
            Tuple[str, float]: Signal type ("BUY", "SELL", "NEUTRAL") and strength (0.0 to 1.0)
        """
        # Default signal
        signal_type = "NEUTRAL"
        signal_strength = 0.0
        
        # RSI signals
        rsi_signal = "NEUTRAL"
        if rsi < self.rsi_oversold:
            rsi_signal = "BUY"
            # Calculate how oversold (signal strength increases as RSI decreases below threshold)
            rsi_strength = min(1.0, (self.rsi_oversold - rsi) / 10)
        elif rsi > self.rsi_overbought:
            rsi_signal = "SELL"
            # Calculate how overbought (signal strength increases as RSI increases above threshold)
            rsi_strength = min(1.0, (rsi - self.rsi_overbought) / 10)
        else:
            rsi_strength = 0.0
        
        # EMA crossover signals
        ema_signal = "NEUTRAL"
        if ema_fast > ema_slow:
            ema_signal = "BUY"
            # Calculate crossover strength (normalized difference between EMAs)
            ema_strength = min(1.0, (ema_fast - ema_slow) / ema_slow * 10)
        elif ema_fast < ema_slow:
            ema_signal = "SELL"
            # Calculate crossover strength (normalized difference between EMAs)
            ema_strength = min(1.0, (ema_slow - ema_fast) / ema_slow * 10)
        else:
            ema_strength = 0.0
        
        # Combine signals (if both agree, stronger signal)
        if rsi_signal == ema_signal and rsi_signal != "NEUTRAL":
            signal_type = rsi_signal
            # Combined strength (average of both signals with a bonus for agreement)
            signal_strength = min(1.0, (rsi_strength + ema_strength) / 2 * 1.2)
        # If they disagree, use the stronger signal
        elif rsi_strength > ema_strength and rsi_signal != "NEUTRAL":
            signal_type = rsi_signal
            signal_strength = rsi_strength * 0.8  # Reduced confidence due to disagreement
        elif ema_strength > 0 and ema_signal != "NEUTRAL":
            signal_type = ema_signal
            signal_strength = ema_strength * 0.8  # Reduced confidence due to disagreement
        
        return signal_type, signal_strength
