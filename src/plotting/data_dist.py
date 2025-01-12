import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.font_manager as fm
import seaborn as sns
import re
import os
from schema_matching_scenarios import scenario_names, load_scenario
from matching_hub.repository import MatchingSession

def __scatter_heat_2d(n_values, m_values, x_values, colors, sources, unique_sources, output_file=None):
	scaling_factor = 20
	font_size = 14
	bold_font = fm.FontProperties(weight='bold', size=font_size)

	plt.figure(figsize=(11, 7))

	plt.scatter(
		n_values, 
		m_values, 
		s=[v * scaling_factor for v in x_values],
		c=colors, 
		alpha=0.3
	)

	plt.xlabel('Number of attributes in source relation', fontsize=font_size)
	plt.ylabel('Number of attributes in target relation', fontsize=font_size)

	plt.xticks(fontsize=font_size)
	plt.yticks(fontsize=font_size)

	plt.gca().set_aspect(2 / 3)

	color_palette = sns.color_palette("tab10", len(unique_sources))
	source_color_map = {source: color for source, color in zip(unique_sources, color_palette)}

	size_legend_elements = [
		Line2D([0], [0], marker='o', color='gray', 
			   markersize=(size[0] * scaling_factor) ** 0.5, 
			   label=size[1], markerfacecolor='gray', alpha=0.5, linestyle='None')
		for size in sorted([(5, '1 to 5'), (10, '6 to 10'), (20, '11 to 20'), 
							(30, '21 to 30'), (50, '31 to 50')])
	]

	source_legend_elements = [
		Line2D([0], [0], marker='o', color='w', 
			   label=source, markerfacecolor=source_color_map[source], markersize=10)
		for source in unique_sources
	]

	size_header = Line2D([0], [0], linestyle="None", label="Ground truth size")
	spacer = Line2D([0], [0], linestyle="None", label=" ")
	source_header = Line2D([0], [0], linestyle="None", label="Repository")

	combined_legend_elements = (
		[size_header] + size_legend_elements + [spacer, source_header] + source_legend_elements
	)

	legend = plt.legend(
		handles=combined_legend_elements,
		loc="center left",
		bbox_to_anchor=(1.02, 0.5),
		frameon=True,
		fontsize=font_size
	)

	plt.subplots_adjust(right=0.75)

	if output_file:
		file_extension = os.path.splitext(output_file)[1].lower().lstrip('.')
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
	colors = []

	unique_sources = set()

	for scenario in session.get_all_scenarios():
		scenario_data = load_scenario(scenario.name, False)
		stats = scenario_data.get_stats()

		n.append(stats.source_column_count)
		m.append(stats.target_column_count)
		v_x = min(stats.source_column_count, stats.target_column_count, stats.ground_truth_size)
		x.append(v_x)

		source_match = re.match(r"^_?(.*?)\/", scenario.name)
		source = source_match.group(1) if source_match else "Unknown"
		sources.append(source)
		unique_sources.add(source)

	color_palette = sns.color_palette("tab10", len(unique_sources))
	source_color_map = {source: color for source, color in zip(sorted(unique_sources), color_palette)}

	colors = [source_color_map[source] for source in sources]

	__scatter_heat_2d(n, m, x, colors, sources, unique_sources, output_file)
