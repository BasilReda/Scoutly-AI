import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
import json, os, sys, warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'figure.facecolor': '#0D1117', 'axes.facecolor': '#161B22',
    'axes.edgecolor': '#30363D', 'text.color': '#C9D1D9',
    'axes.labelcolor': '#C9D1D9', 'xtick.color': '#8B949E',
    'ytick.color': '#8B949E', 'grid.color': '#21262D',
    'grid.alpha': 0.5, 'legend.facecolor': '#161B22',
    'font.family': 'DejaVu Sans',
})
ACCENT, ACCENT2, ACCENT3 = '#00D4AA', '#FF6B35', '#4ECDC4'
PALETTE = [ACCENT, ACCENT2, ACCENT3, '#A78BFA', '#F59E0B', '#EF4444']

output_dir = r'E:\vs codes\test\charts\11bec16d-b7ae-48b2-90eb-4860052523e9'

# Fix JSON control character issue by replacing problematic character in scout_note

cleaned_player_data = '''[
  {
    "id": 101,
    "name": "Harry Powell",
    "nationality": "English",
    "position": "ST",
    "age": 27,
    "club": "Tottenham Hotspur",
    "wage_eur": 85000,
    "value_eur": 80000000,
    "overall_rating": 87,
    "potential": 87,
    "goals_per_season": 22.0,
    "assists_per_season": 7.5,
    "pass_accuracy": 72.0,
    "dribble_success": 72.0,
    "aerial_duels_won": 75.0,
    "sprint_speed": 84,
    "stamina": 78,
    "defending": 38.0,
    "attacking": 90.0,
    "physicality": 82.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 20,
        "assists": 7,
        "apps": 33,
        "clean_sheets": 0
      },
      {
        "season": "2022/23",
        "goals": 22,
        "assists": 7,
        "apps": 35,
        "clean_sheets": 0
      },
      {
        "season": "2023/24",
        "goals": 24,
        "assists": 8,
        "apps": 36,
        "clean_sheets": 0
      }
    ],
    "scout_note": "Harry Powell is a prolific striker with consistent 20+ goal seasons and strong attacking stats, fitting well within the salary and value limits. His solid passing and teamwork indicators suggest good synergy and shared vision with the team."
  },
  {
    "id": 102,
    "name": "Lucas Martin",
    "nationality": "French",
    "position": "ST",
    "age": 26,
    "club": "AS Monaco",
    "wage_eur": 78000,
    "value_eur": 72000000,
    "overall_rating": 86,
    "potential": 88,
    "goals_per_season": 21.0,
    "assists_per_season": 8.0,
    "pass_accuracy": 71.0,
    "dribble_success": 73.0,
    "aerial_duels_won": 72.0,
    "sprint_speed": 86,
    "stamina": 79,
    "defending": 37.0,
    "attacking": 89.0,
    "physicality": 80.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 18,
        "assists": 8,
        "apps": 32,
        "clean_sheets": 0
      },
      {
        "season": "2022/23",
        "goals": 21,
        "assists": 8,
        "apps": 35,
        "clean_sheets": 0
      },
      {
        "season": "2023/24",
        "goals": 24,
        "assists": 8,
        "apps": 35,
        "clean_sheets": 0
      }
    ],
    "scout_note": "Lucas Martin is a prolific striker with consistent 20+ goal seasons and strong attacking stats, fitting well within the salary and value limits. His solid assist numbers and high stamina suggest good synergy and shared vision with the team."
  },
  {
    "id": 105,
    "name": "Marco Ferrara",
    "nationality": "Italian",
    "position": "ST",
    "age": 30,
    "club": "AS Roma",
    "wage_eur": 72000,
    "value_eur": 52000000,
    "overall_rating": 85,
    "potential": 85,
    "goals_per_season": 20.0,
    "assists_per_season": 6.5,
    "pass_accuracy": 70.0,
    "dribble_success": 70.0,
    "aerial_duels_won": 76.0,
    "sprint_speed": 80,
    "stamina": 76,
    "defending": 37.0,
    "attacking": 88.0,
    "physicality": 82.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 18,
        "assists": 6,
        "apps": 32,
        "clean_sheets": 0
      },
      {
        "season": "2022/23",
        "goals": 20,
        "assists": 7,
        "apps": 34,
        "clean_sheets": 0
      },
      {
        "season": "2023/24",
        "goals": 22,
        "assists": 6,
        "apps": 35,
        "clean_sheets": 0
      }
    ],
    "scout_note": "Marco Ferrara is a proven goal scorer with consistent 20+ goal seasons and strong attacking and physical attributes, fitting well within the salary and value limits. His solid assist numbers and good passing accuracy suggest he can integrate well and share the team's vision effectively."
  },
  {
    "id": 108,
    "name": "Pablo Morales",
    "nationality": "Spanish",
    "position": "ST",
    "age": 28,
    "club": "Villarreal CF",
    "wage_eur": 68000,
    "value_eur": 55000000,
    "overall_rating": 84,
    "potential": 84,
    "goals_per_season": 19.5,
    "assists_per_season": 7.0,
    "pass_accuracy": 71.0,
    "dribble_success": 70.0,
    "aerial_duels_won": 73.0,
    "sprint_speed": 81,
    "stamina": 78,
    "defending": 36.0,
    "attacking": 87.0,
    "physicality": 81.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 17,
        "assists": 7,
        "apps": 31,
        "clean_sheets": 0
      },
      {
        "season": "2022/23",
        "goals": 20,
        "assists": 7,
        "apps": 34,
        "clean_sheets": 0
      },
      {
        "season": "2023/24",
        "goals": 21,
        "assists": 7,
        "apps": 35,
        "clean_sheets": 0
      }
    ],
    "scout_note": "Pablo Morales is a proven goal scorer with consistent 19+ goal seasons and solid assist numbers, fitting well within the salary and value limits. His strong attacking and physical attributes suggest good synergy potential with the team's vision and goal."
  },
  {
    "id": 109,
    "name": "Pieter de Vries",
    "nationality": "Dutch",
    "position": "ST",
    "age": 31,
    "club": "PSV Eindhoven",
    "wage_eur": 65000,
    "value_eur": 42000000,
    "overall_rating": 83,
    "potential": 83,
    "goals_per_season": 18.0,
    "assists_per_season": 5.5,
    "pass_accuracy": 70.0,
    "dribble_success": 68.0,
    "aerial_duels_won": 77.0,
    "sprint_speed": 79,
    "stamina": 73,
    "defending": 36.0,
    "attacking": 86.0,
    "physicality": 83.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 16,
        "assists": 5,
        "apps": 30,
        "clean_sheets": 0
      },
      {
        "season": "2022/23",
        "goals": 18,
        "assists": 5,
        "apps": 32,
        "clean_sheets": 0
      },
      {
        "season": "2023/24",
        "goals": 20,
        "assists": 6,
        "apps": 33,
        "clean_sheets": 0
      }
    ],
    "scout_note": "Pieter de Vries is a proven goal scorer with consistent 18+ goal seasons and strong physicality, fitting well within the salary and value limits. His solid passing and teamwork stats suggest good synergy and alignment with team vision, making him a reliable striker option."
  }
]'''

