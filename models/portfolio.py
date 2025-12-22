from typing import Dict
from pydantic import BaseModel, Field, ConfigDict


class PortfolioRequest(BaseModel):
    """Esquema para calcular el valor de un portafolio"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "portfolio": {
                    "BTC": 0.5,
                    "ETH": 2.0,
                    "USDT": 1000
                },
                "fiat_currency": "CLP"
            }
        }
    )
    
    portfolio: Dict[str, float] = Field(
        ...,
        title="Portfolio",
        description="Objeto con pares criptomoneda:cantidad. Criptos soportadas: BTC, ETH, BCH, LTC, USDC, USDT. Ejemplo: BTC=0.5, ETH=2.0, USDT=1000",
        examples=[{"BTC": 0.5, "ETH": 2.0, "USDT": 1000}]
    )
    fiat_currency: str = Field(
        ...,
        title="Moneda Fiat",
        description="Moneda fiat destino. Valores soportados: CLP, COP, PEN, USDC, BTC. La combinación cripto-fiat debe ser válida.",
        examples=["CLP"],
        min_length=2,
        max_length=10
    )


class PortfolioResponse(BaseModel):
    """Esquema de respuesta para el cálculo de valor de portafolio"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "portfolio_value": 46312554.36,
                "fiat_currency": "CLP"
            }
        }
    )
    
    portfolio_value: float = Field(
        ...,
        title="Valor Total",
        description="Valor total del portafolio convertido a la moneda fiat especificada",
        examples=[46312554.36]
    )
    fiat_currency: str = Field(
        ...,
        title="Moneda Fiat",
        description="Moneda en la que se calculó el valor total",
        examples=["CLP"]
    )


class PortfolioExactResponse(BaseModel):
    """Respuesta para el cálculo exacto: incluye desglose por moneda."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "portfolio_value": 46312554.36,
                "fiat_currency": "CLP",
                "breakdown": {
                    "BTC": 30000000.0,
                    "ETH": 1000000.0
                }
            }
        }
    )

    portfolio_value: float = Field(..., title="Valor Total (Exacto)")
    fiat_currency: str = Field(..., title="Moneda Fiat")
    breakdown: dict = Field(..., title="Desglose por moneda", description="Mapa moneda → valor en fiat")


class PortfolioExactRequest(BaseModel):
    """Esquema exacto mínimo: recibe `market_id` y `quantity` (cantidad a comprar)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "market_id": "btc-clp",
                "quantity": 0.5
            }
        }
    )

    market_id: str = Field(
        ...,
        title="Market ID",
        description="Identificador del mercado en formato 'base-quote' (p.ej. 'btc-clp')."
    )
    quantity: float = Field(
        ...,
        gt=0,
        title="Cantidad",
        description="Cantidad positiva de la moneda base a comprar."
    )
