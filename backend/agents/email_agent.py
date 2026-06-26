"""Email Agent — generates a formal recruitment email via deepagents and sends it via Gmail SMTP."""
import asyncio
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any

from openai import AsyncAzureOpenAI

from .base import BaseAgent

GMAIL_FROM = "basilreda112211@gmail.com"
GMAIL_TO = "basilreda12344321@gmail.com"


def _send_smtp_sync(to: str, subject: str, body: str, app_password: str) -> None:
    """Blocking SMTP send — run in executor to avoid blocking the event loop."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_FROM
    msg["To"] = to
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_FROM, app_password)
        server.sendmail(GMAIL_FROM, to, msg.as_string())


class EmailAgent(BaseAgent):
    AGENT_NAME = "email_agent"  # maps to prompts/email_agent.md

    async def run(
        self,
        player_name: str,
        player_data: dict,
        financial_decision: dict,
        run_id: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate a formal recruitment email draft via deepagents."""
        await self.emit_start(f"Drafting recruitment email for {player_name}...")

        # Build task context from player + financial data
        salary_max = financial_decision.get("salary_max", 0)
        salary_offer = f"€{salary_max:,}/week" if salary_max else "to be discussed"
        position = player_data.get("position", "the position")
        team_name = financial_decision.get("team_name", "FC Antigravity")
        age = player_data.get("age", "")
        club = player_data.get("club", "")

        task_message = (
            f"Draft a formal recruitment email for the following player:\n\n"
            f"Player Name: {player_name}\n"
            f"Position: {position}\n"
            f"Age: {age}\n"
            f"Current Club: {club}\n"
            f"Weekly Salary Offer (EXACT — do not change this number): {salary_offer}\n"
            f"Team Making Offer: {team_name}\n"
            f"From (sender email): {GMAIL_FROM}\n\n"
            f"IMPORTANT: The salary in the email MUST be exactly {salary_offer}. "
            "Do not substitute, round, or invent a different salary figure.\n\n"
            "First line must be: Subject: <subject>\nThen a blank line, then the email body."
        )

        # Use deepagents framework (via BaseAgent._run_deep_agent)
        raw = await self._run_deep_agent(task_message=task_message, tools=[])

        # Parse subject line and body
        lines = raw.strip().splitlines()
        subject = "Official Recruitment Interest"
        body_lines = lines
        if lines and lines[0].lower().startswith("subject:"):
            subject = lines[0][len("subject:"):].strip()
            body_lines = lines[2:] if len(lines) > 2 else []

        draft = "\n".join(body_lines).strip()

        await self.emit_complete(f"Email draft ready for {player_name}")
        return {
            "draft": draft,
            "subject": subject,
            "to": GMAIL_TO,
            "from": GMAIL_FROM,
            "player_name": player_name,
        }

    async def send(self, to: str, subject: str, body: str) -> bool:
        """Send the email via Gmail SMTP. Returns True on success."""
        app_password = os.getenv("GMAIL_APP_PASSWORD", "")
        if not app_password:
            await self.emit_error(
                "Email send failed",
                "GMAIL_APP_PASSWORD env var not set. Add it to .env to enable sending.",
            )
            return False

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _send_smtp_sync, to, subject, body, app_password)
            await self.emit({
                "type": "email_sent",
                "agent": "email",
                "message": f"Recruitment email sent to {to}",
                "data": {"to": to, "subject": subject},
                "timestamp": time.time(),
            })
            return True
        except Exception as exc:
            await self.emit_error("Email send failed", str(exc))
            return False
