"""
Tactical Agent — evaluates candidates against the team's tactical PDF and ranks them.
"""
import asyncio
import json
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from .base import BaseAgent
from ..utils.config import settings

# Try to import pymupdf for PDF reading
try:
    import fitz  # PyMuPDF
    _PDF_BACKEND = "pymupdf"
except ImportError:
    _PDF_BACKEND = None


def _extract_pdf_text(pdf_path: Path) -> str:
    """Extract text content from a PDF file."""
    if not pdf_path.exists():
        return (
            "Tactical document not found. Using default tactical profile:\n"
            "Formation: 4-3-3 (high press)\n"
            "Style: Possession-based with vertical transitions\n"
            "Striker role: Lead presser, clinical finisher, strong aerial ability\n"
            "Midfielder role: Box-to-box, high stamina, range of passing\n"
            "Wide players: Pace and dribbling, cut inside, chance creation\n"
            "Defenders: Comfortable in possession, strong aerially, high defensive line\n"
        )

    if _PDF_BACKEND == "pymupdf":
        doc = fitz.open(str(pdf_path))
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)

    # Fallback: read as plain text if PDF library not available
    try:
        return pdf_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return "Unable to read tactical document."


class TacticalAgent(BaseAgent):
    AGENT_NAME = "tactical"

    def __init__(self, client: AsyncOpenAI, sse_queue: asyncio.Queue):
        super().__init__(client, sse_queue)
        self._tactics_text: str | None = None

    def _get_tactics(self) -> str:
        """Load and cache the tactics PDF content."""
        if self._tactics_text is None:
            self._tactics_text = _extract_pdf_text(settings.TACTICS_PDF_PATH)
        return self._tactics_text

    async def run(
        self,
        players: list[dict],
        analysis_report: str,
        financial_decision: dict,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Evaluate and rank players for tactical fit.

        Args:
            players:           Shortlisted players from ScouterAgent.
            analysis_report:   Unified analysis report from AnalysisAgent.
            financial_decision: Output from FinancialAgent.

        Returns:
            {
                "ranked_players": [list of ranked player dicts with tactical scores],
                "tactical_summary": str,
            }
        """
        await self.emit_start("Loading team tactical document...")

        tactics_text = self._get_tactics()
        await self.emit_progress(
            "Tactical document loaded",
            {"preview": tactics_text[:200] + "..."},
        )

        await self.emit_progress(
            f"Evaluating {len(players)} candidates against team tactics and ranking..."
        )

        result = await self.chat_json(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You must evaluate and rank {len(players)} football player candidates for tactical fit.\n\n"
                        f"=== TEAM TACTICAL DOCUMENT ===\n{tactics_text}\n\n"
                        f"=== STATISTICAL ANALYSIS REPORT ===\n{analysis_report[:3000]}\n\n"
                        f"=== CANDIDATE PLAYERS ===\n{json.dumps(players, indent=2)}\n\n"
                        f"=== FINANCIAL CONTEXT ===\n{json.dumps(financial_decision, indent=2)}\n\n"
                        "Score each player on tactical fit (0–100) using the framework in your instructions. "
                        "Rank from best to worst. "
                        "For each player include: rank, name, tactical_fit_score, "
                        "formation_fit (0-25), style_compatibility (0-25), "
                        "statistical_benchmark (0-25), squad_balance (0-25), "
                        "strengths (list), weaknesses (list), tactical_verdict (str), "
                        "reference_to_tactics (str). "
                        "Also include a tactical_summary covering all candidates. "
                        'Return JSON: {"ranked_players": [...], "tactical_summary": "..."}'
                    ),
                }
            ]
        )

        ranked = result.get("ranked_players", [])
        summary = result.get("tactical_summary", "")

        # Merge tactical scores back into the original player dicts
        name_to_player = {p["name"]: p for p in players}
        for ranked_player in ranked:
            name = ranked_player.get("name", "")
            if name in name_to_player:
                name_to_player[name].update(
                    {
                        "rank": ranked_player.get("rank"),
                        "tactical_fit_score": ranked_player.get("tactical_fit_score"),
                        "tactical_verdict": ranked_player.get("tactical_verdict"),
                        "strengths": ranked_player.get("strengths", []),
                        "weaknesses": ranked_player.get("weaknesses", []),
                        "reference_to_tactics": ranked_player.get("reference_to_tactics", ""),
                        "formation_fit": ranked_player.get("formation_fit"),
                        "style_compatibility": ranked_player.get("style_compatibility"),
                        "statistical_benchmark": ranked_player.get("statistical_benchmark"),
                        "squad_balance": ranked_player.get("squad_balance"),
                    }
                )
                ranked_player.update(name_to_player[name])

        await self.emit_complete(
            f"Tactical ranking complete — #{1} pick: {ranked[0]['name'] if ranked else 'N/A'}",
            {
                "top_pick": ranked[0].get("name") if ranked else None,
                "scores": [
                    {"name": p.get("name"), "score": p.get("tactical_fit_score")}
                    for p in ranked
                ],
            },
        )

        return {"ranked_players": ranked, "tactical_summary": summary}
