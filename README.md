# ⚽ Scoutly AI - Football Management System

## Project Overview & The Problem It Solves

Modern football clubs generate massive amounts of data—from financial constraints and wage structures to detailed player performance metrics and complex tactical systems. Traditionally, a Head Scout or Sporting Director must manually consult different departments (Finance, Data Analytics, Tactics/Coaching) to identify transfer targets that fit the club's budget, playstyle, and statistical benchmarks.

**Scoutly AI** solves this problem by providing a **multi-agent AI platform** powered by LangGraph, GPT-5/GPT-4o, SQLite, FastMCP, and WeasyPrint. It orchestrates a team of specialized AI agents that act as your virtual front office. When you ask a simple natural language query (e.g., *"Find me a box-to-box midfielder with high stamina and good passing"*), the system automatically:

1. **Checks Finances:** Determines your exact budget, salary caps, and negotiation margins.
2. **Scouts the Market:** Queries the club's SQLite player database dynamically.
3. **Analyzes Data:** Generates custom statistical visualizations (radars, scatter plots, trend lines).
4. **Evaluates Tactics:** Ranks players against the manager's tactical PDF playbook.
5. **Generates Reports:** Assembles a beautiful, management-ready PDF briefing with high-confidence recommendations.

---

## Architecture

```
User (natural language query)
         │ SSE stream
         ▼
┌─────────────────────────┐
│    FastAPI Backend      │  Port 8000
│    (SSE + REST API)     │
└──────────┬──────────────┘
           │
┌──────────▼──────────────────────────────────────────────┐
│                   Planner Agent                         │
│  loads prompts/planner.md + agent manifest at runtime   │
└──┬──────────┬──────────────┬───────────────┬────────────┘
   │          │              │               │
   ▼          ▼              ▼               ▼
Financial  Scouter       Analysis        Tactical
Agent      Agent         Agent           Agent
           │             │
        MCP Server    Python Sandbox
        (Port 8001)   (matplotlib charts)
           │
       SQLite DB
       (football.db)
                              └──→ WeasyPrint PDF
```

### MD-as-System-Prompt
Every agent loads its own system prompt from a `.md` file at runtime. Modify any `.md` file in the `prompts/` directory and it takes effect on the **next pipeline run** — no restart needed.

---

## Quick Start (Podman)

We use **Podman** for a fast, containerized start. All services (PostgreSQL, MCP Server, FastAPI Backend) are orchestrated seamlessly using a single PowerShell script.

### 1. Clone & Configure

```bash
git clone https://github.com/BasilReda/Scoutly-AI.git
cd Scoutly-AI

# Copy env template and fill in your Azure/OpenAI details
cp .env.example .env
# Edit .env and set your API keys
```

### 2. Start Services

Run the provided PowerShell script to build the images, create the network, and launch the backend and MCP servers (which automatically connects to the SQLite database).

```powershell
.\start_podman.ps1
```

*This script completely automates the setup. The API will be available at `http://localhost:8000` and the MCP server at `http://localhost:8001`.*

### 3. Open the UI

Navigate your browser to **http://localhost:8000** to access the premium dark-mode interface and start scouting!

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Frontend UI |
| `/api/scout` | POST | Start scouting pipeline (SSE stream) |
| `/api/download/{run_id}` | GET | Download PDF report |
| `/api/agents` | GET | List all available agents |
| `/api/prompt/{agent_name}` | GET | View an agent's system prompt |
| `/api/health` | GET | Health check |
| `/docs` | GET | Swagger UI |

**POST /api/scout** body:
```json
{
  "query": "Find me a striker under €70K/week who scores 15+ goals and fits a high-press system"
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
3. **Per-Player Profiles** (3–5 pages):
   - Stats grid, tactical verdict, strengths/weaknesses
   - Financial badge, analyst narrative
4. **Visual Analytics** — All 6 chart types embedded
5. **Tactical Appendix & Conclusion** — Formation context, final recommendation

---

## Customization

### Change Agent Behavior
Edit any file in `prompts/` — no restart needed. The agents reload prompts on every pipeline run.

### Change Financial Plan
Edit `data/financial_plan.yaml` — update budget, salary caps, or performance rules.

### Change Team Tactics
Replace `data/tactics.pdf` with your club's actual tactical document.

### Add More Players
Add rows to `data/players_seed.sql` and rebuild the database to re-seed the SQLite instance.
