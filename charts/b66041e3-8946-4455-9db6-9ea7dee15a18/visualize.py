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

output_dir = r'/app/charts/b66041e3-8946-4455-9db6-9ea7dee15a18'

import os

# Player data
player_data = [
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
    "scout_note": "Pablo Morales is a proven striker consistently scoring over 15 goals per season, with a strong attacking rating and good physicality, making him a reliable goal threat for Villarreal CF."
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
    "scout_note": "Pieter de Vries is a proven striker consistently scoring 15+ goals per season, demonstrating strong attacking ability and physical presence. His experience and reliable goal output make him a valuable asset for any team seeking a clinical finisher."
  }
]

# Determine role group
positions = [p['position'] for p in player_data]
# All are ST, so role is striker
role = 'striker'

# Prepare output directory
output_dir = '/app/charts/b66041e3-8946-4455-9db6-9ea7dee15a18'

# Chart 1: Radar chart for all players
attributes = ['attacking', 'defending', 'sprint_speed', 'stamina', 'dribble_success', 'physicality']

plt.figure(figsize=(8, 8))
angles = np.linspace(0, 2 * np.pi, len(attributes), endpoint=False).tolist()
angles += angles[:1]

ax = plt.subplot(111, polar=True)

for player in player_data:
    values = [player[attr] for attr in attributes]
    values += values[:1]
    ax.plot(angles, values, label=player['name'], linewidth=2)
    ax.fill(angles, values, alpha=0.25)

ax.set_thetagrids(np.degrees(angles[:-1]), attributes)
plt.title('Player Attribute Radar Comparison', size=15, y=1.1)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.savefig(os.path.join(output_dir, 'radar_chart.png'), dpi=150, bbox_inches='tight')
plt.close()

# Role-specific charts for striker
# Chart 2: goals_trend.png - Line chart goals per season per player
plt.figure(figsize=(10, 6))
for player in player_data:
    seasons = [sd['season'] for sd in player['seasons_data']]
    goals = [sd['goals'] for sd in player['seasons_data']]
    plt.plot(seasons, goals, marker='o', label=player['name'])
    for i, g in enumerate(goals):
        plt.text(seasons[i], g, str(g), fontsize=9, ha='center', va='bottom')
plt.title('Goals per Season')
plt.xlabel('Season')
plt.ylabel('Goals')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(output_dir, 'goals_trend.png'), dpi=150, bbox_inches='tight')
plt.close()

# Chart 3: shot_conversion.png - Bar chart goals_per_season vs assists_per_season
width = 0.35
x = np.arange(len(player_data))
plt.figure(figsize=(8, 6))
goals = [p['goals_per_season'] for p in player_data]
assists = [p['assists_per_season'] for p in player_data]
plt.bar(x - width/2, goals, width, label='Goals per Season')
plt.bar(x + width/2, assists, width, label='Assists per Season')
plt.xticks(x, [p['name'] for p in player_data])
plt.ylabel('Count')
plt.title('Goals vs Assists per Season')
plt.legend()
plt.savefig(os.path.join(output_dir, 'shot_conversion.png'), dpi=150, bbox_inches='tight')
plt.close()

# Chart 4: attacking_physicality.png - Grouped bar chart attacking and physicality
width = 0.35
x = np.arange(len(player_data))
plt.figure(figsize=(8, 6))
attacking = [p['attacking'] for p in player_data]
physicality = [p['physicality'] for p in player_data]
plt.bar(x - width/2, attacking, width, label='Attacking')
plt.bar(x + width/2, physicality, width, label='Physicality')
plt.xticks(x, [p['name'] for p in player_data])
plt.ylabel('Rating')
plt.title('Attacking and Physicality Comparison')
plt.legend()
plt.savefig(os.path.join(output_dir, 'attacking_physicality.png'), dpi=150, bbox_inches='tight')
plt.close()

# Chart 5: head_to_head.png - Matplotlib table comparing all players on key stats
cols = ['name', 'age', 'club', 'wage_eur', 'value_eur', 'overall_rating', 'potential',
        'pass_accuracy', 'dribble_success', 'aerial_duels_won', 'sprint_speed',
        'stamina', 'defending', 'attacking', 'physicality']

cell_text = []
for p in player_data:
    row = [p[c] for c in cols]
    cell_text.append(row)

fig, ax = plt.subplots(figsize=(14, 2))
ax.axis('off')

# Create table
colors = ['#222222', '#333333']
row_colors = [colors[i % 2] for i in range(len(cell_text))]

# Create table with alternating row colors
table = ax.table(cellText=cell_text,
                 colLabels=cols,
                 cellLoc='center',
                 loc='center')

# Style table
for i, key in enumerate(cols):
    table.auto_set_column_width(i)

for i, color in enumerate(row_colors):
    for j in range(len(cols)):
        table[(i+1, j)].set_facecolor(color)
        table[(i+1, j)].get_text().set_color('white')

# Header style
for j in range(len(cols)):
    table[(0, j)].set_facecolor('#444444')
    table[(0, j)].get_text().set_color('white')
    table[(0, j)].get_text().set_fontweight('bold')

plt.savefig(os.path.join(output_dir, 'head_to_head.png'), dpi=150, bbox_inches='tight')
plt.close()
