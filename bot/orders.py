from typing import Dict, Any, Optional
from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging

logger = setup_logging()

class OrderManager:
    """Handles order creation logic and parameters parsing."""

    def __init__(self, client: BinanceFuturesClient):
        self.client = client

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        
        endpoint = "/fapi/v1/order"
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force

        logger.info(f"Initiating {side} {order_type} order for {quantity} {symbol} at price {price}")
        return self.client.post(endpoint, params)