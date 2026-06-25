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

output_dir = r'E:\vs codes\test\charts\92d429a1-8257-4e9c-b9e8-4f5192628af8'

# The previous error was a KeyboardInterrupt, likely unrelated to the script content itself.
# I will retry the script with a slight simplification and no re-imports.

# Load player data
players = json.loads('''[
  {
    "id": 67,
    "name": "Klaus Hoffmann",
    "nationality": "German",
    "position": "CB",
    "age": 28,
    "club": "FC Bayern Munich",
    "wage_eur": 85000,
    "value_eur": 62000000,
    "overall_rating": 89,
    "potential": 89,
    "goals_per_season": 2.8,
    "assists_per_season": 2.0,
    "pass_accuracy": 86.0,
    "dribble_success": 52.0,
    "aerial_duels_won": 85.0,
    "sprint_speed": 66,
    "stamina": 81,
    "defending": 91.0,
    "attacking": 56.0,
    "physicality": 87.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 2,
        "assists": 2,
        "apps": 32,
        "clean_sheets": 0
      },
      {
        "season": "2022/23",
        "goals": 3,
        "assists": 2,
        "apps": 34,
        "clean_sheets": 0
      },
      {
        "season": "2023/24",
        "goals": 3,
        "assists": 2,
        "apps": 35,
        "clean_sheets": 0
      }
    ],
    "scout_note": "Klaus Hoffmann is a top-tier central defender with excellent defending (91) and physicality (87), combined with strong aerial ability (85) and consistent contributions in goals and assists, making him a reliable and well-rounded defensive asset."
  },
  {
    "id": 81,
    "name": "David Torres",
    "nationality": "Spanish",
    "position": "CM",
    "age": 26,
    "club": "FC Barcelona",
    "wage_eur": 80000,
    "value_eur": 75000000,
    "overall_rating": 88,
    "potential": 91,
    "goals_per_season": 8.5,
    "assists_per_season": 9.2,
    "pass_accuracy": 91.0,
    "dribble_success": 75.0,
    "aerial_duels_won": 65.0,
    "sprint_speed": 78,
    "stamina": 88,
    "defending": 62.0,
    "attacking": 82.0,
    "physicality": 72.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 7,
        "assists": 9,
        "apps": 33,
        "clean_sheets": 0
      },
      {
        "season": "2022/23",
        "goals": 9,
        "assists": 9,
        "apps": 35,
        "clean_sheets": 0
      },
      {
        "season": "2023/24",
        "goals": 9,
        "assists": 10,
        "apps": 36,
        "clean_sheets": 0
      }
    ],
    "scout_note": "David Torres is a highly skilled central midfielder with excellent passing accuracy and consistent goal and assist contributions, making him a valuable playmaker with strong stamina and physicality to influence both attack and defense."
  },
  {
    "id": 98,
    "name": "Alejandro D\u00edaz",
    "nationality": "Spanish",
    "position": "RW",
    "age": 25,
    "club": "Real Madrid CF",
    "wage_eur": 95000,
    "value_eur": 90000000,
    "overall_rating": 88,
    "potential": 90,
    "goals_per_season": 16.0,
    "assists_per_season": 11.5,
    "pass_accuracy": 80.0,
    "dribble_success": 88.0,
    "aerial_duels_won": 50.0,
    "sprint_speed": 91,
    "stamina": 83,
    "defending": 35.0,
    "attacking": 91.0,
    "physicality": 63.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 13,
        "assists": 11,
        "apps": 32,
        "clean_sheets": 0
      },
      {
        "season": "2022/23",
        "goals": 16,
        "assists": 11,
        "apps": 35,
        "clean_sheets": 0
      },
      {
        "season": "2023/24",
        "goals": 19,
        "assists": 12,
        "apps": 36,
        "clean_sheets": 0
      }
    ],
    "scout_note": "Alejandro D\u00edaz is a dynamic right winger with excellent dribbling and sprint speed, consistently delivering double-digit goals and assists per season, making him a top attacking threat for Real Madrid."
  },
  {
    "id": 66,
    "name": "Carlos Vidal",
    "nationality": "Spanish",
    "position": "CB",
    "age": 31,
    "club": "Atl\u00e9tico Madrid",
    "wage_eur": 60000,
    "value_eur": 32000000,
    "overall_rating": 87,
    "potential": 87,
    "goals_per_season": 3.0,
    "assists_per_season": 1.2,
    "pass_accuracy": 84.0,
    "dribble_success": 46.0,
    "aerial_duels_won": 84.0,
    "sprint_speed": 60,
    "stamina": 75,
    "defending": 90.0,
    "attacking": 52.0,
    "physicality": 86.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 3,
        "assists": 1,
        "apps": 33,
        "clean_sheets": 0
      },
      {
        "season": "2022/23",
        "goals": 2,
        "assists": 2,
        "apps": 30,
        "clean_sheets": 0
      },
      {
        "season": "2023/24",
        "goals": 4,
        "assists": 1,
        "apps": 32,
        "clean_sheets": 0
      }
    ],
    "scout_note": "Carlos Vidal is a highly rated, experienced center-back with excellent defending and physicality stats, complemented by strong aerial ability and good passing accuracy, making him a reliable defensive presence for Atl\u00e9tico Madrid."
  },
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
    "scout_note": "Harry Powell is a prolific striker with consistent 20+ goal seasons and strong attacking attributes, making him a reliable goal scorer and valuable asset for any team seeking a clinical finisher."
  }
]''')

