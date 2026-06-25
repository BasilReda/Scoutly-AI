# ⚽ Football AI Management System

A **multi-agent AI platform** for professional football club scouting, player analysis, and recruitment decisions — powered by GPT-4o, PostgreSQL, FastMCP, and WeasyPrint.

---

## Architecture

```
User (natural language query)
         │ SSE stream
         ▼
┌─────────────────────────┐
│    FastAPI Backend       │  Port 8000
│    (SSE + REST API)      │
└──────────┬──────────────┘
           │
┌──────────▼──────────────────────────────────────────────┐
│                   Planner Agent                          │
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
       PostgreSQL
       (Port 5432)
                              └──→ WeasyPrint PDF
```

### MD-as-System-Prompt
Every agent loads its own system prompt from a `.md` file at runtime:

| File | Agent |
|---|---|
| `prompts/planner.md` | Planner — reads all other agent .md files to build a dynamic manifest |
| `prompts/financial.md` | Financial Agent |
| `prompts/scouter.md` | Scouter Agent |
| `prompts/analysis.md` | Analysis Agent |
| `prompts/tactical.md` | Tactical Agent |
| `prompts/pdf_report.md` | PDF Narrative Agent |

Modify any `.md` file and it takes effect on the **next pipeline run** — no restart needed.

---

## Quick Start

### 1. Clone & Configure

```bash
git clone <repo-url>
cd football-ai

# Copy env template and fill in your OpenAI API key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

### 2. Start PostgreSQL (Podman)

```bash
podman run -d \
  --name football-postgres \
  -e POSTGRES_USER=football_user \
  -e POSTGRES_PASSWORD=football_pass \
  -e POSTGRES_DB=football_db \
  -p 5432:5432 \
  postgres:16-alpine

# Seed the player database (wait ~5s for postgres to start)
sleep 5
podman exec -i football-postgres psql -U football_user football_db < data/players_seed.sql
```

### 3. Generate the Tactics PDF (first time only)

```bash
pip install reportlab   # just for this one-time script
python data/generate_tactics_pdf.py
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the MCP Server

```bash
# Terminal 1
python -m backend.mcp_server.server
# Runs on http://localhost:8001
```

### 6. Start the FastAPI Backend

```bash
# Terminal 2
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Open the UI

Navigate to **http://localhost:8000**

---

## Using Podman (Individual Containers)

```bash
# Build backend image
podman build -f Containerfile.backend -t football-ai-backend .

# Build MCP server image
podman build -f Containerfile.mcp -t football-ai-mcp .

# Run PostgreSQL
podman run -d --name football-postgres \
  -e POSTGRES_USER=football_user \
  -e POSTGRES_PASSWORD=football_pass \
  -e POSTGRES_DB=football_db \
  -p 5432:5432 postgres:16-alpine

# Seed database
sleep 5
podman exec -i football-postgres psql -U football_user football_db < data/players_seed.sql

# Run MCP server (link to postgres)
podman run -d --name football-mcp \
  --add-host host.containers.internal:host-gateway \
  -e DATABASE_URL=postgresql://football_user:football_pass@host.containers.internal:5432/football_db \
  -e MCP_SERVER_PORT=8001 \
  -p 8001:8001 football-ai-mcp

# Run FastAPI backend
podman run -d --name football-api \
  --add-host host.containers.internal:host-gateway \
  -e OPENAI_API_KEY=sk-... \
  -e DATABASE_URL=postgresql://football_user:football_pass@host.containers.internal:5432/football_db \
  -e MCP_SERVER_HOST=host.containers.internal \
  -v $(pwd)/charts:/app/charts \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/data:/app/data \
  -p 8000:8000 football-ai-backend
```

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

## Project Structure

```
├── backend/
│   ├── main.py                    # FastAPI app + SSE endpoint
│   ├── agents/
│   │   ├── base.py                # BaseAgent (MD prompt loader + SSE emission)
│   │   ├── planner.py             # Orchestrator (GPT-4o function calling loop)
│   │   ├── financial.py           # Financial analysis
│   │   ├── scouter.py             # MCP-backed DB queries
│   │   ├── analysis.py            # Stats + chart generation
│   │   └── tactical.py            # Tactical fit ranking
│   ├── mcp_server/
│   │   └── server.py              # FastMCP PostgreSQL server
│   ├── sandbox/
│   │   └── executor.py            # Python code sandbox runner
│   ├── pdf/
│   │   ├── generator.py           # WeasyPrint PDF generator
│   │   └── templates/report.html  # Jinja2 HTML template
│   └── utils/
│       ├── config.py              # Settings from .env
│       └── prompt_loader.py       # MD prompt file loader
├── prompts/                       # Agent system prompts as .md files
│   ├── planner.md
│   ├── financial.md
│   ├── scouter.md
│   ├── analysis.md
│   ├── tactical.md
│   └── pdf_report.md
├── frontend/
│   ├── index.html                 # Premium dark UI
│   ├── style.css
│   └── app.js                     # SSE client + pipeline r
├── data/
│   ├── financial_plan.yaml        # Club financial constraints
│   ├── tactics.pdf                # Team tactical document (generated)
│   ├── generate_tactics_pdf.py    # One-time tactics PDF generator
│   └── players_seed.sql           # 55 mock players in PostgreSQL
├── charts/                        # Runtime chart PNGs (gitignored)
├── reports/                       # Runtime PDF reports (gitignored)
├── Containerfile.backend          # Podman backend container
├── Containerfile.mcp              # Podman MCP server container
├── requirements.txt
└── .env.example
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
Replace `data/tactics.pdf` with your club's actual tactical document (PDF, max ~20 pages).

### Add More Players
Add rows to `data/players_seed.sql` and re-run the seed script.
