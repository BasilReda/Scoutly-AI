import matplotlib; matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

player_data = [
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
    "scout_note": "Reliable La Liga goalkeeper with consistent clean sheets and solid defensive stats, offering excellent value under the salary cap."
  },
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
    "scout_note": "Experienced goalkeeper with strong defensive and physical attributes, consistently delivering clean sheets and good value within the wage limit."
  }
]

# Convert to DataFrame for easier manipulation
players_df = pd.DataFrame(player_data)

# 1. Radar chart per player (attacking, defending, speed, stamina, dribble, physicality)
attributes = ['attacking', 'defending', 'sprint_speed', 'stamina', 'dribble_success', 'physicality']

# Prepare data for radar
radar_data = players_df.set_index('name')[attributes]

# Radar chart function
from math import pi

def make_radar_chart(df, title, filename):
    categories = list(df.columns)
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    plt.figure(figsize=(6,6))
    ax = plt.subplot(111, polar=True)

    for i, (name, row) in enumerate(df.iterrows()):
        values = row.tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=name)
        ax.fill(angles, values, alpha=0.25)

    plt.xticks(angles[:-1], categories)
    ax.set_rlabel_position(30)
    plt.yticks([20,40,60,80,100], ['20','40','60','80','100'], color='grey', size=7)
    plt.ylim(0,100)
    plt.title(title)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

make_radar_chart(radar_data, 'Player Attribute Radar', r'E:\\vs codes\\test\\charts\\eb976526-ed98-4482-8766-4770d92cb946\\radar_chart.png')

# 2. Scatter: wage vs performance (overall_rating), annotate with names
plt.figure(figsize=(8,6))
sns.scatterplot(data=players_df, x='wage_eur', y='overall_rating', s=100)
for i, row in players_df.iterrows():
    plt.text(row['wage_eur']+500, row['overall_rating'], row['name'], fontsize=9)
plt.xlabel('Wage (EUR)')
plt.ylabel('Overall Rating')
plt.title('Wage vs Overall Performance')
plt.tight_layout()
plt.savefig(r'E:\\vs codes\\test\\charts\\eb976526-ed98-4482-8766-4770d92cb946\\scatter.png')
plt.close()

# 3. Pitch heatmap: plot player positions on a simple pitch diagram
# For simplicity, map GK to a fixed position, others would be spread
plt.figure(figsize=(10,6))
plt.plot([0,100,100,0,0], [0,0,50,50,0], color='green')  # pitch outline
plt.fill_between([0,100], 0, 50, color='lightgreen', alpha=0.3)

pos_map = {'GK': (10, 25)}
for i, row in players_df.iterrows():
    x, y = pos_map.get(row['position'], (50, 25))
    plt.scatter(x, y, s=300, label=row['name'])
    plt.text(x+2, y, row['name'], fontsize=10)
plt.title('Player Position Heatmap')
plt.xlim(0, 100)
plt.ylim(0, 50)
plt.axis('off')
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig(r'E:\\vs codes\\test\\charts\\eb976526-ed98-4482-8766-4770d92cb946\\pitch_heatmap.png')
plt.close()

# 4. Trends: goals & assists per season trend lines
plt.figure(figsize=(8,6))
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
plt.savefig(r'E:\\vs codes\\test\\charts\\eb976526-ed98-4482-8766-4770d92cb946\\trends.png')
plt.close()

# 5. Squad composition: bar chart of current players (2) and incoming (0) by position
positions = players_df['position'].value_counts()
incoming = pd.Series([0], index=['GK'])  # no incoming data
combined = pd.DataFrame({'Current': positions, 'Incoming': incoming}).fillna(0)
combined.plot(kind='bar', figsize=(8,6))
plt.title('Squad Composition: Current vs Incoming')
plt.xlabel('Position')
plt.ylabel('Number of Players')
plt.tight_layout()
plt.savefig(r'E:\\vs codes\\test\\charts\\eb976526-ed98-4482-8766-4770d92cb946\\squad_composition.png')
plt.close()

# 6. Head to head: table comparing all players side by side
cols = ['name', 'age', 'club', 'wage_eur', 'value_eur', 'overall_rating', 'potential', 'pass_accuracy', 'dribble_success', 'aerial_duels_won', 'sprint_speed', 'stamina', 'defending', 'attacking', 'physicality']
head_to_head_df = players_df[cols].set_index('name')

fig, ax = plt.subplots(figsize=(12,3))
ax.axis('off')
table = ax.table(cellText=head_to_head_df.values,
                 rowLabels=head_to_head_df.index,
                 colLabels=head_to_head_df.columns,
                 cellLoc='center',
                 loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Head to Head Player Comparison')
plt.tight_layout()
plt.savefig(r'E:\\vs codes\\test\\charts\\eb976526-ed98-4482-8766-4770d92cb946\\head_to_head.png')
plt.close()
