"""
Generate a sample team tactics PDF for demo purposes.

Run this script once to create data/tactics.pdf:
    python data/generate_tactics_pdf.py
"""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT

DARK    = HexColor("#0D1117")
ACCENT  = HexColor("#00D4AA")
WHITE   = HexColor("#FFFFFF")
MUTED   = HexColor("#8B949E")
SURFACE = HexColor("#161B22")

OUTPUT_PATH = Path(__file__).parent / "tactics.pdf"

def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=WHITE,
        backColor=DARK,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "H2",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=ACCENT,
        spaceAfter=8,
        spaceBefore=16,
    )
    body_style = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=10,
        textColor=HexColor("#C9D1D9"),
        spaceAfter=6,
        leading=16,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        fontName="Helvetica",
        fontSize=10,
        textColor=HexColor("#C9D1D9"),
        leftIndent=20,
        spaceAfter=4,
        bulletText="•",
    )

    story = []

    story.append(Paragraph("FC Antigravity — Tactical System 2024/25", title_style))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("CONFIDENTIAL — FOR INTERNAL USE ONLY", ParagraphStyle(
        "sub", fontName="Helvetica", fontSize=9,
        textColor=MUTED, alignment=TA_CENTER
    )))
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph("1. Formation", h2_style))
    story.append(Paragraph(
        "Our primary formation is <b>4-3-3 (Attack)</b>. We operate with a high defensive line "
        "and compact midfield block. The three forwards press aggressively in the opposition half, "
        "with the striker leading the press from the front. The three central midfielders provide "
        "the engine room — one holding midfielder protects the back four while two box-to-box "
        "midfielders carry play forward.", body_style
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("2. Pressing System — High Press", h2_style))
    story.append(Paragraph("Our press is triggered by a designated signal from the holding midfielder. Key principles:", body_style))
    for pt in [
        "The striker must lead the press from the front — intercepting the goalkeeper's distribution and pressing centre-backs aggressively. Stamina ≥ 80 and sprint speed ≥ 78 are non-negotiable for this role.",
        "Wingers tuck inside to create a pressing trap on the flanks, preventing progression through wide areas.",
        "When the press is beaten, the team drops into a compact 4-5-1 mid-block at 60% of the pitch.",
        "Pressing triggers: goalkeeper in possession, opposition defender under pressure, or wayward back-pass.",
        "The team aims to win the ball within 6 seconds of losing it (GEGENPRESSING principle).",
    ]:
        story.append(Paragraph(pt, bullet_style))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("3. Build-Up Play — Possession Based", h2_style))
    story.append(Paragraph(
        "In possession, we build from the back through short, triangular combinations. "
        "The goalkeeper distributes to the centre-backs, who split wide. The holding midfielder "
        "drops between the centre-backs to form a back three in possession, freeing the "
        "full-backs to advance high up the pitch.", body_style
    ))
    for pt in [
        "Pass accuracy requirement: all outfield players should achieve ≥ 78% in our system.",
        "The centre-backs must be comfortable receiving under pressure and playing forward passes.",
        "When the build-up is blocked centrally, we switch to the opposite full-back who overlaps.",
        "Our target is > 55% possession in league games.",
    ]:
        story.append(Paragraph(pt, bullet_style))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("4. Attacking Patterns", h2_style))
    story.append(Paragraph("We use three primary attacking patterns:", body_style))
    story.append(Paragraph(
        "<b>Pattern A — Inside Run:</b> The left winger cuts inside onto their stronger foot while "
        "the left-back overlaps into the space. The striker makes a near-post run. "
        "The left winger must have dribble_success ≥ 75 to execute this reliably.", body_style
    ))
    story.append(Paragraph(
        "<b>Pattern B — Striker Hold-Up:</b> When we can't build from the back, the striker "
        "receives long balls and holds up play for the midfielders to join. Aerial duel win rate "
        "≥ 70% is required for this to be effective.", body_style
    ))
    story.append(Paragraph(
        "<b>Pattern C — Counter Attack:</b> On turnovers in the opponent's half, the fastest "
        "winger runs in behind immediately. Sprint speed ≥ 85 is needed for the wingers to "
        "exploit counter-attack opportunities effectively.", body_style
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("5. Set Pieces", h2_style))
    for pt in [
        "Corners: Delivery to the near post. Striker and one centre-back attack the near post. Second striker / CAM arrives late at the far post.",
        "Free kicks (wide): Low ball into the penalty area — striker makes a bending run across the near post.",
        "Defensive set pieces: Zonal marking — centre-backs take the central zone, CDM guards the edge.",
        "Players with aerial_duels_won ≥ 75 are prioritised for set-piece duty.",
    ]:
        story.append(Paragraph(pt, bullet_style))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("6. Key Player Requirements by Role", h2_style))

    table_data = [
        ["Role", "Min Stats Required", "Key Trait"],
        ["Striker (ST)", "Goals/ssn ≥ 15, Aerial ≥ 70, Pace ≥ 78", "Press leader + finisher"],
        ["Left Winger (LW)", "Dribble ≥ 75, Pace ≥ 85, Goals ≥ 10", "Cut inside + create"],
        ["Right Winger (RW)", "Dribble ≥ 75, Pace ≥ 85, Goals ≥ 10", "Wide outlet + cross"],
        ["CM (Box-to-Box)", "Stamina ≥ 82, Pass% ≥ 82, Goals ≥ 5", "Engine room"],
        ["CDM (Holder)", "Defending ≥ 80, Aerial ≥ 72, Pass% ≥ 85", "Shield backline"],
        ["Centre-Back (CB)", "Defending ≥ 83, Aerial ≥ 78, Pass% ≥ 78", "Ball-playing CB"],
        ["Full-Back (LB/RB)", "Pace ≥ 76, Assists ≥ 4/ssn, Defending ≥ 72", "Attacking FB"],
    ]

    table = Table(table_data, colWidths=[3.5*cm, 7*cm, 5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), DARK),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [SURFACE, DARK]),
        ("TEXTCOLOR", (0, 1), (-1, -1), HexColor("#C9D1D9")),
        ("GRID", (0, 0), (-1, -1), 0.3, HexColor("#30363D")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("7. Summary Philosophy", h2_style))
    story.append(Paragraph(
        "FC Antigravity plays an attractive, high-intensity brand of football built on "
        "pressing, possession, and vertical transitions. Every signing must contribute to "
        "this philosophy. Athletic players with technical quality are prioritised over "
        "technically gifted players who lack the physical capacity to press and counter-press "
        "at the required intensity. A player's tactical intelligence — knowing when to press, "
        "when to hold, when to run in behind — is weighted equally alongside raw statistics.",
        body_style
    ))

    doc.build(story)
    print(f"Tactics PDF generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
