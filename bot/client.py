import hmac
import hashlib
import time
import urllib.parse
import requests
from typing import Dict, Any
from bot.logging_config import setup_logging

logger = setup_logging()

class BinanceFuturesClient:
    """REST Client wrapper for Binance USDT-M Futures Testnet."""

    BASE_URL = "https://testnet.binancefuture.com"

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            logger.error("API Key or Secret missing during initialization.")
            raise ValueError("API Key and API Secret must be provided.")
        
        # Clean API key and secret (strip whitespace, trailing quotes, or hidden characters)
        self.api_key = str(api_key).strip().strip("'").strip('"')
        self.api_secret = str(api_secret).strip().strip("'").strip('"')
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        })

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        # Encode URL parameters properly into query string format
        query_string = urllib.parse.urlencode(sorted(params.items()))
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def post(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        params["timestamp"] = int(time.time() * 1000)
        params["signature"] = self._generate_signature(params)

        logger.debug(f"Sending POST request to {endpoint} with params: {params}")

        try:
            response = self.session.post(url, data=params, timeout=10)
            logger.debug(f"HTTP Status Code: {response.status_code}")
            
            payload = response.json()
            if response.status_code != 200:
                logger.error(f"API Error Response: {payload}")
                raise RuntimeError(f"Binance API Error [{payload.get('code')}]: {payload.get('msg')}")

            logger.info(f"API Request Succeeded | Endpoint: {endpoint} | OrderId: {payload.get('orderId')}")
            return payload

        except requests.exceptions.RequestException as e:
            logger.critical(f"Network error during POST {endpoint}: {str(e)}")
            raise ConnectionError(f"Network error connecting to Binance Testnet: {str(e)}")