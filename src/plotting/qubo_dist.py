import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import re
from math import comb
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
		alpha=0.1
	)

	plt.xlabel('Number of linear terms (variables)', fontsize=font_size)
	plt.ylabel('Number of quadratic terms (in $\\times 10^6$)', fontsize=font_size)

	plt.xticks(fontsize=font_size)
	plt.yticks(fontsize=font_size)
	
	x = np.linspace(0, 1800, 500)  # Generate 500 points between 0 and 1800

	# Add n choose r line
	y_n_choose_r = [comb(int(val), 2) if val >= 2 else 0 for val in x]
	plt.plot(x, y_n_choose_r, color='pink', label=r'$y = \binom{x}{2}$', alpha=1)

	# # Highlight region up to x = 156
	# x_highlight = 156
	# plt.axvspan(0, x_highlight, color='lightblue', alpha=0.3, label=f'QUBO formulations of up to {x_highlight} linear terms')

	plt.legend(loc='upper left', fontsize=font_size)

	if output_file:
		file_extension = os.path.splitext(output_file)[1].lower().lstrip('.')
		file_format = file_extension if file_extension else 'pdf'
		
		plt.savefig(output_file, format=file_format, dpi=300, bbox_inches='tight')
	else:
		plt.show()

	plt.close()

def plot_qubo_dist(session, output_file=None):
	n = []
	m = []
	x = []
	sources = []
	colors = []

	unique_sources = set()

	c = 1
	for matching in session.get_all_matchings():
		#print(f"\r{c}", end="")	

		n.append(matching.qubo_number_of_variables)
		m.append(matching.qubo_number_of_quadratic_terms)
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
