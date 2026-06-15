# **KinetiFi Orchestrator: Multi-MCP Integration & Telemetry Plan**

## **🌐 Context & Objective**

Path to KinetiFi Agent Directory: /home/tmalone1250/ToshibaDrive/Dev/DoraHacks/turing_test_hackathon_2026/

You are acting as the Lead AI Backend Architect for KinetiFi. We have successfully engineered two isolated MCP (Model Context Protocol) servers:

1. **The Brain (kinetifi-mcp)**: Read-only. Scans cross-chain yields, aggregates portfolio balances, and generates execution intents.  
2. **The Muscle (casper-mcp-py)**: Write-only. Safely constructs, signs, and broadcasts transactions to the Casper Network using local Ed25519 keys.

**The Objective:** We are now inside the main KinetiFi dashboard repository. We need to build the central intelligence loop that connects to BOTH servers simultaneously, provides their aggregated tools to our LLM, and streams real-time telemetry to our frontend UI.

## **🛠️ Phase 1: The Multi-Server Connection Manager**

**Target File:** backend/mcp\_manager.py (or equivalent)

**Requirements:**

1. **Async Context Management:** Create a class KinetiFiMCPManager that uses mcp.client.stdio.stdio\_client to spawn both servers as background processes.  
2. **Tool Aggregation:** The manager must query get\_tools() from both the Brain and the Muscle and merge them into a single, unified list.  
3. **Routing Logic:** When the LLM calls a tool, the manager must route the request to the correct underlying server based on the tool's origin.

## **📡 Phase 2: The Telemetry Interceptor**

**Target File:** backend/telemetry\_logger.py (or equivalent)

**Requirements:**

1. **Tool-Call Wrappers:** We must intercept the data *before* it goes to the MCP server and *after* the MCP server responds.  
2. **Standardized JSON Format:** Every tool execution must emit a payload looking like this:  
   {  
     "timestamp": "2026-06-06T21:45:00Z",  
     "server\_origin": "Brain | Muscle",  
     "tool\_name": "scan\_yields",  
     "status": "executing | success | error",  
     "input\_args": {...},  
     "output\_preview": "..."  
   }

3. **Frontend Emitter:** Hook this payload into our existing Websocket/Server-Sent-Events (SSE) stream so the UI dashboard updates dynamically as the agent "thinks".

## **🧠 Phase 3: The Agent Execution Loop**

**Target File:** backend/agent\_loop.py (or quivalent)

**Requirements:**

1. **LLM Integration:** Write the main async function run\_orchestration(user\_prompt: str).  
2. **Tool Provisioning:** Bind the unified tools from KinetiFiMCPManager to the LLM (OpenAI/Anthropic).  
3. **Execution Pipeline:** Feed the LLM a prompt like *"Maximize my idle CSPR"*. The LLM should autonomously decide to:  
   * Call get\_portfolio\_state (Brain)  
   * Call scan\_yields (Brain)  
   * Call generate\_strategy (Brain)  
   * Call BuildTransferTransaction or BuildDelegateTransaction (Muscle)  
   * Call SignAndSubmitTransaction (Muscle)

## **🛑 REQUIRED ACTION: HALT & VERIFY**

Before writing any code, you MUST halt and request the following context from the human developer:

1. The absolute file paths to the kinetifi-mcp/server.py and casper-mcp-py/server.py files.  
2. The absolute file path to the Casper .pem secret key file (needed for Muscle server arguments).  
3. The specific backend framework currently handling frontend Websockets/SSE (e.g., FastAPI, Flask) so the telemetry emitter can be correctly matched.

Acknowledge this plan and ask for the required paths to begin.