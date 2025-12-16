import httpx
import time

BASE_URL = "https://www.buda.com/api/v2"

VALID_PAIRS = {
    "BTC": ["CLP", "COP", "PEN"],
    "ETH": ["CLP", "COP", "PEN"],
    "BCH": ["CLP", "COP", "PEN"],
    "LTC": ["CLP", "COP", "PEN"],
    "USDC": ["CLP", "COP", "PEN"],
    "USDT": ["CLP", "COP", "PEN"],
}


class TickersCache:
    CACHE_TTL = 30
    
    def __init__(self):
        self.data = None
        self.timestamp = None
    
    def is_valid(self) -> bool:
        if self.data is None or self.timestamp is None:
            return False
        elapsed = time.time() - self.timestamp
        return elapsed < self.CACHE_TTL
    
    def get(self):
        if self.is_valid():
            return self.data
        return None
    
    def set(self, data):
        self.data = data
        self.timestamp = time.time()
    
    def clear(self):
        self.data = None
        self.timestamp = None


class BudaAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(f"Buda API Error ({status_code}): {message}")

"""
SUPUESTOS UTILIZADOS:
- Se hace llamdo a todos los tickers, esto se justifica por el tamaño del mismo
- Se cachean los datos por 30 segundos para evitar múltiples llamadas en corto tiempo
- Se considera de esta manera por ser un caso test
- Le implementaria una consulta por par en un caso real de producción, de esta menera solo se consulta lo necesario
"""
class BudaClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=5.0)
        self.cache = TickersCache()

    async def get_current_price(self, base_currency: str, quote_currency: str) -> float:
        base_upper = base_currency.upper()
        quote_upper = quote_currency.upper()
        market_id = f"{base_upper}-{quote_upper}"
        
        tickers_data = self.cache.get()
        
        if tickers_data is None:
            print(f"[API] Llamada a {market_id}")
            tickers_data = await self._fetch_tickers()
            self.cache.set(tickers_data)
        else:
            print(f"[CACHE] Usando datos cacheados para {market_id}")
        
        return self._extract_price_from_tickers(tickers_data, market_id)
    
    async def _fetch_tickers(self) -> dict:
        try:
            response = await self.client.get("/tickers")
            response.raise_for_status()
            data = response.json()
            
            if 'tickers' not in data:
                raise BudaAPIError("Respuesta inválida", status_code=400)
            
            return data
            
        except httpx.HTTPStatusError as e:
            raise BudaAPIError(
                f"Error API {e.response.status_code}",
                status_code=e.response.status_code
            ) from e
        except httpx.TimeoutException as e:
            raise BudaAPIError(
                "Timeout al conectar con API de Buda.com",
                status_code=504
            ) from e
        except httpx.ConnectError as e:
            raise BudaAPIError(
                "API de Buda.com no disponible",
                status_code=503
            ) from e
        except ValueError as e:
            raise BudaAPIError(
                "Respuesta inválida del servidor (no JSON)",
                status_code=500
            ) from e
        except httpx.RequestError as e:
            raise BudaAPIError(
                f"Error conexión: {e}",
                status_code=500
            ) from e
    
    def _extract_price_from_tickers(self, tickers_data: dict, market_id: str) -> float:
        for ticker in tickers_data.get('tickers', []):
            if ticker.get('market_id') == market_id:
                last_price = ticker.get('last_price')
                if last_price and len(last_price) > 0:
                    try:
                        return float(last_price[0])
                    except (ValueError, IndexError):
                        raise BudaAPIError(f"Precio inválido para {market_id}", status_code=500)
        
        raise BudaAPIError(f"Par {market_id} no encontrado", status_code=404)