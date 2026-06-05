# Wealth Coach Agent Roadmap

## Current Status

### V1 - Rule-Based Agent ✅

Current implementation:

* Python application
* Basic wealth tracking
* Goal evaluation
* Rule-based recommendations
* GitHub repository

---

## V2 - Improved Financial Assistant

Goals:

* Historical tracking
* Monthly snapshots
* Savings evolution
* Better recommendations

Features:

* Wealth history
* Monthly reports
* Progress visualization
* Goal tracking

---

## V3 - LLM-Powered Agent

Goals:

* Introduce AI reasoning
* Natural language interaction

Features:

* GPT or Claude integration
* Conversational financial analysis
* Dynamic recommendations
* Scenario simulation

Example:

"What happens if I invest €500 more per month?"

---

## V4 - Tool-Based Agent

Goals:

* Separate reasoning from data access

Tools:

* read_wealth()
* read_expenses()
* read_investments()
* create_monthly_plan()

Architecture:

User
→ LLM
→ Tools
→ Data
→ LLM
→ Recommendation

---

## V5 - MCP Integration

Goals:

* Learn Model Context Protocol
* Expose tools through MCP

Potential MCP tools:

* read_wealth()
* read_savings()
* read_investments()
* generate_report()

Learning objectives:

* MCP servers
* MCP clients
* Tool discovery
* Tool execution

---

## V6 - Real Integrations

Potential integrations:

* Banking APIs
* Investment platforms
* Spreadsheets
* Personal finance databases

---

## V7 - Autonomous Wealth Coach

Vision:

An AI agent capable of:

* Monitoring financial progress
* Detecting opportunities
* Identifying risks
* Generating recommendations
* Helping achieve long-term financial goals

Final architecture:

User
↓
LLM
↓
MCP
↓
Tools
↓
Financial Data
↓
Recommendations
