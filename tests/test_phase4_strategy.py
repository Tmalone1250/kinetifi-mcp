import pytest
import asyncio
from models.execution_intent import CrossChainExecutionIntent
from tools.generate_strategy import generate_strategy

@pytest.mark.asyncio
async def test_cross_chain_execution_intent_model():
    """Verify that the CrossChainExecutionIntent model strictly formats intent blueprints."""
    data = {
        "action_type": "bridge_and_swap",
        "source_network": "Mantle",
        "target_network": "Casper",
        "asset_to_deploy": "USDT",
        "estimated_amount": "1500.00",
        "target_protocol": "Friendly Market",
        "expected_apy": 22.5,
        "reasoning": "Highest cross-chain APY matched for held USDT."
    }
    
    intent = CrossChainExecutionIntent(**data)
    
    assert intent.action_type == "bridge_and_swap"
    assert intent.target_network == "Casper"
    assert intent.estimated_amount == "1500.00"
    assert intent.expected_apy == 22.5

@pytest.mark.asyncio
async def test_generate_strategy_tool():
    """Verify the generate_strategy tool properly matches a user portfolio to yields."""
    
    # Mock Portfolio Data: 5000 CSPR available
    portfolio = {
        "balances": [
            {
                "network": "Casper",
                "asset_symbol": "CSPR",
                "balance": "5000.0000",
                "usd_value_estimate": 150.0
            }
        ]
    }
    
    # Mock Yield Data: Friendly Market at 12% APY, Agni at 15% (but user doesn't hold MNT)
    yields = [
        {
            "network": "Casper",
            "dex_name": "Friendly Market",
            "trading_pair": "CSPR/USDC",
            "apy": 12.0,
            "pool_hash": "hash-friendly"
        },
        {
            "network": "Mantle",
            "dex_name": "Agni",
            "trading_pair": "MNT/USDT",
            "apy": 15.0,
            "pool_hash": "hash-agni"
        }
    ]
    
    # Call the tool function logic
    result = await generate_strategy("Maximize yield on my CSPR", portfolio, yields)
    
    assert result["action_type"] == "swap" # Source & Target are both Casper
    assert result["source_network"] == "Casper"
    assert result["target_network"] == "Casper"
    assert result["target_protocol"] == "Friendly Market"
    assert result["asset_to_deploy"] == "CSPR"
    assert result["estimated_amount"] == "5000.0000"
    assert result["expected_apy"] == 12.0
    assert "Friendly Market" in result["reasoning"]

@pytest.mark.asyncio
async def test_generate_strategy_tool_no_match():
    """Verify fallback behavior when no yields match the held portfolio assets."""
    portfolio = {
        "balances": [
            {
                "network": "Casper",
                "asset_symbol": "ABC",
                "balance": "100.0",
                "usd_value_estimate": 10.0
            }
        ]
    }
    yields = [
        {
            "network": "Casper",
            "dex_name": "Friendly Market",
            "trading_pair": "CSPR/USDC",
            "apy": 12.0,
            "pool_hash": "hash-friendly"
        }
    ]
    
    result = await generate_strategy("Do something", portfolio, yields)
    
    assert result["action_type"] == "hold"
    assert result["asset_to_deploy"] == "None"
    assert result["expected_apy"] == 0.0
