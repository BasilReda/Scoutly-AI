"""
init_db.py — Initialize the SQLite football database.

Creates the database file, runs the schema + seed SQL,
then verifies the player count.

Usage:
    python data/init_db.py
"""
import sqlite3
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parent.parent          # project root
SQL_FILE = ROOT / "data" / "players_seed.sql"
DB_FILE  = ROOT / "data" / "football.db"


def init():
    print(f"[init_db] Database path : {DB_FILE}")
    print(f"[init_db] Seed SQL file : {SQL_FILE}")

    if not SQL_FILE.exists():
        print(f"[ERROR] Seed file not found: {SQL_FILE}", file=sys.stderr)
        sys.exit(1)

    sql = SQL_FILE.read_text(encoding="utf-8")

    # Split on semicolons so we can execute statement by statement
    # (sqlite3.executescript would work too, but this handles encoding better)
    with sqlite3.connect(str(DB_FILE)) as conn:
        conn.executescript(sql)
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
        positions = conn.execute(
            "SELECT position, COUNT(*) FROM players GROUP BY position ORDER BY position"
        ).fetchall()

    print(f"\n[init_db] ✓ Database initialised successfully")
    print(f"[init_db] ✓ {count} players loaded\n")
    print(f"{'Position':<10} {'Count':>6}")
    print("-" * 18)
    for pos, cnt in positions:
        print(f"{pos:<10} {cnt:>6}")
    print(f"\n[init_db] Ready → {DB_FILE}")


if __name__ == "__main__":
    init()
