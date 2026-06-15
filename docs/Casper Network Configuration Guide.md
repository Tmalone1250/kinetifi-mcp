# **KinetiFi: Casper Network DEX & Configuration Guide**

### ***Target Protocol Coordinates for the KinetiFi Brain***

## **1\. The Primary DEX Targets (Casper Ecosystem)**

Unlike Mantle, which has dozens of Uniswap V2/V3 forks, Casper's liquidity is highly concentrated. Following manual field verification, we are targeting these specific AMMs:

1. **Friendly Market (Phase 1 Focus):** The primary actively functioning and deeply liquid AMM verified for this buildathon. It handles the bulk of standard CSPR and bridged asset swaps.  
2. **CSPR.trade (Phase 2 Expansion):** Our secondary target for yield scanning and arbitrage. We will integrate this once the Friendly Market pipeline is fully validated.

*(Note: Previously documented DEXs like CasperSwap and Swappery have been deprecated from the KinetiFi target list due to inactive frontends/stale liquidity).*

## **2\. The "Cheat Code" (Data Retrieval Strategy)**

On Mantle, we had to write an "Alpha Factory Resolver" to manually query the Agni and Merchant Moe factory smart contracts on-chain to find pool addresses.

**On Casper, we don't have to do that.**

Because we are utilizing the CSPR.cloud API, the infrastructure already indexes DEX data natively. KinetiFi's brain will hit these API endpoints, filtering specifically for Friendly Market (and eventually CSPR.trade) data:

* /dexes: Returns the active DEXs on the network (used to programmatically grab the DEX's exact contract package hash).  
* /ft/{contractPackageHash}/dex-rates/latest: Returns the exact exchange rate for a fungible token specifically filtered by the DEX.  
* /swaps: Returns live, historical swap volume and execution prices.

## **3\. Implementation: The scan\_yields Strategy**

Inside the kinetifi-mcp server, our scan\_yields tool will aggregate data by executing the following pipeline:

1. **Fetch Mantle APYs:** Call the existing Web3 Python logic to hit Agni Finance/Merchant Moe.  
2. **Fetch Casper APYs:** Make an asynchronous REST call to the CSPR.cloud DEX endpoints, initially isolating data tied to the Friendly Market protocol.  
3. **The "Delta" Output:** Condense both data streams into a single Pydantic model (CrossChainYieldState) so the LLM Agent can instantly see if bridging liquidity from Mantle to Casper is profitable.