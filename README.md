# Scoutly AI — Football Scouting Pipeline

## Overview

Modern football clubs generate enormous amounts of data across finance, analytics, and tactics. Scouts and sporting directors must manually cross-reference all three departments to identify targets that fit budget, style, and statistical benchmarks.

**Scoutly AI** is a multi-agent AI platform that automates this workflow. A single natural-language query — *"Find me a box-to-box midfielder under €60K/week"* — triggers a full pipeline of specialized agents that check finances, scout the database, verify player existence, analyse stats, evaluate tactics, draft emails, and produce a management-ready PDF report.

---

## Architecture

```
User (natural language query)
         │ SSE stream
         ▼
┌──────────────────────────────┐
│      FastAPI Backend         │  Port 8000
│      (SSE + REST API)        │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────────────────────────────────────────────┐
│                         Planner Agent                                 │
│   Coordinates all sub-agents via LangGraph deepagents framework.      │
│   Runs Human-in-the-Loop (HITL) interrupt after each key stage.       │
└──┬──────┬──────┬─────────┬──────────┬────────┬───────────┬───────────┘
   │      │      │         │          │        │           │
   ▼      ▼      ▼         ▼          ▼        ▼           ▼
Financial Scouter Verifier Analysis Tactical  Email      PDF
Agent    Agent   Agent    Agent    Agent      Agent    Generator
           │       │                           │
        MCP SSE  MCP SSE                   SMTP / stub
        (8001)   (8001)
           │       │
        SQLite  SQLite
       (search) (verify)
```

### Pipeline Flow

```
query → Financial → [HITL] → Scouter ──→ Verifier ──→ [HITL] → Analysis → [HITL] → Tactical → [HITL] → Email → PDF
                                  ↑           │
                                  └───────────┘
                             re-scout if hallucination detected
                             (up to 3 automatic retries)
```

**Human-in-the-Loop (HITL):** After Financial and Scouter stages, the pipeline pauses so you can review results. You can approve (Proceed), request changes (type an adjustment and click Proceed), or stop the pipeline entirely. The pipeline only shows verified, non-hallucinated players.

---

## Agents

| Agent | File | Purpose |
|---|---|---|
| **Planner** | `backend/agents/planner.py` | Top-level orchestrator. Routes the query through the full pipeline using a LangGraph deepagents graph with MemorySaver checkpointing for HITL support. |
| **Financial** | `backend/agents/financial.py` | Reads `data/financial_plan.yaml` and the user query to extract `salary_min`, `salary_max`, and `value_max` budgets. Uses direct LLM JSON-mode call (no tool loop). |
| **Scouter** | `backend/agents/scouter.py` | Queries the SQLite player database via the MCP server using `search_players`. Returns a shortlist of candidates matching budget and position criteria. |
| **Verifier** | `backend/agents/verifier.py` | **Anti-hallucination guard.** Checks every scouted player name against the local database using `query_players` via MCP. If any name doesn't exist in the DB, the scouter is automatically re-run with explicit feedback. Runs silently — the user never sees hallucinated players. |
| **Analysis** | `backend/agents/analysis.py` | Generates statistical visualisations (radar charts, scatter plots, trend lines) using matplotlib. |
| **Tactical** | `backend/agents/tactical.py` | Reads `data/tactics.pdf` and ranks each player against the manager's tactical system, producing a verdict per player. |
| **Email** | `backend/agents/email_agent.py` | Drafts personalised player contact emails with exact salary figures and club context. |
| **PDF Generator** | `backend/pdf/generator.py` | Assembles a WeasyPrint PDF report with cover page, executive summary, per-player profiles, charts, and tactical appendix. |

All agents extend `BaseAgent` (`backend/agents/base.py`) which provides:
- **`system_prompt`** — hot-reloads from `prompts/<agent_name>.md` on every run (no restart needed)
- **`_run_deep_agent`** — runs a deepagents (LangGraph) loop with SSE event streaming
- **`_call_mcp_tool`** — connects to the MCP server via SSE and calls any registered tool
- **SSE emitters** — `emit_start`, `emit_progress`, `emit_complete`, `emit_error`

---

## MCP Server

The MCP server (`backend/mcp_server/server.py`) runs as a standalone FastMCP service on port 8001. Agents connect to it at runtime via SSE transport.

