# KinetiFi Cross-Chain MCP Server (`kinetifi-mcp`)

A high-performance Model Context Protocol (MCP) server built with Python and [FastMCP](https://github.com/modelcontextprotocol/python-sdk). This server coordinates cross-chain operations between the **Casper Network** and the **Mantle Network**, enabling agentic systems to scan yields, aggregate multi-chain portfolio balances, and generate intent-based execution strategies.

---

## Features

- **Cross-Chain Yield Scanner:** Connects to DefiLlama (for Mantle) and CSPR.cloud APIs (for Casper) to scan active DEX volumes, estimate APYs, and identify yield-generating pools.
- **Unified Portfolio Aggregator:** Aggregates and standardizes balances for both Casper and Mantle accounts, parsing raw base units (motes/wei) into standardized, human-readable decimal strings.
- **Intent-Based Strategy Generator:** Evaluates a user's natural language goal against their liquid holdings and active cross-chain yields to design optimal transaction paths (bridges, swaps, or stakes).
- **Stateless & Secure:** Functions strictly as a read-only advisor. It does not handle private keys or execute transactions, adhering to KinetiFi's Zero-Trust design.

---

## Repository Structure

```tree
kinetifi-mcp/
├── .ai_rules             # Local developer instructions
├── requirements.txt      # Python dependencies
├── server.py             # Server entrypoint and tool registration
├── models/               # Pydantic models defining standard schemas
│   ├── execution_intent.py   # Strategy intent blueprint schema
│   ├── portfolio_state.py    # Cross-chain asset balance schema
│   └── yield_state.py        # Cross-chain pool yield schema
├── tools/                # Sub-modules implementing individual query logic
│   ├── __init__.py
│   ├── generate_strategy.py  # Strategy formulation logic
│   ├── get_portfolio_state.py# Portfolio balancer logic
│   └── scan_yields.py        # DefiLlama and CSPR.cloud scanners
└── tests/                # Offline unit and integration tests
    ├── test_smoke.py         # Basic connection tests
    ├── test_phase2_yields.py # Yield scanner mock assertions
    ├── test_phase3_portfolio.py # Portfolio state mock tests
    └── test_phase4_strategy.py  # Intent strategy generator tests
```

---

## Prerequisites

Ensure you have the following installed:
- **Python 3.10+** (verified on Python 3.14)
- **Virtual Environment Tool** (`venv`)
- **MCP Host** (e.g., Claude Desktop, KinetiFi Agent, or any custom client)

---

## Installation & Setup

1. **Navigate to the Directory:**
   ```bash
   cd /home/tmalone1250/KinetiFi_local/KinetiFi/kinetifi-mcp
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Configuration

Set up your `.env` file in the project root to authenticate with Casper APIs:

```env
# KinetiFi MCP Environment Variables
CSPR_CLOUD_BASE_URL=https://api.testnet.cspr.cloud
CSPR_CLOUD_API_KEY=your_cspr_cloud_api_key_here
```

---

## Running the Server

### Development Mode (with Live Reload Dashboard)
```bash
fastmcp dev server.py
```

### Production Mode (stdio transport)
```bash
python server.py
```

---

## MCP Tool Reference

`kinetifi-mcp` exposes 4 tools to clients:

### 1. `get_status`
Checks the server health.
- **Response Format:**
  `"KinetiFi MCP Server is operational."`

---

### 2. `scan_yields`
Aggregates live yield opportunities across Casper DEXs (e.g., Friendly Market) and Mantle L2 DEXs (e.g., Agni, Merchant Moe).
- **Response Format:**
  A JSON string representing a list of cross-chain pool yields:
  ```json
  [
    {
      "network": "Mantle",
      "dex_name": "merchant-moe",
      "trading_pair": "WMNT-USDT",
      "apy": 45.2,
      "pool_hash": "0x365722f12ceb2063286a268B03c654Df81B7C00F"
    },
    {
      "network": "Casper",
      "dex_name": "Friendly Market",
      "trading_pair": "CSPR-USDC",
      "apy": 12.45,
      "pool_hash": "hash-abcd..."
    }
  ]
  ```

---

### 3. `get_portfolio_state`
Aggregates portfolio balances from Casper and Mantle addresses, converting them into standardized decimal representation.
- **Arguments:**
  - `casper_account` (string, required): The Casper public key or account hash.
  - `mantle_account` (string, required): The Mantle EVM wallet address.
- **Response Format:**
  ```json
  {
    "balances": [
      {
        "network": "Casper",
        "asset_symbol": "CSPR",
        "balance": "1500.2500",
        "usd_value_estimate": null
      },
      {
        "network": "Mantle",
        "asset_symbol": "USDC",
        "balance": "250.00",
        "usd_value_estimate": null
      }
    ]
  }
  ```

---

### 4. `generate_strategy`
Analyzes the aggregated portfolio and yield conditions to design a non-binding execution plan that maximizes yields or balances risks.
- **Arguments:**
  - `user_goal` (string, required): The user's goal (e.g. `"Maximize yield on my Casper assets"`).
  - `portfolio_state` (object, required): Output from `get_portfolio_state`.
  - `yield_state` (array, required): Output from `scan_yields`.
- **Response Format:**
  ```json
  {
    "action_type": "bridge_and_swap",
    "source_network": "Casper",
    "target_network": "Mantle",
    "asset_to_deploy": "CSPR",
    "estimated_amount": "1500.2500",
    "target_protocol": "merchant-moe",
    "expected_apy": 45.2,
    "reasoning": "Matched highest available APY (45.2%) on merchant-moe by routing CSPR to Mantle L2."
  }
  ```

---

## Testing

Run the test suite offline (all external API calls are fully mocked):
```bash
.venv/bin/pytest -v
```
