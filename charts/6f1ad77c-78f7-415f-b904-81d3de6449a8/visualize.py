import matplotlib; matplotlib.use('Agg')
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Cleaned player_data JSON with proper unicode and no null bytes
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
    "scout_note": "Reliable Spanish goalkeeper with consistent clean sheet performance and good defensive stats, offering excellent value under the salary cap."
  }
]

# Prepare dataframes

# Radar chart data: attacking, defending, speed, stamina, dribble, physicality
radar_stats = ['attacking', 'defending', 'sprint_speed', 'stamina', 'dribble_success', 'physicality']
radar_df = pd.DataFrame([{stat: p[stat] for stat in radar_stats} for p in player_data], index=[p['name'] for p in player_data])

# Scatter data: wage vs overall_rating
scatter_df = pd.DataFrame({
    'name': [p['name'] for p in player_data],
    'wage': [p['wage_eur'] for p in player_data],
    'performance': [p['overall_rating'] for p in player_data]
})

# Pitch heatmap data: position zones simplified
# We'll map GK to a zone on the pitch
position_map = {'GK': (0.1, 0.5)}  # x,y normalized pitch coordinates
pitch_df = pd.DataFrame({
    'name': [p['name'] for p in player_data],
    'position': [p['position'] for p in player_data],
    'x': [position_map.get(p['position'], (0.5, 0.5))[0] for p in player_data],
    'y': [position_map.get(p['position'], (0.5, 0.5))[1] for p in player_data]
})

# Trends data: goals & assists per season
seasons = sorted(set(s['season'] for p in player_data for s in p['seasons_data']))
goals_data = {p['name']: [next((s['goals'] for s in p['seasons_data'] if s['season'] == season), 0) for season in seasons] for p in player_data}
assists_data = {p['name']: [next((s['assists'] for s in p['seasons_data'] if s['season'] == season), 0) for season in seasons] for p in player_data}

# Squad composition: current + incoming (simulate incoming as 1 for each player for demo)
squad_slots = ['GK']
squad_current = {pos: sum(1 for p in player_data if p['position'] == pos) for pos in squad_slots}
squad_incoming = {pos: 1 for pos in squad_slots}  # assume 1 incoming per position

# Head to head: key stats side by side
head_to_head_stats = ['age', 'wage_eur', 'value_eur', 'overall_rating', 'potential', 'pass_accuracy', 'dribble_success', 'aerial_duels_won', 'sprint_speed', 'stamina', 'defending', 'attacking', 'physicality']
head_to_head_df = pd.DataFrame({p['name']: [p[stat] for stat in head_to_head_stats] for p in player_data}, index=head_to_head_stats)

# 1. Radar chart
labels = radar_stats
num_vars = len(labels)

angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

for i, player in enumerate(player_data):
    values = radar_df.loc[player['name']].tolist()
    values += values[:1]
    ax.plot(angles, values, label=player['name'])
    ax.fill(angles, values, alpha=0.25)

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
ax.set_thetagrids(np.degrees(angles[:-1]), labels)
ax.set_ylim(0, 100)
ax.set_title('Player Radar Comparison')
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.tight_layout()
radar_path = os.path.join(r"E:\vs codes\test\charts\6f1ad77c-78f7-415f-b904-81d3de6449a8", 'radar_chart.png')
plt.savefig(radar_path)
plt.close()

# 2. Scatter plot wage vs performance
plt.figure(figsize=(8, 6))
sns.scatterplot(data=scatter_df, x='wage', y='performance', s=100)
for i, row in scatter_df.iterrows():
    plt.text(row['wage'] + 500, row['performance'], row['name'])
plt.xlabel('Wage (EUR)')
plt.ylabel('Overall Rating')
plt.title('Wage vs Performance')
plt.tight_layout()
scatter_path = os.path.join(r"E:\vs codes\test\charts\6f1ad77c-78f7-415f-b904-81d3de6449a8", 'scatter.png')
plt.savefig(scatter_path)
plt.close()

# 3. Pitch heatmap
plt.figure(figsize=(8, 6))
plt.scatter(pitch_df['x'], pitch_df['y'], s=300, c='blue')
for i, row in pitch_df.iterrows():
    plt.text(row['x'], row['y'] + 0.05, row['name'], ha='center')
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.title('Player Position Zones on Pitch')
plt.xlabel('Pitch Length')
plt.ylabel('Pitch Width')
plt.gca().invert_xaxis()
plt.tight_layout()
pitch_path = os.path.join(r"E:\vs codes\test\charts\6f1ad77c-78f7-415f-b904-81d3de6449a8", 'pitch_heatmap.png')
plt.savefig(pitch_path)
plt.close()

# 4. Trends: goals & assists per season
plt.figure(figsize=(10, 6))
for player in player_data:
    plt.plot(seasons, goals_data[player['name']], marker='o', label=f"{player['name']} Goals")
    plt.plot(seasons, assists_data[player['name']], marker='x', linestyle='--', label=f"{player['name']} Assists")
plt.xlabel('Season')
plt.ylabel('Count')
plt.title('Goals and Assists per Season')
plt.legend()
plt.tight_layout()
trends_path = os.path.join(r"E:\vs codes\test\charts\6f1ad77c-78f7-415f-b904-81d3de6449a8", 'trends.png')
plt.savefig(trends_path)
plt.close()

# 5. Squad composition bar chart
positions = list(squad_current.keys())
current_counts = [squad_current[pos] for pos in positions]
incoming_counts = [squad_incoming[pos] for pos in positions]

x = np.arange(len(positions))
width = 0.35

fig, ax = plt.subplots(figsize=(6, 4))
rects1 = ax.bar(x - width/2, current_counts, width, label='Current')
rects2 = ax.bar(x + width/2, incoming_counts, width, label='Incoming')

ax.set_ylabel('Number of Players')
ax.set_title('Squad Composition by Position')
ax.set_xticks(x)
ax.set_xticklabels(positions)
ax.legend()
plt.tight_layout()
squad_path = os.path.join(r"E:\vs codes\test\charts\6f1ad77c-78f7-415f-b904-81d3de6449a8", 'squad_composition.png')
plt.savefig(squad_path)
plt.close()

# 6. Head to head table
fig, ax = plt.subplots(figsize=(12, 4))
ax.axis('off')

# Prepare table data
cell_text = []
rows = head_to_head_stats
cols = [p['name'] for p in player_data]
for stat in rows:
    cell_text.append([str(head_to_head_df[col][stat]) for col in cols])

# Create table
table = ax.table(cellText=cell_text, rowLabels=rows, colLabels=cols, loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.title('Head to Head Player Stats')
plt.tight_layout()
head_to_head_path = os.path.join(r"E:\vs codes\test\charts\6f1ad77c-78f7-415f-b904-81d3de6449a8", 'head_to_head.png')
plt.savefig(head_to_head_path)
plt.close()

# Return paths for verification
print(radar_path)
print(scatter_path)
print(pitch_path)
print(trends_path)
print(squad_path)
print(head_to_head_path)