| Tool | Description |
|---|---|
| `search_players` | Multi-criteria player search (position, wage, rating, age, nationality, goals). Returns results ordered by `overall_rating DESC`. |
| `get_player_stats` | Full statistical profile for a player by database ID. |
| `query_players` | Raw read-only SQL against the `players` table. SELECT only — INSERT/UPDATE/DELETE/DROP are blocked. |
| `list_positions` | Returns all distinct position codes in the database. |
| `verify_player_on_fbref` | Searches FBref to check if a real footballer exists by name. Used as a secondary real-world existence check. |

---

## System Prompts

Every agent loads its system prompt from `prompts/<agent_name>.md` at runtime via `PromptLoader`. Edit any `.md` file and the change takes effect on the next pipeline run — **no container restart required**.

| File | Controls |
|---|---|
| `prompts/planner.md` | Orchestration strategy, tool ordering, stop conditions |
| `prompts/financial.md` | Budget extraction rules and output format |
| `prompts/scouter.md` | Player search strategy and output format |
| `prompts/scouter_task.md` | Task template injected per scouter run |
| `prompts/verifier.md` | Hallucination detection rules and feedback format |
| `prompts/analysis.md` | Chart generation instructions |
| `prompts/tactical.md` | Tactical evaluation criteria |
| `prompts/email_agent.md` | Email tone, structure, and salary accuracy rules |
| `prompts/email_draft.md` | Email template |
| `prompts/pdf_report.md` | PDF report structure and formatting |

---

## Quick Start (Podman)

### 1. Clone & Configure

```bash
git clone https://github.com/BasilReda/Scoutly-AI.git
cd Scoutly-AI

cp .env.example .env
# Fill in AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and deployment names
```

### 2. Start Services

```powershell
.\start_podman.ps1
```

This builds both container images, creates the `football-net` bridge network, and starts:
- `football-mcp` — MCP server on port 8001
- `football-backend` — FastAPI backend + frontend on port 8000

### 3. Open the UI

Navigate to **http://localhost:8000**

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Frontend UI |
| `/api/scout` | POST | Start scouting pipeline (SSE stream) |
| `/api/hitl/{run_id}` | POST | Submit HITL decision (proceed / adjust / stop) |
| `/api/download/{run_id}` | GET | Download PDF report |
| `/api/agents` | GET | List all available agents |
| `/api/prompt/{agent_name}` | GET | View an agent's live system prompt |
| `/api/health` | GET | Health check |
| `/docs` | GET | Swagger UI |

**Start a pipeline:**
```json
POST /api/scout
{
  "query": "Find me a striker under €70K/week who scores 15+ goals and fits a high-press system"
}
```

**Submit a HITL decision:**
```json
POST /api/hitl/{run_id}
{
  "action": "proceed",
  "comment": ""
}
```
```json
POST /api/hitl/{run_id}
{
  "action": "adjust",
  "comment": "Raise the max salary to €80K/week and look for players with more assists"
}
```

---

## Example Queries

- `Find me a striker under €70K/week who scores 15+ goals`
- `Scout a young left winger under 24 with pace above 88`
- `Find a box-to-box midfielder with high stamina and pass accuracy above 85`
- `I need a ball-playing centre-back under €55K/week`
- `Find me a goalscoring attacking midfielder under €65K/week`

---

## PDF Report Contents

1. **Cover Page** — Mission summary, team, date, run ID
2. **Executive Summary** — Top-line findings, stat cards, ranked table
3. **Per-Player Profiles** (3–5 pages each):
   - Stats grid, tactical verdict, strengths / weaknesses
   - Financial badge, analyst narrative
4. **Visual Analytics** — All chart types embedded
5. **Tactical Appendix & Conclusion** — Formation context, final recommendation

---

## Customization

| What to change | How |
|---|---|
| Agent reasoning / tone | Edit any file in `prompts/` — takes effect immediately, no restart |
| Financial constraints | Edit `data/financial_plan.yaml` |
| Tactical playbook | Replace `data/tactics.pdf` |
| Player database | Add rows to `data/players_seed.sql` and rebuild the DB |
| LLM model | Update deployment names in `.env` |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Agent framework | [deepagents](https://pypi.org/project/deepagents/) 0.6.11 on LangGraph 1.2.6 |
| LLM | Azure OpenAI (GPT-4o / GPT-4.1) |
| Orchestration | LangGraph with MemorySaver checkpointing (HITL via `interrupt()`) |
| MCP server | FastMCP 1.9.4 (SSE transport) |
| Database | SQLite via aiosqlite |
| Backend | FastAPI + asyncio SSE streaming |
| Charts | matplotlib |
| PDF | WeasyPrint |
| Containers | Podman (two images: `football-backend`, `football-mcp`) |
