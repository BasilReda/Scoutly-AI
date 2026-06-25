import matplotlib; matplotlib.use('Agg')
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from math import pi

# Load player data
player_data = [
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
    "scout_note": "Top striker with consistent 20+ goal seasons and strong attacking stats, fitting well within the salary and value limits."
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
    "scout_note": "Highly rated French striker with excellent goal and assist numbers, offering great potential and value under the salary cap."
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
    "scout_note": "Experienced Italian striker with solid goal-scoring record and physical presence, well within budget and value constraints."
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
    "scout_note": "Reliable Spanish striker with consistent scoring and assisting, offering balanced attacking skills and good value."
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
    "scout_note": "Veteran Dutch striker with strong physicality and aerial ability, consistent goal scorer within budget and value limits."
  }
]

# Convert to DataFrame for easier manipulation
players_df = pd.DataFrame(player_data)

# 1. Radar chart data preparation
radar_stats = ['attacking', 'defending', 'sprint_speed', 'stamina', 'dribble_success', 'physicality']

# Prepare radar data
radar_data = players_df[['name'] + radar_stats].copy()

# Radar chart function

def make_radar_chart(df, stats, output_path):
    categories = stats
    N = len(categories)
    
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    for i, row in df.iterrows():
        values = row[stats].tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=row['name'])
        ax.fill(angles, values, alpha=0.1)

    plt.xticks(angles[:-1], categories)
    ax.set_rlabel_position(30)
    plt.yticks([20,40,60,80,100], ['20','40','60','80','100'], color='grey', size=7)
    plt.ylim(0,100)
    plt.title('Player Radar Chart Comparison', size=15, y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

make_radar_chart(radar_data, radar_stats, r'E:\\vs codes\\test\\charts\\05a2e12a-94fa-456a-8bfd-502a69db6d52\\radar_chart.png')

# 2. Scatter plot: wage vs overall_rating
plt.figure(figsize=(10, 6))
sns.scatterplot(data=players_df, x='wage_eur', y='overall_rating', s=100)
for i, row in players_df.iterrows():
    plt.text(row['wage_eur']+1000, row['overall_rating'], row['name'], fontsize=9)
plt.title('Wage vs Overall Rating')
plt.xlabel('Wage (EUR)')
plt.ylabel('Overall Rating')
plt.tight_layout()
plt.savefig(r'E:\\vs codes\\test\\charts\\05a2e12a-94fa-456a-8bfd-502a69db6d52\\scatter.png')
plt.close()

# 3. Pitch heatmap: position zones
# Simplified pitch zones for ST: center forward zone
pitch_length = 105
pitch_width = 68

plt.figure(figsize=(12, 7))
plt.plot([0, pitch_length, pitch_length, 0, 0], [0, 0, pitch_width, pitch_width, 0], color='green')
plt.fill_betweenx([pitch_width*0.3, pitch_width*0.7], pitch_length*0.7, pitch_length, color='lightblue', alpha=0.3)

for i, row in players_df.iterrows():
    # Place each player in the center forward zone with some vertical offset
    x = pitch_length * 0.85
    y = pitch_width * (0.3 + 0.08 * i)
    plt.text(x, y, row['name'], fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7))

plt.title('Player Position Zones on Pitch (ST Focus)')
plt.axis('off')
plt.tight_layout()
plt.savefig(r'E:\\vs codes\\test\\charts\\05a2e12a-94fa-456a-8bfd-502a69db6d52\\pitch_heatmap.png')
plt.close()

# 4. Trends: goals & assists per season
plt.figure(figsize=(10, 6))
for player in player_data:
    seasons = [sd['season'] for sd in player['seasons_data']]
    goals = [sd['goals'] for sd in player['seasons_data']]
    assists = [sd['assists'] for sd in player['seasons_data']]
    plt.plot(seasons, goals, marker='o', label=f"{player['name']} Goals")
    plt.plot(seasons, assists, marker='x', linestyle='--', label=f"{player['name']} Assists")
plt.title('Goals and Assists per Season')
plt.xlabel('Season')
plt.ylabel('Count')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(r'E:\\vs codes\\test\\charts\\05a2e12a-94fa-456a-8bfd-502a69db6d52\\trends.png')
plt.close()

# 5. Squad composition: bar chart of players by age group
age_bins = [25, 27, 29, 31, 33]
age_labels = ['25-26', '27-28', '29-30', '31-32']
players_df['age_group'] = pd.cut(players_df['age'], bins=age_bins, labels=age_labels, right=False)

age_counts = players_df['age_group'].value_counts().sort_index()

plt.figure(figsize=(8, 6))
sns.barplot(x=age_counts.index, y=age_counts.values, palette='viridis')
plt.title('Squad Composition by Age Group')
plt.xlabel('Age Group')
plt.ylabel('Number of Players')
plt.tight_layout()
plt.savefig(r'E:\\vs codes\\test\\charts\\05a2e12a-94fa-456a-8bfd-502a69db6d52\\squad_composition.png')
plt.close()

# 6. Head to head: table of key stats
key_stats = ['overall_rating', 'potential', 'goals_per_season', 'assists_per_season', 'wage_eur', 'value_eur']
head_to_head_df = players_df.set_index('name')[key_stats]

fig, ax = plt.subplots(figsize=(12, 3))
ax.axis('off')
table = ax.table(cellText=head_to_head_df.values,
                 colLabels=head_to_head_df.columns,
                 rowLabels=head_to_head_df.index,
                 cellLoc='center',
                 loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Head to Head Player Stats Comparison')
plt.tight_layout()
plt.savefig(r'E:\\vs codes\\test\\charts\\05a2e12a-94fa-456a-8bfd-502a69db6d52\\head_to_head.png')
plt.close()