# Radar chart data
radar_categories = ['Attacking', 'Defending', 'Speed', 'Stamina', 'Dribble', 'Physicality']
radar_data = []
for p in players:
    radar_data.append({
        'name': p['name'],
        'values': [p['attacking'], p['defending'], p['sprint_speed'], p['stamina'], p['dribble_success'], p['physicality']]
    })

# Scatter data
wages = [p['wage_eur'] for p in players]
overalls = [p['overall_rating'] for p in players]
names = [p['name'] for p in players]

# Pitch heatmap
position_map = {'CB': (40, 50), 'CM': (60, 50), 'RW': (80, 70), 'ST': (90, 50)}
pitch_positions = [(position_map[p['position']][0], position_map[p['position']][1], p['name']) for p in players]

# Trends
seasons = sorted(set(sd['season'] for p in players for sd in p['seasons_data']))
goals_trends = {p['name']: [] for p in players}
assists_trends = {p['name']: [] for p in players}
for p in players:
    season_dict = {sd['season']: sd for sd in p['seasons_data']}
    for season in seasons:
        if season in season_dict:
            goals_trends[p['name']].append(season_dict[season]['goals'])
            assists_trends[p['name']].append(season_dict[season]['assists'])
        else:
            goals_trends[p['name']].append(0)
            assists_trends[p['name']].append(0)

# Squad composition
from collections import Counter
positions = [p['position'] for p in players]
position_counts = Counter(positions)

# Head to head table
head_to_head_cols = ['Name', 'Age', 'Position', 'Overall', 'Potential', 'Goals/Season', 'Assists/Season', 'Wage (k EUR)']
head_to_head_data = []
for p in players:
    head_to_head_data.append([
        p['name'], p['age'], p['position'], p['overall_rating'], p['potential'],
        round(p['goals_per_season'],1), round(p['assists_per_season'],1), round(p['wage_eur']/1000,1)
    ])

# Plot 1: Radar chart
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
angles = np.linspace(0, 2 * np.pi, len(radar_categories), endpoint=False).tolist()
angles += angles[:1]
for player in radar_data:
    values = player['values']
    values += values[:1]
    ax.plot(angles, values, label=player['name'], linewidth=2)
    ax.fill(angles, values, alpha=0.25)
ax.set_thetagrids(np.degrees(angles[:-1]), radar_categories)
ax.set_ylim(0, 100)
ax.set_title('Player Radar Comparison', fontsize=16)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.savefig(os.path.join(output_dir, 'radar_chart.png'), dpi=150, bbox_inches='tight')
plt.close()

# Plot 2: Scatter wage vs overall
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(wages, overalls, c='blue', alpha=0.7)
for i, name in enumerate(names):
    ax.annotate(name, (wages[i], overalls[i]), textcoords="offset points", xytext=(5,5), ha='left')
ax.set_xlabel('Wage (EUR)')
ax.set_ylabel('Overall Rating')
ax.set_title('Wage vs Overall Performance')
plt.savefig(os.path.join(output_dir, 'scatter.png'), dpi=150, bbox_inches='tight')
plt.close()

# Plot 3: Pitch heatmap
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot([0, 100, 100, 0, 0], [0, 0, 100, 100, 0], color='black')
ax.plot([50, 50], [0, 100], color='black')
ax.plot([0, 18, 18, 0], [30, 30, 70, 70], color='black')
ax.plot([100, 82, 82, 100], [30, 30, 70, 70], color='black')
for x, y, name in pitch_positions:
    ax.scatter(x, y, s=200, alpha=0.7)
    ax.text(x, y+3, name, ha='center', fontsize=9)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Player Positions on Pitch')
plt.savefig(os.path.join(output_dir, 'pitch_heatmap.png'), dpi=150, bbox_inches='tight')
plt.close()

# Plot 4: Trends goals & assists
fig, ax = plt.subplots(figsize=(10, 6))
for name in goals_trends:
    ax.plot(seasons, goals_trends[name], marker='o', label=f'{name} Goals')
    ax.plot(seasons, assists_trends[name], marker='x', linestyle='--', label=f'{name} Assists')
ax.set_xlabel('Season')
ax.set_ylabel('Count')
ax.set_title('Goals and Assists per Season Trends')
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.savefig(os.path.join(output_dir, 'trends.png'), dpi=150, bbox_inches='tight')
plt.close()

# Plot 5: Squad composition bar chart
fig, ax = plt.subplots(figsize=(8, 6))
positions_unique = list(position_counts.keys())
counts = list(position_counts.values())
ax.bar(positions_unique, counts, color=PALETTE[:len(positions_unique)])
ax.set_xlabel('Position')
ax.set_ylabel('Number of Players')
ax.set_title('Squad Composition by Position')
plt.savefig(os.path.join(output_dir, 'squad_composition.png'), dpi=150, bbox_inches='tight')
plt.close()

# Plot 6: Head to head table
fig, ax = plt.subplots(figsize=(12, 3))
ax.axis('off')
table = ax.table(cellText=head_to_head_data, colLabels=head_to_head_cols, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)
plt.title('Head to Head Player Comparison', fontsize=14)
plt.savefig(os.path.join(output_dir, 'head_to_head.png'), dpi=150, bbox_inches='tight')
plt.close()
