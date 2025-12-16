from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from models.portfolio import PortfolioRequest, PortfolioResponse
from services.portfolio_service import PortfolioService
from clients.buda_client import BudaAPIError

import uvicorn

app = FastAPI(
    title="Portfolio Valuation API",
    description="API para calcular el valor total de un portafolio de criptomonedas en moneda fiat",
    version="1.0.0"
)
service = PortfolioService()


@app.exception_handler(BudaAPIError)
async def buda_api_error_handler(request, exc: BudaAPIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)}
    )


@app.get("/", tags=["Health"])
async def read_root():
    """Health check - verifica que el servidor está activo"""
    return {"Hello": "Hello Buda!"}


@app.post(
    "/v1/portfolio/value",
    tags=["Portfolio"],
    summary="Calcular valor de portafolio",
    description="Calcula el valor total de un portafolio de criptomonedas en una moneda fiat específica. "
                "Soporta múltiples criptomonedas (BTC, ETH, BCH, LTC, USDC, USDT) y monedas fiat (CLP, COP, PEN). "
                "Utiliza precios de mercado actuales obtenidos en tiempo real de Buda.com.",
    response_model=PortfolioResponse, 
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Valor total del portafolio calculado exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "portfolio_value": 46312554.36,
                        "fiat_currency": "CLP"
                    }
                }
            }
        },
        400: {
            "description": "Error en la solicitud o en la API de Buda.com.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "El par de mercado 'XRP-CLP' no está soportado para valorización directa."
                    }
                }
            }
        },
        422: {
            "description": "Error de validación del Request Body (Pydantic)."
        }
    }
)
async def calculate_portfolio_value(
    portfolio:PortfolioRequest
):
    """Calcula el valor total de un portafolio de criptomonedas."""
    total_value = await service.calculate_total_value(portfolio)
    """
    SUPUESTO UTILIZADO: 
    - Se retorna el valor total calculado y la moneda fiat en un dict, esto se considera importante para el response_model 
    """
    return {"portfolio_value": total_value, "fiat_currency": portfolio.fiat_currency}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)