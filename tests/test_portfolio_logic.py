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

        service = PortfolioService()
        
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
            assert total == expected

    @pytest.mark.asyncio
    async def test_invalid_currency_raises_error(self):
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
        service = PortfolioService()
        
        portfolio = PortfolioRequest(
            portfolio={"BTC": 1.0},
            fiat_currency="USD"  
        )
        
        with pytest.raises(BudaAPIError) as exc_info:
            await service.calculate_total_value(portfolio)
        
        assert exc_info.value.status_code == 400
        assert "BTC-USD" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_portfolio_returns_zero(self):
        service = PortfolioService()
        
        portfolio = PortfolioRequest(
            portfolio={},
            fiat_currency="CLP"
        )
        
        total = await service.calculate_total_value(portfolio)
        assert total == 0.0

    @pytest.mark.asyncio
    async def test_single_currency_btc(self):
        service = PortfolioService()
        
        with patch.object(service.client, 'get_current_price', new_callable=AsyncMock) as mock_price:
            mock_price.return_value = 46312554.36
            
            portfolio = PortfolioRequest(
                portfolio={"BTC": 1.0},
                fiat_currency="CLP"
            )
            
            total = await service.calculate_total_value(portfolio)

            assert total == 46312554.36

    @pytest.mark.asyncio
    async def test_quantity_zero(self):
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
    async def test_negative_quantity_raises_error(self):
        service = PortfolioService()
        
        with patch.object(service.client, 'get_current_price', new_callable=AsyncMock) as mock_price:
            mock_price.return_value = 46312554.36
            
            portfolio = PortfolioRequest(
                portfolio={"BTC": -0.5},
                fiat_currency="CLP"
            )
            
            with pytest.raises(BudaAPIError) as exc_info:
                await service.calculate_total_value(portfolio)

            assert exc_info.value.status_code == 400
            assert "negativa" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_multiple_fiat_currencies(self):
        service = PortfolioService()
        
        with patch.object(service.client, 'get_current_price', new_callable=AsyncMock) as mock_price:
            mock_price.return_value = 180000000.0  
            
            portfolio = PortfolioRequest(
                portfolio={"BTC": 0.5},
                fiat_currency="COP"
            )
            
            total = await service.calculate_total_value(portfolio)
            assert total == 0.5 * 180000000.0