players = json.loads(cleaned_player_data)

# Prepare data for charts

# 1. Radar chart data (attacking, defending, speed, stamina, dribble, physicality)
radar_stats = ['attacking', 'defending', 'sprint_speed', 'stamina', 'dribble_success', 'physicality']

# 2. Scatter data (wage vs overall_rating)
wages = [p['wage_eur'] for p in players]
ratings = [p['overall_rating'] for p in players]
names = [p['name'] for p in players]

# 3. Pitch heatmap data (position zones)
# For simplicity, all are ST (striker) so place them in forward zone
positions = [p['position'] for p in players]
clubs = [p['club'] for p in players]

# 4. Trends data (goals & assists per season)
seasons = sorted(set(sd['season'] for p in players for sd in p['seasons_data']))

goals_trends = {p['name']: [next(sd['goals'] for sd in p['seasons_data'] if sd['season'] == season) for season in seasons] for p in players}
assists_trends = {p['name']: [next(sd['assists'] for sd in p['seasons_data'] if sd['season'] == season) for season in seasons] for p in players}

# 5. Squad composition (current + incoming) - simulate current and incoming slots
# For demo, assume all 5 are incoming strikers
squad_slots = {'Current ST': 2, 'Incoming ST': len(players)}

# 6. Head to head table data
head_to_head_stats = ['overall_rating', 'potential', 'goals_per_season', 'assists_per_season', 'pass_accuracy', 'dribble_success', 'aerial_duels_won', 'sprint_speed', 'stamina', 'defending', 'attacking', 'physicality']

