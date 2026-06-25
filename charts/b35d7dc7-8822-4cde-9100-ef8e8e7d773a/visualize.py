import matplotlib; matplotlib.use('Agg')
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Corrected player data with proper unicode characters
player_data = [
  {
    "id": 56,
    "name": "Marco Lindelöf",
    "nationality": "German",
    "position": "GK",
    "age": 29,
    "club": "Bayer Leverkusen",
    "wage_eur": 35000,
    "value_eur": 22000000,
    "overall_rating": 85,
    "potential": 86,
    "goals_per_season": 0.2,
    "assists_per_season": 0.1,
    "pass_accuracy": 78.0,
    "dribble_success": 35.0,
    "aerial_duels_won": 72.0,
    "sprint_speed": 52,
    "stamina": 72,
    "defending": 78.0,
    "attacking": 20.0,
    "physicality": 76.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 0,
        "assists": 0,
        "apps": 32,
        "clean_sheets": 14
      },
      {
        "season": "2022/23",
        "goals": 0,
        "assists": 1,
        "apps": 35,
        "clean_sheets": 17
      },
      {
        "season": "2023/24",
        "goals": 0,
        "assists": 0,
        "apps": 34,
        "clean_sheets": 15
      }
    ],
    "scout_note": "Experienced German goalkeeper with a strong record of clean sheets and solid defensive stats, fitting well within the salary and value constraints."
  },
  {
    "id": 60,
    "name": "Sebastián Molina",
    "nationality": "Spanish",
    "position": "GK",
    "age": 28,
    "club": "Valencia CF",
    "wage_eur": 30000,
    "value_eur": 18000000,
    "overall_rating": 83,
    "potential": 83,
    "goals_per_season": 0.0,
    "assists_per_season": 0.0,
    "pass_accuracy": 76.0,
    "dribble_success": 33.0,
    "aerial_duels_won": 70.0,
    "sprint_speed": 51,
    "stamina": 71,
    "defending": 77.0,
    "attacking": 19.0,
    "physicality": 74.0,
    "seasons_data": [
      {
        "season": "2021/22",
        "goals": 0,
        "assists": 0,
        "apps": 33,
        "clean_sheets": 13
      },
      {
        "season": "2022/23",
        "goals": 0,
        "assists": 0,
        "apps": 35,
        "clean_sheets": 15
      },
      {
        "season": "2023/24",
        "goals": 0,
        "assists": 1,
        "apps": 36,
        "clean_sheets": 16
      }
    ],
    "scout_note": "Reliable Spanish goalkeeper with consistent clean sheets and solid defensive metrics, offering excellent value under the salary cap."
  }
]

output_dir = r"E:\vs codes\test\charts\b35d7dc7-8822-4cde-9100-ef8e8e7d773a"

# Convert to DataFrame for easier manipulation
players_df = pd.DataFrame(player_data)

# 1. Radar chart per player (attacking, defending, speed, stamina, dribble, physicality)

# Radar chart setup
categories = ['attacking', 'defending', 'sprint_speed', 'stamina', 'dribble_success', 'physicality']
N = len(categories)

angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # close the loop

plt.figure(figsize=(8, 8))
ax = plt.subplot(111, polar=True)

for idx, player in players_df.iterrows():
    values = [player[cat] if cat != 'dribble_success' else player['dribble_success'] for cat in categories]
    values[2] = player['sprint_speed']  # sprint_speed
    values += values[:1]
    ax.plot(angles, values, label=player['name'], linewidth=2)
    ax.fill(angles, values, alpha=0.25)

ax.set_thetagrids(np.degrees(angles[:-1]), categories)
ax.set_ylim(0, 100)
plt.title('Player Radar Comparison')
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'radar_chart.png'))
plt.close()

# 2. Scatter plot wage vs overall_rating
plt.figure(figsize=(8, 6))
sns.scatterplot(data=players_df, x='wage_eur', y='overall_rating', s=100)
for idx, player in players_df.iterrows():
    plt.text(player['wage_eur']+500, player['overall_rating'], player['name'])
plt.xlabel('Wage (EUR)')
plt.ylabel('Overall Rating')
plt.title('Wage vs Performance')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'scatter.png'))
plt.close()

# 3. Pitch heatmap with position zones
# For simplicity, map GK to a fixed zone
plt.figure(figsize=(10, 6))
plt.plot([0, 0, 100, 100, 0], [0, 50, 50, 0, 0], color='green')  # pitch outline

for idx, player in players_df.iterrows():
    if player['position'] == 'GK':
        x, y = 5, 25
    else:
        x, y = 50, 25
    plt.scatter(x, y, s=200, label=player['name'])
    plt.text(x+2, y, player['name'])

plt.xlim(0, 100)
plt.ylim(0, 50)
plt.title('Pitch Position Heatmap')
plt.axis('off')
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'pitch_heatmap.png'))
plt.close()

# 4. Trends: goals & assists per season
plt.figure(figsize=(10, 6))
for player in player_data:
    seasons = [sd['season'] for sd in player['seasons_data']]
    goals = [sd['goals'] for sd in player['seasons_data']]
    assists = [sd['assists'] for sd in player['seasons_data']]
    plt.plot(seasons, goals, marker='o', label=f"{player['name']} Goals")
    plt.plot(seasons, assists, marker='x', linestyle='--', label=f"{player['name']} Assists")
plt.xlabel('Season')
plt.ylabel('Count')
plt.title('Goals and Assists per Season')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'trends.png'))
plt.close()

# 5. Squad composition bar chart (current + incoming)
# Here we only have current players, so show count by position
position_counts = players_df['position'].value_counts()
plt.figure(figsize=(8, 6))
sns.barplot(x=position_counts.index, y=position_counts.values)
plt.title('Squad Composition by Position')
plt.xlabel('Position')
plt.ylabel('Number of Players')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'squad_composition.png'))
plt.close()

# 6. Head to head comparison table
fig, ax = plt.subplots(figsize=(10, 3))
ax.axis('off')
cols = ['Name', 'Age', 'Club', 'Wage (EUR)', 'Value (EUR)', 'Overall', 'Potential', 'Pass Accuracy', 'Dribble Success', 'Aerial Duels', 'Sprint Speed', 'Stamina', 'Defending', 'Attacking', 'Physicality']
data = []
for player in player_data:
    data.append([
        player['name'], player['age'], player['club'], player['wage_eur'], player['value_eur'], player['overall_rating'], player['potential'],
        player['pass_accuracy'], player['dribble_success'], player['aerial_duels_won'], player['sprint_speed'], player['stamina'],
        player['defending'], player['attacking'], player['physicality']
    ])

table = ax.table(cellText=data, colLabels=cols, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)
plt.title('Head to Head Player Comparison')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'head_to_head.png'))
plt.close()
