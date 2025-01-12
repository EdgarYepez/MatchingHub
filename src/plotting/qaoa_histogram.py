import os
import matplotlib.pyplot as plt
import numpy as np
import re
from matching_hub.repository import MatchingSession

def __plot_histogram_with_edge_labels(n_values, bin_width=50, output_file=None):
	plt.figure(figsize=(14, 6))
	font_size = 20

	bins_x = np.arange(min(n_values), max(n_values) + bin_width, bin_width)
	hist, bin_edges = np.histogram(n_values, bins=bins_x)

	plt.bar(bin_edges[:-1], hist, width=bin_width, align='edge', color='blue', alpha=0.7, edgecolor='black')

	total_count = np.sum(hist)
	for i in range(len(hist)):
		if hist[i] > 0:
			percentage = (hist[i] / total_count) * 100
			x_pos = (bin_edges[i] + bin_edges[i + 1]) / 2
			plt.text(x_pos, hist[i], f"{percentage:.1f}%", ha="center", va="bottom", fontsize=font_size, color="black")

	plt.xlabel('Width (Number of qubits)', fontsize=font_size+4)
	plt.ylabel('Number of circuits', fontsize=font_size+4)
	
	plt.xticks(bin_edges, [f"{int(edge) - 1}" for edge in bin_edges], rotation=45, fontsize=font_size)
	plt.yticks(fontsize=font_size)

	plt.xlim(bin_edges[0], bin_edges[-1])
	
	ax = plt.gca()
	y_min, y_max = ax.get_ylim()
	ax.set_ylim(y_min, y_max + 0.03 * (y_max - y_min))

	plt.tight_layout()

	if output_file:
		file_extension = os.path.splitext(output_file)[1].lower().lstrip('.')
		file_format = file_extension if file_extension else 'pdf'

		plt.savefig(output_file, format=file_format, dpi=300, bbox_inches='tight')
	else:
		plt.show()

	plt.close()

def plot_qaoa_histogram(session, output_file=None):
	n = []
	sources = []

	unique_sources = set()

	c = 1

	for matching in session.get_all_matchings():
		if matching.qaoa_width is not None:
			#print(f"\r{c}", end="")
	
			width = matching.qaoa_width

			n.append(width)  # width is the same as matching.qubo_number_of_linear_terms

			source_match = re.match(r"^_?(.*?)\/", "_placeholder")
			source = source_match.group(1) if source_match else "Unknown"
			sources.append(source)
			unique_sources.add(source)
	
			c += 1

	__plot_histogram_with_edge_labels(n, bin_width=20, output_file=output_file)
