from pydantic import BaseModel, Field

class CrossChainExecutionIntent(BaseModel):
    """
    The final strategy blueprint for cross-chain execution.
    This dictates the most optimal routing path matching the user's current liquidity state.
    """
    action_type: str = Field(..., description="The fundamental action (e.g., 'bridge_and_swap', 'stake', 'swap', 'hold')")
    source_network: str = Field(..., description="The network where the liquidity currently resides")
    target_network: str = Field(..., description="The destination network for the deployed assets")
    asset_to_deploy: str = Field(..., description="The symbol of the asset to route (e.g., 'CSPR', 'MNT')")
    estimated_amount: str = Field(..., description="The decimal amount to deploy")
    target_protocol: str = Field(..., description="The protocol targeted for deployment (e.g., 'Friendly Market', 'Agni Finance')")
    expected_apy: float = Field(..., description="The estimated APY for this strategy route")
    reasoning: str = Field(..., description="A short deterministic reasoning log explaining why this route was chosen")
