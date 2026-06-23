"""
Analysis Agent — performs deep statistical analysis and generates all 6 visualizations.

Flow:
  1. Receive shortlisted player profiles from Scouter Agent
  2. Ask GPT-4o (using analysis.md prompt) to generate Python visualization code
  3. Execute each chart script in the Python sandbox
  4. Ask GPT-4o to write per-player analysis reports
  5. Unify all reports into one consolidated document
  6. Return charts list + unified report
"""
import asyncio
import json
from typing import Any

from openai import AsyncOpenAI

from .base import BaseAgent
from ..sandbox.executor import run_visualization_code


# ── Position-average benchmarks for radar charts ─────────────────────────────
POSITION_AVERAGES: dict[str, dict] = {
    "ST":  {"attacking": 80, "defending": 35, "sprint_speed": 78, "stamina": 75, "dribble_success": 65, "physicality": 78},
    "LW":  {"attacking": 78, "defending": 32, "sprint_speed": 85, "stamina": 78, "dribble_success": 75, "physicality": 60},
    "RW":  {"attacking": 78, "defending": 32, "sprint_speed": 85, "stamina": 78, "dribble_success": 75, "physicality": 60},
    "CAM": {"attacking": 82, "defending": 40, "sprint_speed": 78, "stamina": 79, "dribble_success": 72, "physicality": 62},
    "CM":  {"attacking": 72, "defending": 55, "sprint_speed": 74, "stamina": 83, "dribble_success": 65, "physicality": 66},
    "CDM": {"attacking": 58, "defending": 80, "sprint_speed": 70, "stamina": 84, "dribble_success": 58, "physicality": 80},
    "CB":  {"attacking": 48, "defending": 85, "sprint_speed": 65, "stamina": 77, "dribble_success": 44, "physicality": 83},
    "LB":  {"attacking": 65, "defending": 74, "sprint_speed": 79, "stamina": 80, "dribble_success": 60, "physicality": 71},
    "RB":  {"attacking": 65, "defending": 74, "sprint_speed": 79, "stamina": 80, "dribble_success": 60, "physicality": 71},
    "GK":  {"attacking": 18, "defending": 75, "sprint_speed": 52, "stamina": 70, "dribble_success": 32, "physicality": 73},
}


