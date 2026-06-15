import pytest
import asyncio
from unittest.mock import patch, MagicMock

from models.portfolio_state import AssetBalance, CrossChainPortfolioState
from tools.get_portfolio_state import fetch_casper_balances, fetch_mantle_balances, get_portfolio_state

@pytest.mark.asyncio
async def test_cross_chain_portfolio_state_model():
    """Verify that the CrossChainPortfolioState model properly formats and accepts data."""
    asset1 = {
        "network": "Casper",
        "asset_symbol": "CSPR",
        "balance": "100.5000",
        "usd_value_estimate": 3.50
    }
    
    state = CrossChainPortfolioState(balances=[asset1])
    
    assert len(state.balances) == 1
    assert state.balances[0].network == "Casper"
    assert state.balances[0].balance == "100.5000"

class MockAsyncContextManager:
    """Helper to mock an async context manager for aiohttp session responses."""
    def __init__(self, response):
        self.response = response
        
    async def __aenter__(self):
        return self.response
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_fetch_casper_balances(mock_get):
    """Verify fetch_casper_balances converts motes to standard CSPR correctly."""
    
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp_future = asyncio.Future()
    
    # Mock return 5,500,000,000 motes = 5.5 CSPR
    mock_resp_future.set_result({
        "data": {
            "balance": "5500000000"
        }
    })
    mock_resp.json = MagicMock(return_value=mock_resp_future)
    
    mock_get.return_value = MockAsyncContextManager(mock_resp)
    
    balances = await fetch_casper_balances("account-hash-123")
    
    assert len(balances) == 1
    assert balances[0].network == "Casper"
    assert balances[0].asset_symbol == "CSPR"
    assert balances[0].balance == "5.5000"

@pytest.mark.asyncio
async def test_fetch_mantle_balances():
    """Verify Mantle RPC skeleton correctly formats EVM wei to human readable decimals."""
    balances = await fetch_mantle_balances("0xMantleAddress")
    
    assert len(balances) == 2
    
    mnt_balance = next(b for b in balances if b.asset_symbol == "MNT")
    assert mnt_balance.balance == "5000.0000"
    
    usdt_balance = next(b for b in balances if b.asset_symbol == "USDT")
    assert usdt_balance.balance == "1500.00"

@pytest.mark.asyncio
@patch("tools.get_portfolio_state.fetch_casper_balances")
@patch("tools.get_portfolio_state.fetch_mantle_balances")
async def test_get_portfolio_state_mcp_tool(mock_mantle, mock_casper):
    """Verify the get_portfolio_state tool aggregates and dumps the global state dictionary."""
    
    mock_casper.return_value = [
        AssetBalance(network="Casper", asset_symbol="CSPR", balance="100.0000", usd_value_estimate=3.5)
    ]
    
    mock_mantle.return_value = [
        AssetBalance(network="Mantle", asset_symbol="MNT", balance="200.0000", usd_value_estimate=150.0)
    ]
    
    # Call the actual tool function directly
    result = await get_portfolio_state("casp123", "0xabc")
    
    assert "balances" in result
    assert len(result["balances"]) == 2
    
    symbols = [b["asset_symbol"] for b in result["balances"]]
    assert "CSPR" in symbols
    assert "MNT" in symbols
