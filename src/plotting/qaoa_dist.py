import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import numpy as np
import re
from matching_hub.repository import MatchingSession

def __scatter_heat_2d(n_values, m_values, x_values, colors, sources, unique_sources, output_file=None):
	scaling_factor = 20
	font_size = 14
	
	plt.figure(figsize=(10, 6))

	plt.scatter(
		n_values, 
		m_values, 
		s=[v * scaling_factor for v in x_values],
		c=colors, 
		alpha=0.3
	)
	
	plt.xlabel('Width (Number of qubits)', fontsize=font_size)
	plt.ylabel('Depth (Number of quantum gates)', fontsize=font_size)

	plt.xticks(fontsize=font_size)
	plt.yticks(fontsize=font_size)

	ax = plt.gca()
	ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
	ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
	
	# # Highlight region up to x = 156
	# x_highlight = 156
	# plt.axvspan(0, x_highlight, color='lightblue', alpha=0.3, label=f'QAOA circuits of up to {x_highlight} qubits')

	x_line = np.linspace(min(n_values), max(n_values), 500)
	y_line = 6 * x_line - 6
	plt.plot(x_line, y_line, color='pink', label=r'$y = 6 x - 6$')

	plt.legend(fontsize=font_size)

	if output_file:
		file_extension = os.path.splitext(output_file)[1].lower().lstrip('.')
		file_format = file_extension if file_extension else 'pdf'

		plt.savefig(output_file, format=file_format, dpi=300, bbox_inches='tight')
	else:
		plt.show()

	plt.close()

def plot_qaoa_dist(session, output_file=None):
	n = []
	m = []
	x = []
	sources = []
	colors = []

	unique_sources = set()

	c = 1
	
	for matching in session.get_all_matchings():
		if matching.qaoa_depth is not None:
			#print(f"\r{c}", end="")
				
			depth = matching.qaoa_depth
			width = matching.qaoa_width
		
			n.append(width)  # width is the same as matching.qubo_number_of_linear_terms
			m.append(depth)
			v_x = 1
			x.append(v_x)

			source_match = re.match(r"^_?(.*?)\/", "_placeholder")
			source = source_match.group(1) if source_match else "Unknown"
			sources.append(source)
			unique_sources.add(source)
	
			c += 1

	color_palette = sns.color_palette("tab10", len(unique_sources))
	source_color_map = {source: color for source, color in zip(unique_sources, color_palette)}

	colors = [source_color_map[source] for source in sources]

	__scatter_heat_2d(n, m, x, colors, sources, unique_sources, output_file)