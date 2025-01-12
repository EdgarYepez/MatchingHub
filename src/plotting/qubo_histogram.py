import numpy as np
import matplotlib.pyplot as plt
from matching_hub.repository import MatchingSession
from matplotlib import colors
import os

def plot_qubo_histogram(session, output_file=None):
	font_size = 16

	linear_terms = []
	quadratic_terms = []

	for matching in session.get_all_matchings():
		linear_terms.append(matching.qubo_number_of_variables)
		quadratic_terms.append(matching.qubo_number_of_quadratic_terms)

	bins_x = 5
	bins_y = 5

	cmap = plt.cm.Blues
	cmap.set_under('white')

	plt.figure(figsize=(12, 6))
	hist, x_edges, y_edges, _ = plt.hist2d(
		linear_terms, quadratic_terms, 
		bins=[bins_x, bins_y], 
		cmap=cmap, 
		vmin=0.01
	)

	cbar = plt.colorbar(label='Number of QUBO formulations')
	cbar.ax.tick_params(labelsize=font_size)
	cbar.set_label('Number of QUBO formulations', fontsize=font_size)

	total_points = hist.sum()

	for i in range(len(x_edges) - 1):
		for j in range(len(y_edges) - 1):
			percentage = (hist[i, j] / total_points) * 100
			if percentage > 0:
				x_pos = (x_edges[i] + x_edges[i + 1]) / 2
				y_pos = (y_edges[j] + y_edges[j + 1]) / 2
				font_color = "white" if percentage > 50 else "black"
				plt.text(
					x_pos, y_pos, f"{percentage:.1f}%", 
					color=font_color, ha="center", va="center", fontsize=font_size
				)

	def format_bin_label(value):
		return f"{value:.1e}".replace('+0', '+') if value > 10000 else f"{int(value)}"

	x_tick_labels = [
		f"{format_bin_label(x_edges[i])} to {format_bin_label(x_edges[i + 1] - 1)}" 
		for i in range(len(x_edges) - 1)
	]
	y_tick_labels = [
		f"{format_bin_label(y_edges[i])} to {format_bin_label(y_edges[i + 1] - 1)}" 
		for i in range(len(y_edges) - 1)
	]

	plt.xticks(
		ticks=(x_edges[:-1] + x_edges[1:]) / 2,
		labels=x_tick_labels,
		rotation=45,
		fontsize=font_size
	)
	plt.yticks(
		ticks=(y_edges[:-1] + y_edges[1:]) / 2,
		labels=y_tick_labels,
		fontsize=font_size
	)
	
	plt.xlabel("Number of linear terms (variables)", fontsize=font_size + 4)
	plt.ylabel("Number of quadratic terms", fontsize=font_size + 4)
	plt.tight_layout()

	if output_file:
		file_extension = os.path.splitext(output_file)[1].lower().lstrip('.')
		file_format = file_extension if file_extension else 'pdf'

		plt.savefig(output_file, format=file_format, dpi=300, bbox_inches='tight')
	else:
		plt.show()

	plt.close()