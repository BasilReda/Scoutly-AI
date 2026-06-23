"""
MCP Server — FastMCP-powered SQLite player database server.

Runs as a standalone HTTP service (SSE transport) on port 8001.
The Scouter Agent connects to it via the MCP client.

Tools exposed:
  - search_players     : Multi-criteria player search
  - get_player_stats   : Full stats for a single player by ID
  - query_players      : Raw SQL (SELECT only — read-only guard applied)
  - list_positions     : Returns all distinct positions in the DB
"""
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Optional

import aiosqlite
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env from project root
_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_root / ".env")

# ── Config ────────────────────────────────────────────────────────────────────
_db_path_raw = os.getenv("SQLITE_DB_PATH", "data/football.db")
DB_PATH = str((_root / _db_path_raw) if not Path(_db_path_raw).is_absolute() else Path(_db_path_raw))
MCP_PORT = int(os.getenv("MCP_SERVER_PORT", "8001"))

mcp = FastMCP("Football Player Database MCP Server")


# ── Row helper ────────────────────────────────────────────────────────────────

def _row_to_dict(row: aiosqlite.Row) -> dict:
    """Convert an aiosqlite Row (sqlite3.Row) to a plain JSON-serialisable dict."""
    d = dict(row)
    # seasons_data is stored as JSON TEXT in SQLite
    if "seasons_data" in d and isinstance(d["seasons_data"], str):
        try:
            d["seasons_data"] = json.loads(d["seasons_data"])
        except (json.JSONDecodeError, TypeError):
            pass
    return d


# ── MCP Tools ─────────────────────────────────────────────────────────────────

@mcp.tool()
async def search_players(
    position: Optional[str] = None,
    max_wage: Optional[int] = None,
    min_wage: Optional[int] = None,
    min_rating: Optional[int] = None,
    max_age: Optional[int] = None,
    min_age: Optional[int] = None,
    nationality: Optional[str] = None,
    min_goals: Optional[float] = None,
    limit: int = 10,
) -> list[dict]:
    """
    Search players using one or more filters.

    Args:
        position: Position code e.g. ST, CM, CB, LW, RW, CAM, CDM, LB, RB, GK
        max_wage: Maximum weekly wage in EUR
        min_wage: Minimum weekly wage in EUR
        min_rating: Minimum overall rating (0-99)
        max_age: Maximum player age
        min_age: Minimum player age
        nationality: Player nationality (partial match)
        min_goals: Minimum goals per season
        limit: Max number of results (default 10)

    Returns:
        List of matching player dicts ordered by overall_rating DESC.
    """
    conditions: list[str] = []
    params: list = []

    if position:
        conditions.append("position = ?")
        params.append(position.upper())
    if max_wage is not None:
        conditions.append("wage_eur <= ?")
        params.append(max_wage)
    if min_wage is not None:
        conditions.append("wage_eur >= ?")
        params.append(min_wage)
    if min_rating is not None:
        conditions.append("overall_rating >= ?")
        params.append(min_rating)
    if max_age is not None:
        conditions.append("age <= ?")
        params.append(max_age)
    if min_age is not None:
        conditions.append("age >= ?")
        params.append(min_age)
    if nationality:
        conditions.append("LOWER(nationality) LIKE LOWER(?)")
        params.append(f"%{nationality}%")
    if min_goals is not None:
        conditions.append("goals_per_season >= ?")
        params.append(min_goals)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.append(limit)

    sql = f"""
        SELECT * FROM players
        {where}
        ORDER BY overall_rating DESC
        LIMIT ?
    """

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()

    return [_row_to_dict(r) for r in rows]


@mcp.tool()
async def get_player_stats(player_id: int) -> dict:
    """
    Get the full statistical profile for a specific player by ID.

    Args:
        player_id: The player's database ID.

    Returns:
        Complete player dict or empty dict if not found.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM players WHERE id = ?", (player_id,))
        row = await cursor.fetchone()

    return _row_to_dict(row) if row else {}


@mcp.tool()
async def query_players(sql: str) -> list[dict]:
    """
    Execute a custom read-only SQL query against the players table.
    Only SELECT statements are permitted.

    Args:
        sql: A SELECT SQL query. Must not contain DML (INSERT/UPDATE/DELETE/DROP).

    Returns:
        List of result rows as dicts.
    """
    # Read-only guard
    forbidden = re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE)\b",
        re.IGNORECASE,
    )
    if forbidden.search(sql):
        raise ValueError("Only SELECT queries are allowed via this tool.")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(sql)
        rows = await cursor.fetchall()

    return [_row_to_dict(r) for r in rows]


@mcp.tool()
async def list_positions() -> list[str]:
    """
    Return all distinct player positions available in the database.

    Returns:
        Sorted list of position codes.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT DISTINCT position FROM players ORDER BY position"
        )
        rows = await cursor.fetchall()

    return [r["position"] for r in rows]


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # FastMCP 1.9.4 — port is set via settings, not as a run() kwarg
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = MCP_PORT
    mcp.run(transport="sse")
