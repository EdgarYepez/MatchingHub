import os
import re
import random
from collections import defaultdict
from matching_hub.repository import MatchingSession
import numpy as np
import pandas as pd

def __build_metrics_df(session, group):
	data = []
	
	def __has_metrics(matching):
		if group == 'qubo':
			return matching.qubo_recall_ground_truth_size is not None
		else:
			return matching.qaoa_recall_ground_truth_size is not None
	
	def __get_metrics(matching):
		if group == 'qubo':
			return matching.qubo_recall_ground_truth_size
		else:
			return matching.qaoa_recall_ground_truth_size

	for matching in session.get_all_matchings():
		if __has_metrics(matching):
			data.append({'id': matching.id, 'recall_ground_truth_size': __get_metrics(matching)})

	df = pd.DataFrame(data)
	return df

def generate_recall_tables(session, group):
	num_bins = 4
	bins = defaultdict(lambda: {"left": [], "right": [], "sources": [], "id": None})
	df = __build_metrics_df(session, group)

	ground_truth_sizes = [
		session.get_matching_by_id(id_value).dataset.ground_truth_size
		for id_value in df["id"]
	]

	bin_edges = np.linspace(min(0, *ground_truth_sizes), max(ground_truth_sizes), num_bins + 1).astype(int)

	total_points = len(df)

	c = 1	
	for id_value, qubo_recall_ground_truth_size in df.itertuples(index=False):
		matching = session.get_matching_by_id(id_value)
	
		#print(f"\r{c}", end="")

		source_match = re.match(r"^_?(.*?)\/", matching.dataset.name)
		source = source_match.group(1) if source_match else "Unknown"

		ground_truth_size = matching.dataset.ground_truth_size
		recall_ground_truth_size = matching.recall_ground_truth_size

		for i in range(num_bins):
			if bin_edges[i] <= ground_truth_size < bin_edges[i + 1] + 1:
				bin_key = f"Bin {i + 1}: GT {bin_edges[i] + 1} to {bin_edges[i + 1]}"
				bins[bin_key]["id"] = i
				bins[bin_key]["left"].append(recall_ground_truth_size)
				bins[bin_key]["right"].append(qubo_recall_ground_truth_size)
				bins[bin_key]["sources"].append(source)
				break

		c += 1

	head = group.upper()
	for bin_key in sorted(bins.keys(), key=lambda x: bins[x]["id"]):
		bin_data = bins[bin_key]
	
		data = defaultdict(list)
		for left, right, source in zip(bin_data["left"], bin_data["right"], bin_data["sources"]):
			data["Source"].append(source)
			data["Recall@GT"].append(left)
			data[f"{head} Recall@GT"].append(right)

		df = pd.DataFrame(data)
		stats = df.groupby("Source").agg(
			Algs_Recall_GT_Mean=("Recall@GT", "mean"),
			Algs_Recall_GT_Std=("Recall@GT", "std"),
			**{f"{head}_Recall_GT_Mean": (f"{head} Recall@GT", "mean")},
			**{f"{head}_Recall_GT_Std": (f"{head} Recall@GT", "std")}
		).reset_index()

		stats["Percentage"] = stats["Source"].apply(lambda source: len(df[df["Source"] == source]) / total_points * 100)

		stats["Improvement"] = stats[f"{head}_Recall_GT_Mean"] - stats["Algs_Recall_GT_Mean"]
		stats["Improvement"] = stats["Improvement"].apply(lambda x: "Yes" if x > 0 else "No")

		yield bin_key, stats