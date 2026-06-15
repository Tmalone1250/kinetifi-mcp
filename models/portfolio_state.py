from pydantic import BaseModel, Field
from typing import List, Optional

class AssetBalance(BaseModel):
    """
    Represents a normalized asset balance on a specific network.
    """
    network: str = Field(..., description="The blockchain network (e.g., 'Casper', 'Mantle')")
    asset_symbol: str = Field(..., description="The symbol of the asset (e.g., 'CSPR', 'MNT', 'USDT')")
    balance: str = Field(..., description="The human-readable decimal balance (e.g., '5.5000'), NOT raw motes/wei")
    usd_value_estimate: Optional[float] = Field(None, description="The estimated USD value of the balance")

class CrossChainPortfolioState(BaseModel):
    """
    A highly condensed 'Delta' representing a user's cross-chain portfolio.
    Used by the agent to instantly contextualize liquidity before routing intents.
    """
    balances: List[AssetBalance] = Field(default_factory=list, description="List of normalized asset balances across networks")
