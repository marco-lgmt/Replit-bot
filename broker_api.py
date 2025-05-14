"""
AllCashBroker API client for forex trading bot.
Handles communication with the broker's API.
"""

import logging
import json
import time
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import requests
from requests.exceptions import RequestException
from config import update_config, load_config

class AllCashBrokerAPI:
    """
    API client for AllCashBroker trading platform.
    Handles authentication and trade execution.
    """
    
    # Base API URL for AllCashBroker
    BASE_URL = "https://api.allcashbroker.com"  # API URL actualizada según información del usuario
    
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
        
        # Verificar y renovar el token si es necesario
        valid_token = self._verify_and_renew_token(api_key)
        
        # Como el token ya incluye "Bearer", lo usamos tal cual
        self.session.headers.update({
            "Authorization": valid_token,  # El token JWT ya incluye "Bearer"
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
            
    def _verify_and_renew_token(self, token: str) -> str:
        """
        Verify if the JWT token is valid and renew it if it's close to expiration.
        
        Args:
            token (str): JWT token to verify
            
        Returns:
            str: Valid JWT token (either the original or a renewed one)
        """
        try:
            # Si el token no comienza con "Bearer ", añadirlo
            actual_token = token
            if token.startswith("Bearer "):
                actual_token = token[7:]
            
            # Decodificar el token sin verificar la firma
            decoded = jwt.decode(actual_token, options={"verify_signature": False})
            
            # Obtener tiempo de expiración
            exp_timestamp = decoded.get('exp', 0)
            expiration_time = datetime.fromtimestamp(exp_timestamp)
            current_time = datetime.now()
            
            # Renovar si expira en menos de 1 hora
            if expiration_time <= current_time + timedelta(hours=1):
                self.logger.info("Token expirará pronto. Actualizando a nuevo token.")
                # Actualizar con el token proporcionado por el usuario
                new_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjAxSlNTWFdGOEc4MDhIRVYyS0RFR1dKWFQyIiwibGFuZ3VhZ2UiOiJlcyIsIm5hbWUiOiJNaXJpYW4gbGFyZ28iLCJpbXBlcnNvbmF0ZSI6ZmFsc2UsImxvZ2luSWQiOiIwMUpWNTQ2RThKMUdOTjFHRjQ2M1g1R1cyUSIsImVtYWlsIjoibWlyaWFubGFyZ28yMUBnbWFpbC5jb20iLCJ0ZW5hbnRJZCI6IjAxSlNGQk1INFZCRzQxMDFUUzQ0Ulo4MzdBIiwiYWN0aXZlIjp0cnVlLCJiYW5uZWQiOmZhbHNlLCJpYXQiOjE3NDcxNTAxMjUsImV4cCI6MTc0NzE5MzMyNSwiaXNzIjoiQVVUSC1UUkFERS1PUFRJT04ifQ.o9dBj4e-wmfYlWAghPGHj7kAts_eB2dkPyaCq8KtsyI"
                
                # Actualizar en la configuración
                update_config("api_key", new_token)
                
                return new_token
            else:
                self.logger.info(f"Token válido hasta {expiration_time.strftime('%Y-%m-%d %H:%M:%S')}")
                return token
                
        except Exception as e:
            self.logger.error(f"Error al verificar el token JWT: {str(e)}")
            # En caso de error, devolver el token original
            return token
    
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
        # Verificar y renovar el token antes de cada solicitud
        self._check_and_refresh_token()
        
        # Use the endpoint provided directly, ignoring old URL construction
        if endpoint.startswith("/"):
            url = f"{self.base_url}{endpoint}"
        else:
            url = f"{self.base_url}/{endpoint}"
        
        # For trade operations, always use the /trades/open endpoint
        if endpoint.startswith("/signal/trade") or endpoint == "/trade":
            url = f"{self.base_url}/trades/open"
            self.logger.info(f"Redirigiendo a endpoint correcto: {url}")
        
        response = None
        try:
            # Asegurarnos de que los datos incluyen el modo demo si es necesario
            if data is None:
                data = {}
            
            if method in ["POST", "PUT"] and self.demo_mode and "isDemo" not in data:
                data["isDemo"] = self.demo_mode
            
            self.logger.info(f"Enviando {method} a {url} con datos: {data}")
            
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
            
            self.logger.info(f"Respuesta: {response.status_code} - {response.text}")
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            result = response.json()
            
            # Check for API errors
            if "error" in result:
                error_message = result.get('error', '')
                # Si el error es por token expirado, intentar renovar y reintentar
                if "token" in error_message.lower() and "expired" in error_message.lower():
                    self.logger.warning("Token expirado detectado en respuesta. Renovando token y reintentando.")
                    self._renew_token_now()
                    # Reintentar la solicitud recursivamente
                    return self._make_request(method, endpoint, data)
                    
                raise Exception(f"API error: {result['error']}")
            
            return result
            
        except RequestException as e:
            self.logger.error(f"API request error: {str(e)}")
            # Verificar si el error está relacionado con autenticación
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code in [401, 403]:
                    self.logger.warning("Error de autenticación. Intentando renovar token y reintentar.")
                    self._renew_token_now()
                    # Reintentar la solicitud recursivamente
                    return self._make_request(method, endpoint, data)
            
            raise Exception(f"API request failed: {str(e)}")
        except json.JSONDecodeError as jde:
            if response:
                self.logger.error(f"Invalid JSON response from API: {response.text}")
            raise Exception("Invalid JSON response from API")
        except Exception as e:
            self.logger.error(f"Unexpected error in API request: {str(e)}")
            raise
            
    def _check_and_refresh_token(self) -> None:
        """
        Verifica el estado del token actual y lo renueva si es necesario.
        Esta función se llama antes de cada solicitud a la API.
        """
        try:
            current_token = self.session.headers.get("Authorization", "")
            # Si no hay token en la sesión, usar el de la instancia
            if not current_token:
                current_token = self.api_key
                
            # Verificar y renovar si es necesario
            valid_token = self._verify_and_renew_token(current_token)
            
            # Si el token cambió, actualizar la sesión y la instancia
            if valid_token != current_token:
                self.logger.info("Actualizando token en la sesión")
                self.session.headers.update({"Authorization": valid_token})
                self.api_key = valid_token
        except Exception as e:
            self.logger.error(f"Error al verificar o renovar token: {str(e)}")
            
    def _renew_token_now(self) -> None:
        """
        Fuerza la renovación del token inmediatamente.
        Se utiliza cuando se detecta un error de autenticación.
        """
        try:
            # Actualizar con el token proporcionado por el usuario
            new_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjAxSlNTWFdGOEc4MDhIRVYyS0RFR1dKWFQyIiwibGFuZ3VhZ2UiOiJlcyIsIm5hbWUiOiJNaXJpYW4gbGFyZ28iLCJpbXBlcnNvbmF0ZSI6ZmFsc2UsImxvZ2luSWQiOiIwMUpWNTQ2RThKMUdOTjFHRjQ2M1g1R1cyUSIsImVtYWlsIjoibWlyaWFubGFyZ28yMUBnbWFpbC5jb20iLCJ0ZW5hbnRJZCI6IjAxSlNGQk1INFZCRzQxMDFUUzQ0Ulo4MzdBIiwiYWN0aXZlIjp0cnVlLCJiYW5uZWQiOmZhbHNlLCJpYXQiOjE3NDcxNTAxMjUsImV4cCI6MTc0NzE5MzMyNSwiaXNzIjoiQVVUSC1UUkFERS1PUFRJT04ifQ.o9dBj4e-wmfYlWAghPGHj7kAts_eB2dkPyaCq8KtsyI"
            
            # Actualizar en la configuración
            update_config("api_key", new_token)
            
            # Actualizar en la sesión actual
            self.session.headers.update({"Authorization": new_token})
            self.api_key = new_token
            
            self.logger.info("Token renovado forzosamente")
        except Exception as e:
            self.logger.error(f"Error al renovar token forzosamente: {str(e)}")
    
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
        try:
            self.logger.info(f"Enviando orden de compra directamente a AllCashBroker")
            
            # Asegurarse de que el símbolo no tiene /
            symbol_clean = symbol.replace("/", "")
            
            # Formato actualizado según el ejemplo proporcionado por el usuario
            data = {
                "symbol": symbol_clean,
                "amount": amount,
                "direction": "BUY",  # Usamos BUY para compra
                "expirationType": "CANDLE_CLOSE",
                "closeType": "05:00",  # Default 5 minutos
                "isDemo": self.demo_mode
            }
            
            if take_profit > 0:
                data["takeProfit"] = take_profit
            
            if stop_loss > 0:
                data["stopLoss"] = stop_loss
            
            # Endpoint actualizado según la información más reciente del usuario
            endpoint = "/trades/open"
            
            self.logger.info(f"Enviando orden a: {self.base_url}{endpoint}")
            self.logger.info(f"Datos de la orden: {data}")
            
            # Usar self._make_request para utilizar la sesión con los headers correctos
            response = self._make_request("POST", endpoint, data)
            
            # Procesar la respuesta (puede variar según la implementación de AllCashBroker)
            order_id = response.get("orderId", "")
            if order_id:
                self.logger.info(f"Orden ejecutada correctamente con ID: {order_id}")
                return str(order_id)
            else:
                self.logger.warning("Orden aceptada pero no se recibió ID")
                return "orden_aceptada"
                
        except Exception as e:
            self.logger.error(f"Error general en solicitud de compra: {str(e)}")
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
        try:
            self.logger.info(f"Enviando orden de venta directamente a AllCashBroker")
            
            # Asegurarse de que el símbolo no tiene /
            symbol_clean = symbol.replace("/", "")
            
            # Formato actualizado según el ejemplo proporcionado por el usuario
            data = {
                "symbol": symbol_clean,
                "amount": amount,
                "direction": "SELL",  # Usamos SELL para venta
                "expirationType": "CANDLE_CLOSE",
                "closeType": "05:00",  # Default 5 minutos
                "isDemo": self.demo_mode
            }
            
            if take_profit > 0:
                data["takeProfit"] = take_profit
            
            if stop_loss > 0:
                data["stopLoss"] = stop_loss
            
            # Endpoint actualizado según la información más reciente del usuario
            endpoint = "/trades/open"
            
            self.logger.info(f"Enviando orden a: {self.base_url}{endpoint}")
            self.logger.info(f"Datos de la orden: {data}")
            
            # Usar self._make_request para utilizar la sesión con los headers correctos
            response = self._make_request("POST", endpoint, data)
            
            # Procesar la respuesta (puede variar según la implementación de AllCashBroker)
            order_id = response.get("orderId", "")
            if order_id:
                self.logger.info(f"Orden ejecutada correctamente con ID: {order_id}")
                return str(order_id)
            else:
                self.logger.warning("Orden aceptada pero no se recibió ID")
                return "orden_aceptada"
                
        except Exception as e:
            self.logger.error(f"Error general en solicitud de venta: {str(e)}")
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
                "isDemo": self.demo_mode
            }
            response = self._make_request("POST", "/trades/close", data)
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
        return self._make_request("GET", f"/trades/{order_id}")
    
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
        data: Dict[str, Any] = {
            "isDemo": self.demo_mode
        }
        
        if take_profit is not None:
            data["takeProfit"] = take_profit
        
        if stop_loss is not None:
            data["stopLoss"] = stop_loss
        
        # If no changes requested, return early
        if len(data) <= 1:  # only has isDemo
            return True
        
        response = self._make_request("PUT", f"/trades/{order_id}", data)
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
        symbol_clean = symbol.replace("/", "")
        return self._make_request("GET", f"/market/{symbol_clean}")