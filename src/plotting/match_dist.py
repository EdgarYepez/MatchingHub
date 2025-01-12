import os
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
import numpy as np
import re
from collections import defaultdict
from matching_hub.repository import MatchingSession

def __scatter_and_mean_depth_line_plot(n_values, m_values, x_values, colors, sources, unique_sources, output_file=None):
	scaling_factor = 20
	font_size = 18

	plt.figure(figsize=(12, 6))
	plt.scatter(
		n_values, 
		m_values, 
		s=[v * scaling_factor for v in x_values],
		c=colors, 
		alpha=0.5
	)

	plt.xlabel('Ground truth size', fontsize=font_size)
	plt.ylabel('Recall@GT', fontsize=font_size)

	plt.xticks(fontsize=font_size)
	plt.yticks(fontsize=font_size)

	source_legend_elements = [
		Line2D([0], [0], marker='o', color='w', label=source,
			   markerfacecolor=source_color_map[source], markersize=10)
		for source in unique_sources
	]

	plt.legend(handles=source_legend_elements, title="Matchings from repository", title_fontsize=font_size, 
			   loc="upper center", bbox_to_anchor=(0.5, -0.12), 
			   frameon=True, ncol=2, fontsize=font_size)

	plt.tight_layout(rect=[0, 0.01, 1, 1])

	if output_file:
		file_extension = os.path.splitext(output_file)[1].lower().lstrip('.')
		file_format = file_extension if file_extension else 'pdf'

		plt.savefig(output_file, format=file_format, dpi=300, bbox_inches='tight')
	else:
		plt.show()

	plt.close()

def plot_match_dist(session, output_file=None):
	n = []
	m = []
	x = []
	sources = []
	colors = []

	unique_sources = set()

	c = 1

	for matching in session.get_all_matchings():
		#print(f"\r{c}", end="")
	
		ground_truth_size = matching.dataset.ground_truth_size
		recall_ground_truth_size = matching.recall_ground_truth_size

		n.append(ground_truth_size)
		m.append(matching.recall_ground_truth_size)
		v_x = 1
		x.append(v_x)

		source_match = re.match(r"^_?(.*?)\/", matching.dataset.name)
		source = source_match.group(1) if source_match else "Unknown"
		sources.append(source)
		unique_sources.add(source)
	
		c += 1

	color_palette = sns.color_palette("tab10", len(unique_sources))
	global source_color_map
	source_color_map = {source: color for source, color in zip(sorted(unique_sources), color_palette)}

	colors = [source_color_map[source] for source in sources]

	__scatter_and_mean_depth_line_plot(n, m, x, colors, sources, unique_sources, output_file)