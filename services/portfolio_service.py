from clients.buda_client import BudaClient, BudaAPIError, VALID_PAIRS
from models.portfolio import PortfolioRequest


class PortfolioService:
    def __init__(self):
        self.client = BudaClient()

    async def calculate_total_value(self, portfolio_data: PortfolioRequest) -> float:
        """
        Calcula el valor total del portafolio en la moneda solicitada.

        Args:
            portfolio_data: Datos del portafolio con monedas y cantidad de cada una.

        Returns:
            El valor total del portafolio en la moneda fiat solicitada.
        """
        fiat_upper = portfolio_data.fiat_currency.upper()
        
        for base_currency, qty in portfolio_data.portfolio.items():
            if qty < 0:
                raise BudaAPIError(
                    f"Cantidad inválida (negativa) para {base_currency}: {qty}",
                    status_code=400
                )

        for base_currency in portfolio_data.portfolio.keys():
            base_upper = base_currency.upper()
            
            if base_upper not in VALID_PAIRS:
                raise BudaAPIError(
                    f"La moneda base '{base_upper}' no es soportada.",
                    status_code=400
                )
            
            if fiat_upper not in VALID_PAIRS[base_upper]:
                raise BudaAPIError(
                    f"El par '{base_upper}-{fiat_upper}' no es válido. Las monedas fiat soportadas para {base_upper} son: {', '.join(VALID_PAIRS[base_upper])}.",
                    status_code=400
                )
        
        total_value = 0.0

        for base_currency, quantity in portfolio_data.portfolio.items():
            price = await self.client.get_current_price(base_currency, portfolio_data.fiat_currency)

            total_value += price * float(quantity)

        return total_value
