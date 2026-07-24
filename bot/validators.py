from typing import Optional
from pydantic import BaseModel, Field, field_validator

class OrderInput(BaseModel):
    symbol: str = Field(..., description="Trading pair symbol, e.g., BTCUSDT")
    side: str = Field(..., description="BUY or SELL")
    order_type: str = Field(..., description="MARKET or LIMIT")
    quantity: float = Field(..., gt=0, description="Order quantity must be positive")
    price: Optional[float] = Field(None, description="Limit price, required for LIMIT orders")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        v_upper = v.strip().upper()
        if not v_upper.endswith("USDT") and not v_upper.endswith("BUSD"):
            raise ValueError("Symbol must end with USDT or BUSD (e.g., BTCUSDT)")
        return v_upper

    @field_validator("side")
    @classmethod
    def validate_side(cls, v: str) -> str:
        v_upper = v.strip().upper()
        if v_upper not in ["BUY", "SELL"]:
            raise ValueError("Side must be either BUY or SELL")
        return v_upper

    @field_validator("order_type")
    @classmethod
    def validate_order_type(cls, v: str) -> str:
        v_upper = v.strip().upper()
        if v_upper not in ["MARKET", "LIMIT", "STOP_LIMIT"]:
            raise ValueError("Order type must be MARKET, LIMIT, or STOP_LIMIT")
        return v_upper

    def check_type_specific_requirements(self):
        if self.order_type in ["LIMIT", "STOP_LIMIT"]:
            if self.price is None or self.price <= 0:
                raise ValueError(f"Price must be a positive number for {self.order_type} orders")