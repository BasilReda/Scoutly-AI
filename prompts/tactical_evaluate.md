# Tactical Agent — Player Evaluation Prompt

You must evaluate and rank {player_count} football player candidates for tactical fit.

=== TEAM TACTICAL DOCUMENT ===
{tactics_text}

=== STATISTICAL ANALYSIS REPORT ===
{analysis_report}

=== CANDIDATE PLAYERS ===
{players_json}

=== FINANCIAL CONTEXT ===
{financial_json}

Score each player on tactical fit (0–100) using the framework in your instructions.
Rank from best to worst.

For each player include:
- rank
- name
- tactical_fit_score
- formation_fit (0-25)
- style_compatibility (0-25)
- statistical_benchmark (0-25)
- squad_balance (0-25)
- strengths (list)
- weaknesses (list)
- tactical_verdict (str)
- reference_to_tactics (str)

Also include a tactical_summary covering all candidates.
Return JSON: {{"ranked_players": [...], "tactical_summary": "..."}}
