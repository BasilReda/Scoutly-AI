import matplotlib; matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load player data
players = player_data

# Prepare DataFrame
df = pd.DataFrame(players)

# Radar chart data preparation
radar_attrs = ['attacking', 'defending', 'sprint_speed', 'stamina', 'dribble_success', 'physicality']

# Normalize radar data for better comparison
radar_data = df[['name'] + radar_attrs].copy()
for attr in radar_attrs:
    max_val = radar_data[attr].max()
    min_val = radar_data[attr].min()
    radar_data[attr] = (radar_data[attr] - min_val) / (max_val - min_val)

# Radar chart function
from math import pi

def make_radar_chart(ax, angles, data, color, label):
    data = np.concatenate((data, [data[0]]))
    ax.plot(angles, data, color=color, linewidth=2, label=label)
    ax.fill(angles, data, color=color, alpha=0.25)

# 1. Radar chart
labels = radar_attrs
num_vars = len(labels)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
colors = sns.color_palette('tab10', len(df))

for i, row in radar_data.iterrows():
    values = row[radar_attrs].values
    make_radar_chart(ax, angles, values, colors[i], row['name'])

ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)
ax.set_thetagrids(np.degrees(angles[:-1]), labels)
ax.set_ylim(0, 1)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.title('Player Radar Comparison')
plt.tight_layout()
plt.savefig(r'E:\vs codes\test\charts\cc8c1677-eeb7-494a-b2dc-75f098695069\radar_chart.png')
plt.close()

# 2. Scatter plot: wage vs overall_rating
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='wage_eur', y='overall_rating', hue='name', palette=colors, s=100)
for i, row in df.iterrows():
    plt.text(row['wage_eur']+1000, row['overall_rating'], row['name'], fontsize=9)
plt.xlabel('Wage (EUR)')
plt.ylabel('Overall Rating')
plt.title('Wage vs Overall Rating')
plt.tight_layout()
plt.savefig(r'E:\vs codes\test\charts\cc8c1677-eeb7-494a-b2dc-75f098695069\scatter.png')
plt.close()

# 3. Pitch heatmap: position zones
# Simplified pitch zones for ST: center forward area
pitch_length = 105
pitch_width = 68

plt.figure(figsize=(12, 7))
# Draw pitch
plt.plot([0, 0, pitch_length, pitch_length, 0], [0, pitch_width, pitch_width, 0, 0], color='black')
plt.fill_betweenx([pitch_width*0.3, pitch_width*0.7], pitch_length*0.7, pitch_length, color='lightblue', alpha=0.3)

# Plot players in the forward zone with some vertical spread
y_positions = np.linspace(pitch_width*0.35, pitch_width*0.65, len(df))
for i, player in enumerate(df['name']):
    plt.scatter(pitch_length*0.85, y_positions[i], s=200, label=player)
    plt.text(pitch_length*0.85+1, y_positions[i], player, verticalalignment='center')

plt.title('Player Position Zones on Pitch (ST)')
plt.axis('off')
plt.tight_layout()
plt.savefig(r'E:\vs codes\test\charts\cc8c1677-eeb7-494a-b2dc-75f098695069\pitch_heatmap.png')
plt.close()

# 4. Trends: goals & assists per season
plt.figure(figsize=(10, 6))
for player in players:
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
plt.savefig(r'E:\vs codes\test\charts\cc8c1677-eeb7-494a-b2dc-75f098695069\trends.png')
plt.close()

# 5. Squad composition: bar chart of current wage and value
plt.figure(figsize=(10, 6))
bar_width = 0.35
indices = np.arange(len(df))
plt.bar(indices, df['wage_eur'], bar_width, label='Wage (EUR)', color='skyblue')
plt.bar(indices + bar_width, df['value_eur'], bar_width, label='Value (EUR)', color='orange')
plt.xticks(indices + bar_width / 2, df['name'])
plt.ylabel('EUR')
plt.title('Squad Composition: Wage and Market Value')
plt.legend()
plt.tight_layout()
plt.savefig(r'E:\vs codes\test\charts\cc8c1677-eeb7-494a-b2dc-75f098695069\squad_composition.png')
plt.close()

# 6. Head to head: table of key stats
key_stats = ['age', 'overall_rating', 'potential', 'goals_per_season', 'assists_per_season', 'pass_accuracy', 'dribble_success', 'aerial_duels_won', 'sprint_speed', 'stamina', 'defending', 'attacking', 'physicality']

fig, ax = plt.subplots(figsize=(14, 3))
ax.axis('off')
cell_text = []
for stat in key_stats:
    row = [stat.replace('_', ' ').title()]
    for player in players:
        val = player[stat]
        if isinstance(val, float):
            val = f"{val:.1f}"
        row.append(val)
    cell_text.append(row)

columns = ['Stat'] + [p['name'] for p in players]

table = ax.table(cellText=cell_text, colLabels=columns, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)
plt.title('Head to Head Player Comparison')
plt.tight_layout()
plt.savefig(r'E:\vs codes\test\charts\cc8c1677-eeb7-494a-b2dc-75f098695069\head_to_head.png')
plt.close()
