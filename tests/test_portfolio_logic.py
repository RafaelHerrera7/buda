import pytest
from unittest.mock import AsyncMock, patch

from clients.buda_client import BudaAPIError
from models.portfolio import PortfolioRequest
from services.portfolio_service import PortfolioService

"""
SUPUESTOS UTILIZADOS:
- Solo se prueba logica de Negocio
- Se mockean llamadas a BudaClient.get_current_price
"""

class TestPortfolioLogic:
    """Tests enfocados en la lógica de negocio del portafolio"""

    @pytest.mark.asyncio
    async def test_portfolio_value_case_real(self):
        """
        Caso real: Portfolio con BTC (0.5), ETH (2.0) y USDT (1000)
        Debe retornar portfolio_value de 46312554.36 CLP
        
        Precios utilizados:
        - BTC: 80,000,000 CLP
        - ETH: 3,000,000 CLP
        - USDT: 312.554 CLP
        
        Cálculo:
        - 0.5 * 80000000 = 40,000,000 CLP
        - 2.0 * 3000000 = 6,000,000 CLP
        - 1000 * 312.554 = 312,554 CLP
        Total = 46,312,554 CLP
        """
        service = PortfolioService()
        
        # Definir precios para cada moneda
        prices = {
            ("BTC", "CLP"): 80000000.0,
            ("ETH", "CLP"): 3000000.0,
            ("USDT", "CLP"): 312.554,
        }
        
        async def mock_get_price(base, quote):
            key = (base.upper(), quote.upper())
            if key not in prices:
                raise BudaAPIError(f"Par no encontrado: {base}-{quote}", status_code=404)
            return prices[key]
        
        with patch.object(service.client, 'get_current_price', side_effect=mock_get_price):
            portfolio = PortfolioRequest(
                portfolio={
                    "BTC": 0.5,
                    "ETH": 2.0,
                    "USDT": 1000
                },
                fiat_currency="CLP"
            )
            
            total = await service.calculate_total_value(portfolio)
            
            expected = 46312554.0
            assert abs(total - expected) < 1.0  # Tolerancia para errores flotantes
            assert total > 1000
            assert total < 100000000

    @pytest.mark.asyncio
    async def test_invalid_currency_raises_error(self):
        """Caso: Moneda base inválida debe lanzar BudaAPIError"""
        service = PortfolioService()
        
        portfolio = PortfolioRequest(
            portfolio={"XYZ": 1.0},
            fiat_currency="CLP"
        )
        
        with pytest.raises(BudaAPIError) as exc_info:
            await service.calculate_total_value(portfolio)
        
        assert exc_info.value.status_code == 400
        assert "XYZ" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_pair_raises_error(self):
        """Caso: Par moneda-fiat inválido debe lanzar BudaAPIError"""
        service = PortfolioService()
        
        portfolio = PortfolioRequest(
            portfolio={"BTC": 1.0},
            fiat_currency="USD"  # USD no es soportado para BTC
        )
        
        with pytest.raises(BudaAPIError) as exc_info:
            await service.calculate_total_value(portfolio)
        
        assert exc_info.value.status_code == 400
        assert "BTC-USD" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_portfolio_returns_zero(self):
        """Caso: Portfolio vacío debe retornar 0"""
        service = PortfolioService()
        
        portfolio = PortfolioRequest(
            portfolio={},
            fiat_currency="CLP"
        )
        
        total = await service.calculate_total_value(portfolio)
        assert total == 0.0

    @pytest.mark.asyncio
    async def test_single_currency_btc(self):
        """Caso: Portfolio con una sola moneda (BTC)"""
        service = PortfolioService()
        
        with patch.object(service.client, 'get_current_price', new_callable=AsyncMock) as mock_price:
            mock_price.return_value = 46312554.36
            
            portfolio = PortfolioRequest(
                portfolio={"BTC": 1.0},
                fiat_currency="CLP"
            )
            
            total = await service.calculate_total_value(portfolio)
            
            assert total == 46312554.36
            assert total > 1000
            assert total < 100000000

    @pytest.mark.asyncio
    async def test_quantity_zero(self):
        """Caso: Cantidad cero debe contribuir 0 al total"""
        service = PortfolioService()
        
        with patch.object(service.client, 'get_current_price', new_callable=AsyncMock) as mock_price:
            mock_price.return_value = 46312554.36
            
            portfolio = PortfolioRequest(
                portfolio={"BTC": 0.0},
                fiat_currency="CLP"
            )
            
            total = await service.calculate_total_value(portfolio)
            assert total == 0.0

    @pytest.mark.asyncio
    async def test_negative_quantity_short_position(self):
        """Caso: Cantidad negativa (short) debe ser válida"""
        service = PortfolioService()
        
        with patch.object(service.client, 'get_current_price', new_callable=AsyncMock) as mock_price:
            mock_price.return_value = 46312554.36
            
            portfolio = PortfolioRequest(
                portfolio={"BTC": -0.5},
                fiat_currency="CLP"
            )
            
            total = await service.calculate_total_value(portfolio)
            assert total == -0.5 * 46312554.36

    @pytest.mark.asyncio
    async def test_multiple_fiat_currencies(self):
        """Caso: Diferentes monedas fiat (CLP, COP, PEN)"""
        service = PortfolioService()
        
        # Probar con COP
        with patch.object(service.client, 'get_current_price', new_callable=AsyncMock) as mock_price:
            mock_price.return_value = 180000000.0  # BTC en COP
            
            portfolio = PortfolioRequest(
                portfolio={"BTC": 0.5},
                fiat_currency="COP"
            )
            
            total = await service.calculate_total_value(portfolio)
            assert total == 0.5 * 180000000.0