class AnalysisAgent(BaseAgent):
    AGENT_NAME = "analysis"

    def __init__(self, client: AsyncOpenAI, sse_queue: asyncio.Queue):
        super().__init__(client, sse_queue)

    async def run(
        self,
        players: list[dict],
        run_id: str,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Perform full statistical analysis and generate visualizations.

        Args:
            players: List of player dicts from ScouterAgent.
            run_id:  Unique pipeline run ID (used for chart output directory).

        Returns:
            {
                "charts": list of absolute chart file paths,
                "player_reports": {name: markdown_text},
                "unified_report": full consolidated markdown report,
            }
        """
        await self.emit_start(f"Starting analysis of {len(players)} candidates...")

        all_charts: list[str] = []
        player_reports: dict[str, str] = {}

        # Determine position averages (use the first player's position as reference)
        position = players[0].get("position", "ST") if players else "ST"
        pos_avg = POSITION_AVERAGES.get(position, POSITION_AVERAGES["ST"])

        # ── Step 1: Generate visualization code via LLM ────────────────────
        await self.emit_progress("Generating visualization scripts via AI...")

        viz_data = {
            "players": players,
            "position_averages": pos_avg,
            "position": position,
        }

        viz_code_result = await self.chat_json(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Generate Python visualization code for these {len(players)} football players.\n"
                        f"Player data:\n{json.dumps(viz_data, indent=2)}\n\n"
                        "Create SIX separate charts. Write the code for ALL of them in a single Python script.\n\n"
                        "CHART 1 — Radar/Spider Chart: Compare each player's (attacking, defending, sprint_speed, stamina, dribble_success, physicality) "
                        "vs position_averages. Use matplotlib fill_between on polar axes. One subplot per player.\n\n"
                        "CHART 2 — Salary vs Performance Scatter: X=wage_eur, Y=(goals_per_season*2 + assists_per_season*1.5 + overall_rating*0.5). "
                        "Annotate each point. Add shaded 'value zone' (low wage, high performance). Save as 'scatter_comparison.png'.\n\n"
                        "CHART 3 — Pitch Heatmap: Draw a simple green football pitch (rectangle, centre circle, penalty areas). "
                        "Plot each player's position zone with a scatter point + name. Save as 'pitch_heatmap.png'.\n\n"
                        "CHART 4 — Historical Trend: Per player, line chart of goals and assists from seasons_data. "
                        "Subplots side by side. Save as 'historical_trends.png'.\n\n"
                        "CHART 5 — Team Composition Bar: Show squad slots by position [GK:2,CB:4,LB:2,RB:2,CDM:2,CM:3,CAM:1,LW:1,RW:1,ST:2] "
                        "as current count (dark bar) + incoming (accent bar). Highlight the target position. Save as 'squad_composition.png'.\n\n"
                        "CHART 6 — Head-to-Head Table: Use matplotlib table or pandas styled table converted to image. "
                        "Columns = players, rows = [age,wage_eur,overall_rating,goals_per_season,assists_per_season,pass_accuracy,sprint_speed]. "
                        "Color best value in each row green, worst red. Save as 'head_to_head_table.png'.\n\n"
                        "Return JSON: {\"code\": \"<full Python script as a single string>\"}\n"
                        "Use OUTPUT_DIR and data variables (already available). Do not include import statements for json/os/matplotlib/numpy/pandas/seaborn — they are pre-imported."
                    ),
                }
            ],
            temperature=0.2,
        )

        viz_code: str = viz_code_result.get("code", "")

        # ── Step 2: Execute the visualization code in sandbox ──────────────
        await self.emit_progress("Executing visualization code in Python sandbox...")

        exec_result = await run_visualization_code(
            code=viz_code,
            player_data=viz_data,
            run_id=run_id,
        )

        if exec_result["success"]:
            all_charts = exec_result["charts"]
            await self.emit_progress(
                f"Generated {len(all_charts)} chart(s) successfully",
                {"charts": [c.split("/")[-1] for c in all_charts]},
            )
        else:
            await self.emit_progress(
                "Chart generation encountered issues — continuing with analysis",
                {"stderr": exec_result["stderr"][:500]},
            )

        # ── Step 3: Write per-player analysis reports ──────────────────────
        await self.emit_progress("Writing individual player analysis reports...")

        for player in players:
            name = player.get("name", "Unknown")
            await self.emit_progress(f"Analysing {name}...")

            report_result = await self.chat_json(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Write a detailed performance analysis report for this football player.\n"
                            f"Player data: {json.dumps(player, indent=2)}\n"
                            f"Position averages for {position}: {json.dumps(pos_avg, indent=2)}\n\n"
                            "Format the report in Markdown following the structure in your instructions. "
                            "Be specific — reference exact numbers. "
                            "Return JSON: {\"report\": \"<full markdown report as a string>\"}"
                        ),
                    }
                ]
            )
            player_reports[name] = report_result.get("report", f"## {name}\nAnalysis not available.")

        # ── Step 4: Unified consolidated report ───────────────────────────
        await self.emit_progress("Compiling consolidated analysis report...")

        unified_result = await self.chat_json(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Combine these individual player reports into one unified consolidated analysis document.\n"
                        f"Individual reports:\n{json.dumps(player_reports, indent=2)}\n\n"
                        "Include: an overview section comparing all players, then each player's report. "
                        "Highlight the most statistically exceptional player. "
                        "Return JSON: {\"unified_report\": \"<full markdown as a string>\"}"
                    ),
                }
            ]
        )
        unified_report = unified_result.get(
            "unified_report",
            "\n\n".join(player_reports.values()),
        )

        await self.emit_complete(
            f"Analysis complete — {len(all_charts)} charts, {len(player_reports)} player reports",
            {"chart_count": len(all_charts), "player_count": len(player_reports)},
        )

        return {
            "charts": all_charts,
            "player_reports": player_reports,
            "unified_report": unified_report,
        }
