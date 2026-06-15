import os
import asyncio
import aiohttp
from typing import List

from server import mcp
from models.portfolio_state import AssetBalance, CrossChainPortfolioState

CSPR_CLOUD_BASE_URL = os.getenv("CSPR_CLOUD_BASE_URL", "https://api.testnet.cspr.cloud")
CSPR_CLOUD_API_KEY = os.getenv("CSPR_CLOUD_API_KEY", "")

# Decimal conversion constants
CSPR_DECIMALS = 9
MNT_DECIMALS = 18

async def fetch_mantle_balances(account_address: str) -> List[AssetBalance]:
    """
    Fetches live Mantle balances. Currently unimplemented.
    """
    # TODO: Implement live Web3 provider or RPC logic for Mantle token contracts
    return []

async def fetch_casper_balances(account_identifier: str) -> List[AssetBalance]:
    """
    Fetches Casper balances by querying CSPR.cloud accounts endpoint.
    Converts raw motes to standardized CSPR decimal strings.
    """
    headers = {
        "Accept": "application/json"
    }
    if CSPR_CLOUD_API_KEY:
        headers["Authorization"] = CSPR_CLOUD_API_KEY
        
    balances = []
    
    async with aiohttp.ClientSession(headers=headers) as session:
        account_url = f"{CSPR_CLOUD_BASE_URL}/accounts/{account_identifier}"
        try:
            async with session.get(account_url) as resp:
                if resp.status == 200:
                    payload = await resp.json()
                    
                    # CSPR.cloud returns standard account data with the 'balance' in motes
                    account_data = payload.get("data", {})
                    motes_balance_str = account_data.get("balance", "0")
                    
                    try:
                        motes_balance = int(motes_balance_str)
                    except (ValueError, TypeError):
                        motes_balance = 0
                        
                    cspr_balance = motes_balance / (10 ** CSPR_DECIMALS)
                    
                    balances.append(
                        AssetBalance(
                            network="Casper",
                            asset_symbol="CSPR",
                            balance=f"{cspr_balance:.4f}",
                            usd_value_estimate=None # Would require a price oracle endpoint
                        )
                    )
        except Exception as e:
            print(f"Error fetching Casper balances: {e}")
            
    return balances

@mcp.tool()
async def get_portfolio_state(casper_account: str, mantle_account: str) -> dict:
    """
    Aggregates global cross-chain portfolio state across Casper and Mantle networks.
    Automatically standardizes base unit integers (motes/wei) into LLM-friendly decimals.
    
    Args:
        casper_account: The Casper account hash or public key.
        mantle_account: The Mantle EVM address.
        
    Returns:
        dict: A CrossChainPortfolioState 'Delta' representation.
    """
    casper_task = fetch_casper_balances(casper_account)
    mantle_task = fetch_mantle_balances(mantle_account)
    
    casper_bals, mantle_bals = await asyncio.gather(casper_task, mantle_task)
    
    state = CrossChainPortfolioState(
        balances=casper_bals + mantle_bals
    )
    
    return state.model_dump()
