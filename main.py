# SUPUESTOS UTILIZADOS:
# - Proyecto creado como prueba técnica (1.5 horas). Simplificaciones intencionales:
#   * Sin autenticación ni rate limiting.
#   * No hay gestión de secrets; usar variables de entorno en producción.
#   * Caché en memoria con TTL (por proceso) para reducir llamadas a Buda.com.
#   * Decisiones enfocadas a claridad y rapidez para la prueba; no a alta
#     disponibilidad o multi-replica.
#   * Logging reducido o deshabilitado por defecto (se puede activar si es
#     necesario).
# - Ver README para notas de seguridad y despliegue en Railway.

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from models.portfolio import PortfolioRequest, PortfolioResponse, PortfolioExactResponse
from services.portfolio_service import PortfolioService
from clients.buda_client import BudaAPIError
from config.constants import RESPONSE_FOR_PORTFOLIO_VALUE

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
    return {"Hello": "Hello Buda!"}

@app.post(
    "/v1/portfolio/value",
    tags=["Portfolio"],
    summary="Calcular valor de portafolio",
    response_model=PortfolioResponse, 
    status_code=status.HTTP_200_OK,
    responses=RESPONSE_FOR_PORTFOLIO_VALUE
)
async def calculate_portfolio_value(portfolio: PortfolioRequest):

    total_value = await service.calculate_total_value(portfolio)

    return {"portfolio_value": total_value, "fiat_currency": portfolio.fiat_currency}


@app.post(
    "/v1/portfolio/value/exact",
    tags=["Portfolio"],
    summary="Calcular valor exacto de portafolio (fill desde order book)",
    response_model=PortfolioExactResponse,
    status_code=status.HTTP_200_OK,
)
async def calculate_portfolio_value_exact(portfolio: PortfolioRequest):
    """Endpoint que calcula el valor exacto para un `PortfolioRequest` (todo el portafolio).

    Devuelve el diccionario {"portfolio_value": total, "fiat_currency": fiat, "breakdown": {...}}.
    """
    total_value, breakdown = await service.calculate_total_value_exact(portfolio)
    return {"portfolio_value": total_value, "fiat_currency": portfolio.fiat_currency, "breakdown": breakdown}

# definir endpoint

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)