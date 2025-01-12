import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
import numpy as np
from collections import defaultdict
from mpl_toolkits.mplot3d import Axes3D
import re
from schema_matching_scenarios import scenario_names, load_scenario
from matching_hub.repository import MatchingSession

def __scatter_heat_3d(n_values, m_values, x_values, sources, source_color_map, output_file=None):
	grouped_data = defaultdict(list)
	for n_val, m_val, x_val, source in zip(n_values, m_values, x_values, sources):
		grouped_data[(n_val, m_val, x_val)].append(source)
	
	fig = plt.figure(figsize=(12, 8))
	ax = fig.add_subplot(111, projection='3d')
	
	ax.set_xlabel('Number of Fields in Source Table')
	ax.set_ylabel('Number of Fields in Target Table')
	ax.set_zlabel('Ground Truth Size')

	scaling_factor = 50

	for (n, m, x), source_list in grouped_data.items():
		count = len(source_list)
		
		unique_sources_at_point = set(source_list)
		if len(unique_sources_at_point) == 1:
			color = source_color_map[next(iter(unique_sources_at_point))]
		else:
			color = 'gray'
		
		ax.scatter(n, m, x, s=count * scaling_factor, color=color, alpha=0.6, edgecolors='w')

	source_legend_elements = [
		Line2D([0], [0], marker='o', color='w', label=source,
			   markerfacecolor=color, markersize=10, linestyle='None')
		for source, color in source_color_map.items()
	]
	source_legend_elements.append(Line2D([0], [0], marker='o', color='w', label="Mixed Sources",
										 markerfacecolor='gray', markersize=10, linestyle='None'))
	source_legend = ax.legend(handles=source_legend_elements, title="Sources", loc="upper right", frameon=True)
	ax.add_artist(source_legend)

	size_legend_elements = [
		Line2D([0], [0], marker='o', color='gray', markersize=(size * scaling_factor) ** 0.5, 
			   label=f'{size} instances', markerfacecolor='gray', alpha=0.5, linestyle='None')
		for size in [1, 5, 10, 20]
	]
	size_legend = ax.legend(handles=size_legend_elements, title="Number of Points", loc="center left", 
							bbox_to_anchor=(1.15, 0.5), frameon=True)

	if output_file:
		file_extension = output_file.split(".")[-1].lower()
		file_format = file_extension if file_extension else 'pdf'

		plt.savefig(output_file, format=file_format, dpi=300, bbox_inches='tight')
	else:
		plt.show()

	plt.close()

def plot_data_dist(session, output_file=None):
	n = []
	m = []
	x = []
	sources = []

	unique_sources = set()
	
	for scenario in session.get_all_scenarios():
		scenario_data = load_scenario(scenario.name, False)
		stats = scenario_data.get_stats()
	
		n_val = stats.source_column_count
		m_val = stats.target_column_count
		x_val = min(stats.source_column_count, stats.target_column_count, stats.ground_truth_size)
	
		n.append(n_val)
		m.append(m_val)
		x.append(x_val)
	
		source_match = re.match(r"^_?(.*?)\/", scenario.name)
		source = source_match.group(1) if source_match else "Unknown"
		sources.append(source)
		unique_sources.add(source)

	color_palette = sns.color_palette("tab10", len(unique_sources))
	source_color_map = {source: color for source, color in zip(sorted(unique_sources), color_palette)}

	__scatter_heat_3d(n, m, x, sources, source_color_map, output_file)