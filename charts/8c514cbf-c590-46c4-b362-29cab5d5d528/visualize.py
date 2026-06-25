import matplotlib; matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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
    ]
  }
]

output_dir = r"E:\vs codes\test\charts\8c514cbf-c590-46c4-b362-29cab5d5d528"

# Convert player_data to DataFrame for easier plotting
players_df = pd.DataFrame(player_data)

# 1. Radar chart for Pablo Morales
# Attributes: attacking, defending, sprint_speed, stamina, dribble_success, physicality
radar_attrs = ['attacking', 'defending', 'sprint_speed', 'stamina', 'dribble_success', 'physicality']

# Normalize attributes for radar chart (0-100 scale)
values = [players_df.loc[0, attr] for attr in radar_attrs]

# Radar chart setup
labels = radar_attrs
num_vars = len(labels)

angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
values += values[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, values, color='red', alpha=0.25)
ax.plot(angles, values, color='red', linewidth=2)
ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)
ax.set_title(f"Radar Chart - {players_df.loc[0, 'name']}")
plt.tight_layout()
plt.savefig(f"{output_dir}/radar_chart.png")
plt.close()

# 2. Scatter plot: wage vs overall_rating
plt.figure(figsize=(8, 6))
plt.scatter(players_df['wage_eur'], players_df['overall_rating'], color='blue')
for i, row in players_df.iterrows():
    plt.text(row['wage_eur'], row['overall_rating'], row['name'], fontsize=9, ha='right')
plt.xlabel('Wage (EUR)')
plt.ylabel('Overall Rating')
plt.title('Wage vs Overall Rating')
plt.tight_layout()
plt.savefig(f"{output_dir}/scatter.png")
plt.close()

# 3. Pitch heatmap: Show player position zone
# Simplified pitch zones for ST: forward center
pitch_length = 105
pitch_width = 68

fig, ax = plt.subplots(figsize=(10, 7))
# Draw pitch outline
plt.plot([0, 0, pitch_length, pitch_length, 0], [0, pitch_width, pitch_width, 0, 0], color='black')
# Mark position for ST roughly at forward center
pos_x = pitch_length * 0.85
pos_y = pitch_width / 2
ax.scatter(pos_x, pos_y, s=300, color='red')
ax.text(pos_x, pos_y + 3, players_df.loc[0, 'name'], ha='center', fontsize=12)
ax.set_xlim(0, pitch_length)
ax.set_ylim(0, pitch_width)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('Pitch Position Heatmap')
plt.tight_layout()
plt.savefig(f"{output_dir}/pitch_heatmap.png")
plt.close()

# 4. Trends: goals & assists per season
seasons = [sd['season'] for sd in player_data[0]['seasons_data']]
goals = [sd['goals'] for sd in player_data[0]['seasons_data']]
assists = [sd['assists'] for sd in player_data[0]['seasons_data']]

plt.figure(figsize=(8, 6))
plt.plot(seasons, goals, marker='o', label='Goals')
plt.plot(seasons, assists, marker='o', label='Assists')
plt.xlabel('Season')
plt.ylabel('Count')
plt.title('Goals and Assists per Season')
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/trends.png")
plt.close()

# 5. Squad composition: current + incoming
# Since only one player, show current position count
positions = players_df['position'].value_counts()
plt.figure(figsize=(6, 4))
positions.plot(kind='bar', color='green')
plt.title('Squad Composition by Position')
plt.xlabel('Position')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig(f"{output_dir}/squad_composition.png")
plt.close()

# 6. Head to head: table comparing all players side by side
# Only one player, so table with stats
stats = ['name', 'age', 'position', 'club', 'wage_eur', 'value_eur', 'overall_rating', 'potential', 'goals_per_season', 'assists_per_season']

fig, ax = plt.subplots(figsize=(10, 2))
ax.axis('off')
cell_text = [[players_df.loc[0, stat] for stat in stats]]
col_labels = stats
ax.table(cellText=cell_text, colLabels=col_labels, loc='center')
plt.title('Head to Head Player Stats')
plt.tight_layout()
plt.savefig(f"{output_dir}/head_to_head.png")
plt.close()
