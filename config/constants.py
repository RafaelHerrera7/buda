# Constantes del proyecto

# Respuestas OpenAPI para el endpoint de valorización de portafolios
RESPONSE_FOR_PORTFOLIO_VALUE = {
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

# Configuración de Buda
BASE_URL = "https://www.buda.com/api/v2"

VALID_PAIRS = {
    "BTC": ["CLP", "COP", "PEN"],
    "ETH": ["CLP", "COP", "PEN"],
    "BCH": ["CLP", "COP", "PEN"],
    "LTC": ["CLP", "COP", "PEN"],
    "USDC": ["CLP", "COP", "PEN"],
    "USDT": ["CLP", "COP", "PEN"],
}
