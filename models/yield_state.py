from pydantic import BaseModel, Field

class CrossChainYieldState(BaseModel):
    """
    A highly condensed 'Delta' output representing a yield opportunity.
    This structure ensures LLM context window efficiency.
    """
    network: str = Field(..., description="The blockchain network (e.g., 'Casper', 'Mantle')")
    dex_name: str = Field(..., description="The name of the DEX protocol (e.g., 'Friendly Market', 'Agni Finance')")
    trading_pair: str = Field(..., description="The trading pair symbol (e.g., 'CSPR/USDC', 'MNT/USDT')")
    apy: float = Field(..., description="The current Annual Percentage Yield (APY) as a percentage")
    pool_hash: str = Field(..., description="The exact pool or contract package hash on the network")