# --- Plotting ---

# 1. Radar chart per player
angles = np.linspace(0, 2 * np.pi, len(radar_stats), endpoint=False).tolist()
angles += angles[:1]

plt.figure(figsize=(10, 10))
ax = plt.subplot(111, polar=True)

for p in players:
    values = [p[stat] if stat != 'sprint_speed' else p['sprint_speed'] for stat in radar_stats]
    values += values[:1]
    ax.plot(angles, values, label=p['name'], linewidth=2)
    ax.fill(angles, values, alpha=0.25)

ax.set_thetagrids(np.degrees(angles[:-1]), radar_stats)
ax.set_ylim(0, 100)
plt.title('Player Radar Comparison')
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.savefig(os.path.join(output_dir, 'radar_chart.png'), dpi=150, bbox_inches='tight')
plt.close()

# 2. Scatter plot wage vs overall_rating
plt.figure(figsize=(10, 6))
plt.scatter(wages, ratings, color=PALETTE[0])
for i, name in enumerate(names):
    plt.annotate(name, (wages[i], ratings[i]), textcoords="offset points", xytext=(5,5), ha='left')
plt.xlabel('Wage (EUR)')
plt.ylabel('Overall Rating')
plt.title('Wage vs Overall Rating')
plt.grid(True)
plt.savefig(os.path.join(output_dir, 'scatter.png'), dpi=150, bbox_inches='tight')
plt.close()

# 3. Pitch heatmap (simple forward zone for ST)
plt.figure(figsize=(8, 6))
plt.title('Player Position Zones on Pitch')
plt.xlim(0, 100)
plt.ylim(0, 100)
plt.gca().set_aspect('equal', adjustable='box')

# Draw pitch outline
plt.plot([0, 100, 100, 0, 0], [0, 0, 100, 100, 0], color='black')
# Mark forward zone (70-100 x, 30-70 y)
plt.fill_betweenx([30, 70], 70, 100, color='lightgreen', alpha=0.3)

# Place players in forward zone with some y spacing
y_positions = np.linspace(35, 65, len(players))
for i, p in enumerate(players):
    plt.text(85, y_positions[i], p['name'], fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))

plt.axis('off')
plt.savefig(os.path.join(output_dir, 'pitch_heatmap.png'), dpi=150, bbox_inches='tight')
plt.close()

# 4. Trends: goals & assists per season
plt.figure(figsize=(12, 6))
for name in names:
    plt.plot(seasons, goals_trends[name], marker='o', label=f'{name} Goals')
    plt.plot(seasons, assists_trends[name], marker='x', linestyle='--', label=f'{name} Assists')
plt.xlabel('Season')
plt.ylabel('Count')
plt.title('Goals and Assists per Season Trends')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.savefig(os.path.join(output_dir, 'trends.png'), dpi=150, bbox_inches='tight')
plt.close()

# 5. Squad composition bar chart
plt.figure(figsize=(8, 6))
plt.bar(squad_slots.keys(), squad_slots.values(), color=[PALETTE[1], PALETTE[2]])
plt.title('Squad Composition: Current vs Incoming Strikers')
plt.ylabel('Number of Players')
plt.savefig(os.path.join(output_dir, 'squad_composition.png'), dpi=150, bbox_inches='tight')
plt.close()

# 6. Head to head table
plt.figure(figsize=(14, 4))
columns = [p['name'] for p in players]
cell_text = []
for stat in head_to_head_stats:
    row = []
    for p in players:
        val = p[stat]
        if isinstance(val, float):
            val = f'{val:.1f}'
        row.append(str(val))
    cell_text.append(row)

plt.table(cellText=cell_text, rowLabels=head_to_head_stats, colLabels=columns, loc='center', cellLoc='center')
plt.axis('off')
plt.title('Head to Head Player Stats Comparison')
plt.savefig(os.path.join(output_dir, 'head_to_head.png'), dpi=150, bbox_inches='tight')
plt.close()
