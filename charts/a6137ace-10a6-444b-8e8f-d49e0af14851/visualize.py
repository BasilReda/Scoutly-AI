import matplotlib; matplotlib.use('Agg')
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from math import pi
import os

# Embed player_data directly
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
    "scout_note": "Prolific striker with consistent 20+ goal seasons and strong attacking stats, fitting well under the salary cap."
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
    "scout_note": "Dynamic forward with excellent goal and assist records, offering great value below the salary threshold."
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
    "scout_note": "Experienced striker with strong aerial ability and consistent goal scoring, well within budget and value limits."
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
    "scout_note": "Reliable goal scorer with balanced attacking skills and good physicality, fitting well under the salary cap."
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
    "scout_note": "Veteran striker with strong physical presence and consistent scoring, offering excellent value under budget."
  }
]

# Convert to DataFrame for easier manipulation
df = pd.DataFrame(player_data)

# Prepare data for radar chart
# Attributes: attacking, defending, sprint_speed, stamina, dribble_success, physicality
radar_attrs = ['attacking', 'defending', 'sprint_speed', 'stamina', 'dribble_success', 'physicality']

# Radar chart function

def make_radar_chart(df, attrs, output_path):
    # Number of variables
    categories = attrs
    N = len(categories)

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]  # Complete the loop

    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], categories, color='grey', size=12)

    # Draw ylabels
    ax.set_rlabel_position(30)
    plt.yticks([20,40,60,80,100], ["20","40","60","80","100"], color="grey", size=10)
    plt.ylim(0,100)

    # Plot each player
    for i, row in df.iterrows():
        values = row[attrs].tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=row['name'])
        ax.fill(angles, values, alpha=0.1)

    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.title('Player Radar Chart (Key Attributes)', size=15, y=1.1)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# Scatter plot wage vs overall_rating

def make_scatter(df, output_path):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='wage_eur', y='overall_rating', s=100, color='blue')
    for i, row in df.iterrows():
        plt.text(row['wage_eur']+1000, row['overall_rating'], row['name'], fontsize=9)
    plt.xlabel('Wage (EUR)')
    plt.ylabel('Overall Rating')
    plt.title('Wage vs Overall Rating')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# Pitch heatmap - approximate position zones

def make_pitch_heatmap(df, output_path):
    # Simplified pitch zones for ST: mostly central forward area
    # We'll plot a pitch and mark each player's approximate position
    plt.figure(figsize=(10, 6))
    pitch_length = 105
    pitch_width = 68

    # Draw pitch
    plt.plot([0, 0, pitch_length, pitch_length, 0], [0, pitch_width, pitch_width, 0, 0], color='black')
    plt.plot([pitch_length/2, pitch_length/2], [0, pitch_width], color='black')
    plt.plot([pitch_length*0.8, pitch_length*0.8], [0, pitch_width], color='black', linestyle='--')

    # Mark player positions (ST: around 80% length, center width)
    y_pos = pitch_width / 2
    x_pos = pitch_length * 0.8

    for i, row in df.iterrows():
        plt.scatter(x_pos, y_pos + (i-2)*3, s=200, label=row['name'])

    plt.title('Player Position Zones on Pitch (Approximate)')
    plt.axis('off')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# Trends: goals and assists per season

def make_trends(df, output_path):
    plt.figure(figsize=(10, 6))
    for i, row in df.iterrows():
        seasons = [s['season'] for s in row['seasons_data']]
        goals = [s['goals'] for s in row['seasons_data']]
        assists = [s['assists'] for s in row['seasons_data']]
        plt.plot(seasons, goals, marker='o', label=f"{row['name']} Goals")
        plt.plot(seasons, assists, marker='x', linestyle='--', label=f"{row['name']} Assists")

    plt.xlabel('Season')
    plt.ylabel('Count')
    plt.title('Goals and Assists per Season')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# Squad composition bar chart (current + incoming)
# Here we only have incoming players, so show count by age group or rating group

def make_squad_composition(df, output_path):
    plt.figure(figsize=(10, 6))
    # Age groups
    bins = [20, 25, 30, 35, 40]
    labels = ['20-24', '25-29', '30-34', '35+']
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)
    age_counts = df['age_group'].value_counts().sort_index()

    # Rating groups
    rating_bins = [80, 84, 88, 92]
    rating_labels = ['80-83', '84-87', '88-91']
    df['rating_group'] = pd.cut(df['overall_rating'], bins=rating_bins, labels=rating_labels, right=False)
    rating_counts = df['rating_group'].value_counts().sort_index()

    # Align indices and fill missing with 0
    rating_counts = rating_counts.reindex(labels, fill_value=0)

    # Plot side by side
    width = 0.35
    ind = np.arange(len(age_counts))

    plt.bar(ind, age_counts, width, label='Age Groups')
    plt.bar(ind + width, rating_counts, width, label='Rating Groups')

    plt.xlabel('Groups')
    plt.ylabel('Number of Players')
    plt.title('Squad Composition by Age and Rating Groups')
    plt.xticks(ind + width / 2, age_counts.index)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# Head to head comparison table

def make_head_to_head(df, output_path):
    # Select key stats
    stats = ['name', 'age', 'club', 'wage_eur', 'value_eur', 'overall_rating', 'potential', 'goals_per_season', 'assists_per_season', 'pass_accuracy', 'dribble_success', 'aerial_duels_won', 'sprint_speed', 'stamina', 'defending', 'attacking', 'physicality']
    data = df[stats].copy()

    # Format currency
    data['wage_eur'] = data['wage_eur'].apply(lambda x: f"€{x/1000:.0f}k")
    data['value_eur'] = data['value_eur'].apply(lambda x: f"€{x/1e6:.1f}M")

    # Create table plot
    fig, ax = plt.subplots(figsize=(15, 3))
    ax.axis('off')
    table = ax.table(cellText=data.values, colLabels=data.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    plt.title('Head to Head Player Comparison')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# Paths
output_dir = r"E:\vs codes\test\charts\a6137ace-10a6-444b-8e8f-d49e0af14851"

# Generate charts
make_radar_chart(df, radar_attrs, os.path.join(output_dir, 'radar_chart.png'))
make_scatter(df, os.path.join(output_dir, 'scatter.png'))
make_pitch_heatmap(df, os.path.join(output_dir, 'pitch_heatmap.png'))
make_trends(df, os.path.join(output_dir, 'trends.png'))
make_squad_composition(df, os.path.join(output_dir, 'squad_composition.png'))
make_head_to_head(df, os.path.join(output_dir, 'head_to_head.png'))

print("Charts generated")
