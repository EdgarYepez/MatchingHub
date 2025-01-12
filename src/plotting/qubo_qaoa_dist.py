import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import numpy as np
import re
from matching_hub.repository import MatchingSession
from matplotlib.patches import Rectangle

def __scatter_and_box_plot_with_density_labels(n_values, m_values, x_values, colors, sources, unique_sources, total_points, output_file=None):
	scaling_factor = 20
	font_size = 18

	plt.figure(figsize=(12, 6))
	plt.scatter(
		n_values, 
		m_values, 
		s=[v * scaling_factor for v in x_values],
		c=colors, 
		alpha=0.05
	)

	min_bin = (min(n_values) // 1000) * 1000
	max_bin = ((max(n_values) // 1000) + 1) * 1000
	bins = np.arange(min_bin, max_bin + 1, 1000)
	bin_centers = (bins[:-1] + bins[1:]) / 2
	bin_indices = np.digitize(n_values, bins)

	binned_means = []
	box_data = []
	densities = []

	for i in range(1, len(bins)):
		bin_depths = [m_values[j] for j in range(len(n_values)) if bin_indices[j] == i]
		if bin_depths:
			binned_means.append(np.mean(bin_depths))
			box_data.append(bin_depths)
			densities.append(len(bin_depths) / total_points * 100)
		else:
			binned_means.append(None)
			box_data.append([])
			densities.append(0)
			
	valid_bins = [(bin_centers[i], binned_means[i], bins[i], bins[i + 1], densities[i]) 
				  for i in range(len(bin_centers)) if binned_means[i] is not None]
	valid_centers, valid_means, valid_edges_left, valid_edges_right, valid_densities = zip(*valid_bins)

	for left, right, mean, density in zip(valid_edges_left, valid_edges_right, valid_means, valid_densities):
		if mean is not None:
			bin_depths = [m_values[j] for j in range(len(n_values)) if left <= n_values[j] < right]
			depth_min = min(bin_depths) if bin_depths else 0
			depth_max = max(bin_depths) if bin_depths else 0
			
			rect = Rectangle((left, depth_min), right - left, depth_max - depth_min, 
							 linewidth=1, edgecolor='blue', facecolor='none', linestyle='--', alpha=0.4)
			plt.gca().add_patch(rect)
			
			label_x = (left + right) / 2 + 250
			label_y = depth_max + 2
			plt.text(label_x, label_y, f"{density:.1f}%", ha='right', va='bottom', fontsize=font_size, color='black')

	for i, depths in enumerate(box_data):
		if depths:
			plt.boxplot(
				depths, 
				positions=[bin_centers[i]],
				widths=(bins[i + 1] - bins[i]) * 0.5,
				patch_artist=True,
				boxprops=dict(facecolor="lightblue", color="black", alpha=0.7),
				medianprops=dict(color="red"),
				showmeans=True,
				whis=[0, 100]
			)

	all_ticks = list(bins)
	plt.xticks(
		ticks=all_ticks,
		labels=[f"{int(val)}" for val in all_ticks],
		rotation=45,
		fontsize=font_size
	)
	plt.yticks(fontsize=font_size)

	plt.xlabel('QUBO Size (Number of quadratic terms)', fontsize=font_size)
	plt.ylabel('Depth (Number of quantum gates)', fontsize=font_size)

	ax = plt.gca()
	ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
	
	y_min, y_max = ax.get_ylim()
	ax.set_ylim(y_min, y_max + 0.05 * (y_max - y_min))

	plt.tight_layout()

	if output_file:
		file_extension = os.path.splitext(output_file)[1].lower().lstrip('.')
		file_format = file_extension if file_extension else 'pdf'

		plt.savefig(output_file, format=file_format, dpi=300, bbox_inches='tight')
	else:
		plt.show()

	plt.close()

def plot_qubo_qaoa_dist(session, output_file=None):
	n = []
	m = []
	x = []
	sources = []
	colors = []

	unique_sources = set()

	c = 0
	total_points = 0
	for matching in session.get_all_matchings():
		if matching.qubo_formula is not None:
			total_points += 1
			if matching.qaoa_depth is not None:
				c += 1
				#print(f"\r{c}", end="")    
				depth = matching.qaoa_depth
				width = matching.qaoa_width
				time_ansatz = matching.qaoa_time_ansatz
				time_transpile = matching.qaoa_time_transpile
			
				n.append(matching.qubo_number_of_quadratic_terms)  # QUBO size
				m.append(depth)
				v_x = 1
				x.append(v_x)

				source_match = re.match(r"^_?(.*?)\/", "_placeholder")
				source = source_match.group(1) if source_match else "Unknown"
				sources.append(source)
				unique_sources.add(source)	

	color_palette = sns.color_palette("tab10", len(unique_sources))
	source_color_map = {source: color for source, color in zip(unique_sources, color_palette)}

	colors = [source_color_map[source] for source in sources]

	__scatter_and_box_plot_with_density_labels(n, m, x, colors, sources, unique_sources, total_points, output_file)
