# SUPUESTOS UTILIZADOS (cliente Buda):
# - Se descarga el listado completo de /tickers y se cachea durante 30s.
# - Esta aproximación es válida para la prueba; en producción preferiría
#   consultas por par y/o un cache centralizado compartido entre réplicas.
# - La caché es en memoria y por proceso; no cubre casos multi-replica.
# - Se normalizan errores httpx a BudaAPIError con status_code apropiado.
# - Timeout 5s y manejo de errores (503/504/500) para comunicarse con Buda.

import httpx
import time

from config.constants import BASE_URL, VALID_PAIRS


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

class BudaClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=5.0)
        self.cache = TickersCache()

    # caso valor más exacto
    async def calculate_total_value_exact(self, base_currency: str, quote_currency: str) -> dict:
        """Devuelve el `order_book` del mercado sin procesarlo.

        Se delega en `_fetch_order_book` para obtener el payload y se retorna
        el diccionario `order_book` tal cual (contiene `asks` y `bids`).
        """
        order_book = await self._fetch_order_book(f"{base_currency.upper()}-{quote_currency.upper()}")
        return order_book
    
    async def get_current_price(self, base_currency: str, quote_currency: str) -> float:
        """Obtiene el último precio para un par de mercado.

        Esta función utiliza la caché de `/tickers` para reducir llamadas de
        red. Si la caché está vacía o expirada, solicita los tickers a Buda y
        luego extrae el precio solicitado.

        Args:
            base_currency (str): Código de la moneda base (p. ej. "BTC").
            quote_currency (str): Código de la moneda cotizada (p. ej. "CLP").

        Returns:
            float: Último precio negociado para el par.

        Raises:
            BudaAPIError: Si el par no existe o si hay errores de red/HTTP al
                obtener los datos. La excepción incluye `status_code`.
        """
        base_upper = base_currency.upper()
        quote_upper = quote_currency.upper()
        market_id = f"{base_upper}-{quote_upper}"
        
        tickers_data = self.cache.get()
        
        if tickers_data is None:
            tickers_data = await self._fetch_tickers()
            self.cache.set(tickers_data)
        else:
            pass
        
        return self._extract_price_from_tickers(tickers_data, market_id)
    
    async def _fetch_order_book(self, market_id: str) -> dict:
        try:
            response = await self.client.get(f"/markets/{market_id}/order_book")
            response.raise_for_status()
            data = response.json()
            if 'order_book' not in data:
                raise BudaAPIError("Respuesta inválida", status_code=400)
            return data['order_book']
        except httpx.HTTPStatusError as e:
            raise BudaAPIError(
                f"Error API {e.response.status_code}",
                status_code=e.response.status_code
            ) from e
            
    async def _fetch_tickers(self) -> dict:
        """Solicita y valida el payload de `/tickers` desde Buda.

        Realiza la petición HTTP, valida la estructura y devuelve el JSON.
        Los errores de red y de respuesta se traducen a `BudaAPIError` con un
        `status_code` apropiado.

        Returns:
            dict: JSON con la clave `tickers`.

        Raises:
            BudaAPIError: En caso de HTTP status no exitoso, timeout, problemas
                de conexión o respuesta inválida/no JSON.
        """
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
        """Extrae el último precio para un `market_id` del payload de tickers.

        Busca el ticker correspondiente y parsea `last_price` a float.

        Args:
            tickers_data (dict): JSON con la lista `tickers`.
            market_id (str): Identificador del mercado, p. ej. 'BTC-CLP'.

        Returns:
            float: Último precio registrado para el par.

        Raises:
            BudaAPIError: 500 si el precio no se puede parsear; 404 si el par
                no se encuentra en el payload.
        """
        for ticker in tickers_data.get('tickers', []):
            if ticker.get('market_id') == market_id:
                last_price = ticker.get('last_price')
                if last_price and len(last_price) > 0:
                    try:
                        return float(last_price[0])
                    except (ValueError, IndexError):
                        raise BudaAPIError(f"Precio inválido para {market_id}", status_code=500)
        
        raise BudaAPIError(f"Par {market_id} no encontrado", status_code=404)