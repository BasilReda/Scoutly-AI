import matplotlib; matplotlib.use('Agg')
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from math import pi

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
    "scout_note": "Proven striker with consistent 20+ goal seasons and strong attacking attributes, offering excellent value at his wage and market price."
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
    "scout_note": "Dynamic forward with excellent goal and assist numbers, combined with high potential and strong physical and technical skills."
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
    "scout_note": "Experienced striker with reliable goal scoring and strong aerial ability, offering solid attacking output at a reasonable wage."
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
    "scout_note": "Consistent goal scorer with good assist numbers and balanced attacking skills, providing strong value under the wage cap."
  }
]

# Convert to DataFrame
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi

df = pd.DataFrame(player_data)

# Radar chart attributes
attributes = ['attacking', 'defending', 'sprint_speed', 'stamina', 'dribble_success', 'physicality']

num_vars = len(attributes)
angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
angles += angles[:1]

plt.figure(figsize=(10, 10))
for i, player in df.iterrows():
    values = [player[attr] for attr in attributes]
    values += values[:1]
    ax = plt.subplot(2, 2, i+1, polar=True)
    plt.xticks(angles[:-1], attributes, color='grey', size=8)
    ax.plot(angles, values, linewidth=2, linestyle='solid', label=player['name'])
    ax.fill(angles, values, alpha=0.25)
    ax.set_ylim(0, 100)
    plt.title(player['name'], size=11, color='black', y=1.1)
plt.tight_layout()
plt.savefig(r"E:\vs codes\test\charts\b2865beb-8589-446b-a379-ea5f79bf39ca\radar_chart.png")
plt.close()

# Scatter plot: wage vs overall_rating
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='wage_eur', y='overall_rating', s=100, color='blue')
for i, player in df.iterrows():
    plt.text(player['wage_eur']+1000, player['overall_rating'], player['name'], fontsize=9)
plt.xlabel('Wage (EUR)')
plt.ylabel('Overall Rating')
plt.title('Wage vs Overall Rating')
plt.tight_layout()
plt.savefig(r"E:\vs codes\test\charts\b2865beb-8589-446b-a379-ea5f79bf39ca\scatter.png")
plt.close()

# Pitch heatmap
plt.figure(figsize=(8, 6))
pitch_length = 105
pitch_width = 68
plt.plot([0, 0, pitch_length, pitch_length, 0], [0, pitch_width, pitch_width, 0, 0], color='black')
plt.title('Player Positions on Pitch')
positions = {'ST': (pitch_length*0.85, pitch_width/2)}
for i, player in df.iterrows():
    pos = positions.get(player['position'], (pitch_length/2, pitch_width/2))
    plt.scatter(pos[0], pos[1], s=200, label=player['name'])
    plt.text(pos[0]+1, pos[1], player['name'], fontsize=9)
plt.xlim(0, pitch_length)
plt.ylim(0, pitch_width)
plt.axis('off')
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig(r"E:\vs codes\test\charts\b2865beb-8589-446b-a379-ea5f79bf39ca\pitch_heatmap.png")
plt.close()

# Trends: goals & assists per season
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
plt.legend(loc='upper left', fontsize='small')
plt.tight_layout()
plt.savefig(r"E:\vs codes\test\charts\b2865beb-8589-446b-a379-ea5f79bf39ca\trends.png")
plt.close()

# Squad composition
plt.figure(figsize=(10, 6))
names = df['name'].tolist()
current_slots = [1]*len(names)
incoming_slots = [1]*len(names)
bar_width = 0.4
indices = np.arange(len(names))
plt.bar(indices, current_slots, bar_width, label='Current')
plt.bar(indices + bar_width, incoming_slots, bar_width, label='Incoming')
plt.xticks(indices + bar_width / 2, names, rotation=45)
plt.ylabel('Squad Slots')
plt.title('Squad Composition: Current vs Incoming')
plt.legend()
plt.tight_layout()
plt.savefig(r"E:\vs codes\test\charts\b2865beb-8589-446b-a379-ea5f79bf39ca\squad_composition.png")
plt.close()

# Head to head table
plt.figure(figsize=(12, 4))
columns = ['Name', 'Age', 'Overall', 'Potential', 'Goals/Season', 'Assists/Season', 'Wage (EUR)', 'Value (EUR)']
cell_text = []
for player in player_data:
    cell_text.append([
        player['name'],
        player['age'],
        player['overall_rating'],
        player['potential'],
        player['goals_per_season'],
        player['assists_per_season'],
        f"{player['wage_eur']:,}",
        f"{player['value_eur']:,}"
    ])
table = plt.table(cellText=cell_text, colLabels=columns, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
plt.axis('off')
plt.title('Head to Head Player Comparison')
plt.tight_layout()
plt.savefig(r"E:\vs codes\test\charts\b2865beb-8589-446b-a379-ea5f79bf39ca\head_to_head.png")
plt.close()
