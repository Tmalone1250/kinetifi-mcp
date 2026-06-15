import pytest
import asyncio
from unittest.mock import patch, MagicMock

from models.yield_state import CrossChainYieldState
from tools.scan_yields import fetch_casper_yields, fetch_mantle_yields, scan_yields

@pytest.mark.asyncio
async def test_cross_chain_yield_state_model():
    """Verify that the CrossChainYieldState model correctly validates types."""
    data = {
        "network": "Casper",
        "dex_name": "Friendly Market",
        "trading_pair": "CSPR/USDC",
        "apy": 15.4,
        "pool_hash": "hash-12345"
    }
    state = CrossChainYieldState(**data)
    
    assert state.network == "Casper"
    assert state.apy == 15.4
    assert state.pool_hash == "hash-12345"

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
async def test_fetch_casper_yields_friendly_market(mock_get):
    """Verify fetch_casper_yields correctly targets 'Friendly Market' using aiohttp mocks."""
    
    # Mock Response 1: /dexes
    mock_dex_resp = MagicMock()
    mock_dex_resp.status = 200
    mock_dex_resp_future = asyncio.Future()
    mock_dex_resp_future.set_result({
        "data": [
            {"name": "Other DEX", "contract_package_hash": "hash-other"},
            {"name": "Friendly Market", "contract_package_hash": "hash-friendly"}
        ]
    })
    mock_dex_resp.json = MagicMock(return_value=mock_dex_resp_future)
    
    # Mock Response 2: /dex-rates/latest
    mock_rate_resp = MagicMock()
    mock_rate_resp.status = 200
    mock_rate_resp_future = asyncio.Future()
    mock_rate_resp_future.set_result({
        "data": {
            "apy_estimate": "12.34"
        }
    })
    mock_rate_resp.json = MagicMock(return_value=mock_rate_resp_future)
    
    # Route the requests based on URL
    def side_effect(url, *args, **kwargs):
        if "/dexes" in url:
            return MockAsyncContextManager(mock_dex_resp)
        elif "/dex-rates/latest" in url:
            return MockAsyncContextManager(mock_rate_resp)
        return MockAsyncContextManager(MagicMock(status=404))

    mock_get.side_effect = side_effect
    
    yields = await fetch_casper_yields()
    
    # We expect 1 yield specifically from Friendly Market
    assert len(yields) == 1
    assert yields[0].network == "Casper"
    assert yields[0].dex_name == "Friendly Market"
    assert yields[0].pool_hash == "hash-friendly"
    assert yields[0].apy == 12.34

@pytest.mark.asyncio
async def test_fetch_mantle_yields_skeleton():
    """Verify that Mantle returns the mock Web3 schema skeleton."""
    mantle_yields = await fetch_mantle_yields()
    
    assert len(mantle_yields) == 2
    assert mantle_yields[0].network == "Mantle"
    assert mantle_yields[0].dex_name in ["Agni Finance", "Merchant Moe"]

@pytest.mark.asyncio
@patch("tools.scan_yields.fetch_casper_yields")
@patch("tools.scan_yields.fetch_mantle_yields")
async def test_scan_yields_mcp_tool(mock_mantle, mock_casper):
    """Verify the scan_yields MCP tool properly triggers and aggregates lists."""
    mock_mantle.return_value = [
        CrossChainYieldState(network="Mantle", dex_name="Agni", trading_pair="MNT", apy=10.0, pool_hash="abc")
    ]

    mock_casper.return_value = [
        CrossChainYieldState(network="Casper", dex_name="Friendly", trading_pair="CSPR", apy=12.0, pool_hash="def")
    ]
    
    result = await scan_yields()  # Call the decorated function directly
    
    assert len(result) == 2
    
    # Validates data is dumped to standard Python dictionaries
    assert isinstance(result[0], dict)
    
    networks = [r["network"] for r in result]
    assert "Mantle" in networks
    assert "Casper" in networks
