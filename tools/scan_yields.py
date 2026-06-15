import os
import asyncio
import aiohttp
from typing import List

from server import mcp
from models.yield_state import CrossChainYieldState

CSPR_CLOUD_BASE_URL = os.getenv("CSPR_CLOUD_BASE_URL", "https://api.testnet.cspr.cloud")
CSPR_CLOUD_API_KEY = os.getenv("CSPR_CLOUD_API_KEY", "")

async def fetch_mantle_yields() -> List[CrossChainYieldState]:
    """
    Fetches real Mantle APYs dynamically from DefiLlama open API.
    """
    yields = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://yields.llama.fi/pools") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pools = data.get("data", [])
                    
                    # Filter for Mantle chain pools
                    mantle_pools = [p for p in pools if p.get("chain") == "Mantle"]
                    
                    # We'll take the top 5 pools on Mantle by TVL
                    for p in mantle_pools[:5]:
                        yields.append(
                            CrossChainYieldState(
                                network="Mantle",
                                dex_name=p.get("project", "Unknown DEX"),
                                trading_pair=p.get("symbol", "Unknown Pair"),
                                apy=float(p.get("apy", 0.0)),
                                pool_hash=p.get("pool", "Unknown Pool Hash")
                            )
                        )
    except Exception as e:
        print(f"Error fetching Mantle yields from DefiLlama: {e}")
        
    return yields

async def fetch_casper_yields() -> List[CrossChainYieldState]:
    """
    Fetches active Casper APYs by querying CSPR.cloud endpoints.
    Scans recent swaps across all DEXs, retrieves live volumes, and calculates APYs.
    """
    headers = {
        "Accept": "application/json"
    }
    if CSPR_CLOUD_API_KEY:
        headers["Authorization"] = CSPR_CLOUD_API_KEY
        
    yields = []
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            # 1. Fetch active DEXs to map IDs to Names
            dexes_url = f"{CSPR_CLOUD_BASE_URL}/dexes"
            dex_map = {}
            async with session.get(dexes_url) as resp:
                if resp.status == 200:
                    dex_data = await resp.json()
                    for dex in dex_data.get("data", []):
                        d_id = dex.get("id") or dex.get("ID")
                        d_name = dex.get("name") or dex.get("Name", "Unknown DEX")
                        if d_id is not None:
                            dex_map[d_id] = d_name

            # 2. Fetch recent swaps to identify active pools
            swaps_url = f"{CSPR_CLOUD_BASE_URL}/swaps?page_size=20"
            active_pools = {}
            async with session.get(swaps_url) as resp:
                if resp.status == 200:
                    swaps_data = await resp.json()
                    for swap in swaps_data.get("data", []):
                        pair_hash = swap.get("pair_contract_package_hash")
                        if pair_hash and pair_hash not in active_pools:
                            active_pools[pair_hash] = {
                                "token0": swap.get("token0_contract_package_hash"),
                                "token1": swap.get("token1_contract_package_hash"),
                                "dex_id": swap.get("dex_id", 1)
                            }

            # 3. For each active pool, fetch live volume and calculate APY
            for pool_hash, pool_info in active_pools.items():
                token0 = pool_info["token0"]
                token1 = pool_info["token1"]
                dex_id = pool_info["dex_id"]
                dex_name = dex_map.get(dex_id, f"DEX {dex_id}")

                if not token0 or not token1:
                    continue

                rate_url = f"{CSPR_CLOUD_BASE_URL}/ft/{token0}/daily-dex-rates/latest?target_contract_package_hash={token1}"
                volume = 0.0
                
                try:
                    async with session.get(rate_url) as rate_resp:
                        if rate_resp.status == 200:
                            rate_data = await rate_resp.json()
                            vol_str = rate_data.get("data", {}).get("volume", "0")
                            volume = float(vol_str)
                except Exception:
                    pass
                
                # HACKATHON NOTE: Baseline TVL simulated here to bypass complex UREF global state queries on testnet. Live volume is used for dynamic APY calculation.
                baseline_tvl = 100000.0
                
                # Execute the Math: APY = ((24h_Volume * 0.003) * 365) / TVL * 100
                if volume > 0:
                    apy_estimate = ((volume * 0.003) * 365) / baseline_tvl * 100
                else:
                    apy_estimate = 0.0

                yields.append(
                    CrossChainYieldState(
                        network="Casper",
                        dex_name=dex_name,
                        trading_pair="Token0/Token1", # Generic pair fallback
                        apy=round(apy_estimate, 4),
                        pool_hash=pool_hash
                    )
                )

        except Exception as e:
            print(f"DEBUG: Exception during fetch_casper_yields: {e}")
            
    return yields

@mcp.tool()
async def scan_yields() -> str:
    """
    Aggregates APY data across Casper DEXs (Friendly Market) and Mantle (Agni/Moe).
    Returns a highly condensed 'Delta' representing the state of cross-chain yields.
    
    Returns:
        str: A JSON string representation of a list of CrossChainYieldState.
    """
    try:
        mantle_task = fetch_mantle_yields()
        casper_task = fetch_casper_yields()
        
        mantle_yields, casper_yields = await asyncio.gather(mantle_task, casper_task)
        
        all_yields = mantle_yields + casper_yields
        
        # Dump to native dicts and return as a JSON string to prevent FastMCP splitting
        import json
        return json.dumps([y.model_dump() for y in all_yields])
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return json.dumps([{"error": "Service Unavailable: Network timeout or failure."}])
    except Exception as e:
        return json.dumps([{"error": f"Service Unavailable: {str(e)}"}])
