"""
PDF Generator — assembles the final scouting report using WeasyPrint.

Flow:
  1. Call GPT-4o (using pdf_report.md prompt) to generate narrative sections
  2. Encode all chart images as base64
  3. Render the Jinja2 HTML template with all data
  4. Convert HTML → PDF using WeasyPrint
  5. Save to reports/<run_id>.pdf
"""
import asyncio
import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from openai import AsyncAzureOpenAI
from weasyprint import HTML as WeasyHTML

from ..utils.config import settings
from ..utils.prompt_loader import PromptLoader


def _encode_chart(path: str) -> str:
    """Base64-encode a chart image for embedding in HTML."""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""


def _chart_name(path: str) -> str:
    return Path(path).stem.replace("_", " ").title()


class PDFGenerator:
    """Generates the final WeasyPrint PDF scouting report."""

    def __init__(self, sse_queue: asyncio.Queue):
        self.queue = sse_queue
        self._client: AsyncAzureOpenAI | None = None

    async def emit(self, event: dict) -> None:
        event.setdefault("agent", "pdf_generator")
        await self.queue.put(event)

    def _get_client(self) -> AsyncAzureOpenAI:
        if self._client is None:
            self._client = AsyncAzureOpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            )
        return self._client

    async def _generate_narratives(
        self,
        query: str,
        ranked_players: list[dict],
        financial_decision: dict,
        tactical_summary: str,
        unified_analysis: str,
    ) -> dict[str, Any]:
        """Use GPT-4o with pdf_report.md prompt to write all narrative sections."""
        system_prompt = PromptLoader.get("pdf_report", use_cache=False)
        client = self._get_client()

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Scouting mission: {query}\n\n"
                        f"Ranked candidates: {json.dumps(ranked_players, indent=2)[:4000]}\n\n"
                        f"Financial decision: {json.dumps(financial_decision, indent=2)}\n\n"
                        f"Tactical summary: {tactical_summary}\n\n"
                        f"Analysis highlights: {unified_analysis[:2000]}\n\n"
                        "Generate all narrative sections for the PDF report. "
                        "Return JSON with keys: executive_summary, player_narratives (dict name→text), "
                        "financial_section, tactical_appendix, conclusion."
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        return json.loads(response.choices[0].message.content)

    async def generate(
        self,
        run_id: str,
        query: str,
        ranked_players: list[dict] | None = None,
        financial_decision: dict | None = None,
        tactical_summary: str = "",
        charts: list[str] | None = None,
        unified_analysis: str = "",
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generate the full PDF scouting report.

        Returns:
            {"pdf_path": str, "page_count": int}
        """
        await self.emit({"type": "agent_start", "message": "Generating PDF scouting report..."})

        ranked_players = ranked_players or []
        financial_decision = financial_decision or {}
        charts = charts or []

        # ── Step 1: Generate narrative sections ───────────────────────────
        await self.emit({"type": "progress", "message": "Writing report narratives..."})
        try:
            narratives = await self._generate_narratives(
                query=query,
                ranked_players=ranked_players,
                financial_decision=financial_decision,
                tactical_summary=tactical_summary,
                unified_analysis=unified_analysis,
            )
        except Exception as exc:
            narratives = {
                "executive_summary": f"Report generated for: {query}",
                "player_narratives": {},
                "financial_section": str(financial_decision),
                "tactical_appendix": tactical_summary,
                "conclusion": "See ranked players list for recommendations.",
            }

        # ── Step 2: Encode charts as base64 ──────────────────────────────
        await self.emit({"type": "progress", "message": f"Embedding {len(charts)} charts..."})
        encoded_charts = [
            {
                "name": _chart_name(c),
                "filename": Path(c).name,
                "b64": _encode_chart(c),
            }
            for c in charts
        ]

        # ── Step 3: Render HTML template ──────────────────────────────────
        await self.emit({"type": "progress", "message": "Rendering HTML report template..."})

        jinja_env = Environment(
            loader=FileSystemLoader(str(settings.TEMPLATES_DIR)),
            autoescape=select_autoescape(["html"]),
        )
        # zfill is a Python str method, not a built-in Jinja2 filter
        jinja_env.filters["zfill"] = lambda value, width: str(value).zfill(width)
        template = jinja_env.get_template("report.html")

        html_content = template.render(
            query=query,
            run_id=run_id,
            generated_at=datetime.now().strftime("%d %B %Y, %H:%M"),
            team_name=financial_decision.get("team_name", "البط الكيني"),
            ranked_players=ranked_players,
            financial_decision=financial_decision,
            tactical_summary=tactical_summary,
            charts=encoded_charts,
            narratives=narratives,
            player_count=len(ranked_players),
        )

        # ── Step 4: WeasyPrint → PDF ──────────────────────────────────────
        await self.emit({"type": "progress", "message": "Converting HTML to PDF via WeasyPrint..."})

        pdf_path = settings.REPORTS_DIR / f"{run_id}.pdf"
        WeasyHTML(string=html_content, base_url=str(settings.TEMPLATES_DIR)).write_pdf(str(pdf_path))

        await self.emit({
            "type": "agent_complete",
            "message": f"PDF report saved: {pdf_path.name}",
            "data": {"pdf_path": str(pdf_path), "filename": pdf_path.name},
        })

        return {"pdf_path": str(pdf_path), "filename": pdf_path.name}
