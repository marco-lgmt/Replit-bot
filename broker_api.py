"""
AllCashBroker API client for forex trading bot.
Handles communication with the broker's API.
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List
import requests
from requests.exceptions import RequestException

class AllCashBrokerAPI:
    """
    API client for AllCashBroker trading platform.
    Handles authentication and trade execution.
    """
    
    # Base API URL for AllCashBroker
    BASE_URL = "https://allcash.site/api/v1.1"  # API URL from user code
    
    def __init__(self, api_key: str, demo_mode: bool = True):
        """
        Initialize the AllCashBroker API client.
        
        Args:
            api_key (str): API key for authentication
            demo_mode (bool): Whether to use demo (paper trading) account
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.demo_mode = demo_mode
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Set the appropriate API URL based on mode
        # For AllCashBroker, we set the demo parameter in the request instead of URL
        self.base_url = self.BASE_URL
        if demo_mode:
            self.logger.info("API initialized in DEMO mode")
        else:
            self.logger.warning("API initialized in LIVE trading mode")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to the AllCashBroker API.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint path
            data (Optional[Dict]): Request payload data
            
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            Exception: If the API request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        response = None
        try:
            if method == "GET":
                response = self.session.get(url, params=data)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            result = response.json()
            
            # Check for API errors
            if "error" in result:
                raise Exception(f"API error: {result['error']}")
            
            return result
            
        except RequestException as e:
            self.logger.error(f"API request error: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
        except json.JSONDecodeError as jde:
            if response:
                self.logger.error(f"Invalid JSON response from API: {response.text}")
            raise Exception("Invalid JSON response from API")
        except Exception as e:
            self.logger.error(f"Unexpected error in API request: {str(e)}")
            raise
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Dict[str, Any]: Account information (balance, equity, etc.)
        """
        return self._make_request("GET", "/account")
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions.
        
        Returns:
            List[Dict[str, Any]]: List of open positions
        """
        response = self._make_request("GET", "/positions")
        return response.get("positions", [])
    
    def place_buy_order(self, symbol: str, amount: float, take_profit: float = 0, stop_loss: float = 0) -> str:
        """
        Place a buy order.
        
        Args:
            symbol (str): Trading symbol (e.g., "GBP/USD")
            amount (float): Trade amount
            take_profit (float): Take profit price level (0 for none)
            stop_loss (float): Stop loss price level (0 for none)
            
        Returns:
            str: Order ID if successful
        """
        # Intenta el método para la API AllCashBroker descrito por el usuario
        try:
            import requests
            self.logger.info(f"Enviando orden directamente a AllCashBroker via requests")
            
            data = {
                "amount": amount,
                "direction": "CALL",
                "asset": symbol,
                "time": 5,  # Default trade duration in minutes
                "demo": self.demo_mode
            }
            
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            r = requests.post(
                "https://allcash.site/api/v1.1/signal/trade", 
                json=data, 
                headers=headers
            )
            
            self.logger.info(f"Respuesta: {r.status_code} - {r.text}")
            
            if r.status_code == 200:
                response = r.json()
                # Convertir a string vacío u obtener el ID del orden si está disponible
                return str(response.get("order_id", ""))
            else:
                self.logger.error(f"Error al enviar orden: {r.status_code} - {r.text}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error en solicitud directa: {str(e)}")
            return ""
        
        # Este código ya no se ejecutará
        return ""
    
    def place_sell_order(self, symbol: str, amount: float, take_profit: float = 0, stop_loss: float = 0) -> str:
        """
        Place a sell order.
        
        Args:
            symbol (str): Trading symbol (e.g., "GBP/USD")
            amount (float): Trade amount
            take_profit (float): Take profit price level (0 for none)
            stop_loss (float): Stop loss price level (0 for none)
            
        Returns:
            str: Order ID if successful
        """
        # Intenta el método para la API AllCashBroker descrito por el usuario
        try:
            import requests
            self.logger.info(f"Enviando orden de venta directamente a AllCashBroker via requests")
            
            data = {
                "amount": amount,
                "direction": "PUT",
                "asset": symbol,
                "time": 5,  # Default trade duration in minutes
                "demo": self.demo_mode
            }
            
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            r = requests.post(
                "https://allcash.site/api/v1.1/signal/trade", 
                json=data, 
                headers=headers
            )
            
            self.logger.info(f"Respuesta: {r.status_code} - {r.text}")
            
            if r.status_code == 200:
                response = r.json()
                # Convertir a string vacío u obtener el ID del orden si está disponible
                return str(response.get("order_id", ""))
            else:
                self.logger.error(f"Error al enviar orden de venta: {r.status_code} - {r.text}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error en solicitud directa de venta: {str(e)}")
            return ""
        
        # Este código ya no se ejecutará
        return ""
    
    def close_order(self, order_id: str) -> bool:
        """
        Close an existing order.
        
        Args:
            order_id (str): ID of the order to close
            
        Returns:
            bool: True if the order was closed successfully
        """
        # For AllCashBroker API, they might not support closing orders or use a different endpoint
        # This is a placeholder implementation
        try:
            data = {
                "order_id": order_id,
                "demo": self.demo_mode
            }
            response = self._make_request("POST", "/signal/close", data)
            success = response.get("success", False)
            
            if success:
                self.logger.info(f"Closed order {order_id} successfully")
            else:
                self.logger.warning(f"Failed to close order {order_id}")
            
            return success
        except Exception as e:
            self.logger.error(f"Error closing order {order_id}: {str(e)}")
            return False
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get the status of an order.
        
        Args:
            order_id (str): ID of the order
            
        Returns:
            Dict[str, Any]: Order status information
        """
        return self._make_request("GET", f"/orders/{order_id}")
    
    def modify_order(self, order_id: str, take_profit: Optional[float] = None, 
                     stop_loss: Optional[float] = None) -> bool:
        """
        Modify an existing order (update TP/SL).
        
        Args:
            order_id (str): ID of the order to modify
            take_profit (Optional[float]): New take profit level (None to leave unchanged)
            stop_loss (Optional[float]): New stop loss level (None to leave unchanged)
            
        Returns:
            bool: True if the order was modified successfully
        """
        data = {}
        
        if take_profit is not None:
            data["take_profit"] = take_profit
        
        if stop_loss is not None:
            data["stop_loss"] = stop_loss
        
        # If no changes requested, return early
        if not data:
            return True
        
        response = self._make_request("PUT", f"/orders/{order_id}", data)
        success = response.get("success", False)
        
        if success:
            changes = []
            if take_profit is not None: 
                changes.append(f"TP={take_profit}")
            if stop_loss is not None: 
                changes.append(f"SL={stop_loss}")
            
            self.logger.info(f"Modified order {order_id}: {', '.join(changes)}")
        else:
            self.logger.warning(f"Failed to modify order {order_id}")
        
        return success
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market data for a symbol.
        
        Args:
            symbol (str): Trading symbol (e.g., "GBP/USD")
            
        Returns:
            Dict[str, Any]: Market data (bid, ask, etc.)
        """
        return self._make_request("GET", f"/market/{symbol}")
