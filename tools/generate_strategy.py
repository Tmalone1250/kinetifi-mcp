from typing import List, Dict
from server import mcp
from models.execution_intent import CrossChainExecutionIntent

@mcp.tool()
async def generate_strategy(user_goal: str, portfolio_state: dict, yield_state: List[dict]) -> dict:
    """
    Analyzes the portfolio state against active cross-chain yields to formulate an optimal execution strategy.
    This tool strictly returns a conceptual 'Intent' blueprint. It does NOT sign or execute transactions.
    
    Args:
        user_goal: The user's natural language goal (e.g., 'Maximize yield on my CSPR').
        portfolio_state: The JSON dict output representing global balances.
        yield_state: The JSON list output representing active protocols and APYs.
        
    Returns:
        dict: A serialized CrossChainExecutionIntent blueprint.
    """
    balances = portfolio_state.get("balances", [])
    
    best_yield = None
    target_asset = None
    available_balance = "0"
    source_network = ""
    
    # Deterministic matching logic:
    # Scan through user balances. If the asset has an active yield pair, track the highest APY.
    for balance_info in balances:
        symbol = balance_info.get("asset_symbol")
        net = balance_info.get("network")
        bal_str = balance_info.get("balance", "0")
        
        try:
            bal_val = float(bal_str)
        except ValueError:
            bal_val = 0.0
            
        if bal_val <= 0:
            continue
            
        # Cross-reference this held asset with active yields
        for y_info in yield_state:
            pair = y_info.get("trading_pair", "")
            # A simple assumption: if the symbol is in the trading pair, it's compatible
            if symbol and symbol in pair:
                apy = float(y_info.get("apy", 0.0))
                current_best_apy = float(best_yield.get("apy", 0.0)) if best_yield else 0.0
                
                if not best_yield or apy > current_best_apy:
                    best_yield = y_info
                    target_asset = symbol
                    available_balance = bal_str
                    source_network = net

    if not best_yield:
        # Fallback empty intent if no matching profitable routes are found
        intent = CrossChainExecutionIntent(
            action_type="hold",
            source_network="Unknown",
            target_network="Unknown",
            asset_to_deploy="None",
            estimated_amount="0",
            target_protocol="None",
            expected_apy=0.0,
            reasoning="No profitable yield opportunities matched the user's current liquid portfolio."
        )
        return intent.model_dump()
        
    target_net = best_yield.get("network")
    dex_name = best_yield.get("dex_name")
    apy = best_yield.get("apy")
    
    # Logic defining bridge vs direct swap
    action = "swap" if source_network == target_net else "bridge_and_swap"
    
    intent = CrossChainExecutionIntent(
        action_type=action,
        source_network=source_network,
        target_network=target_net,
        asset_to_deploy=target_asset,
        estimated_amount=available_balance,
        target_protocol=dex_name,
        expected_apy=float(apy),
        reasoning=f"Matched highest available APY ({apy}%) on {dex_name} for held asset {target_asset}."
    )
    
    return intent.model_dump()
