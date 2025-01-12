from valentine.algorithms.jaccard_distance import StringDistanceFunction
from valentine import MatcherResults, valentine_match
from valentine.algorithms import *
import re
import json

class ResultAggregator:

	def __init__(self):
		self.arguments = None
		self.matches = None
		self.metrics = None
	
	def update(self, arguments, matches, metrics):
		ret = self.metrics is None or metrics['F1Score'] > self.metrics['F1Score'] or metrics['RecallAtSizeofGroundTruth'] > self.metrics['RecallAtSizeofGroundTruth']
		if ret:
			self.arguments = arguments
			self.matches = matches
			self.metrics = metrics
		return ret
	
def serialise_parameters(parameters_dict):
	def custom_serialiser(obj):
		if isinstance(obj, StringDistanceFunction):
			return obj.name
		raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
	parameters_json = json.dumps(parameters_dict, default=custom_serialiser)
	return parameters_json

def get_matchers(algorithm, argument_grid_strs):
	def __build_argument_iterator(argument, grid_str):
		for chunk in re.finditer(r'[^,]+', str(grid_str)):
			chunk_text = chunk.group().strip()
			range_chunk = re.match(r'\s*(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)(?:\s*:\s*(\d+(?:\.\d+)?))?', chunk_text)
			if range_chunk:
				precision = 5
				start = float(range_chunk.group(1).strip())
				step = 1
				end = float(range_chunk.group(2).strip())
				if range_chunk.group(3):
					step = end
					end = float(range_chunk.group(3).strip())
				current = round(start, precision)
				while current <= end:
					yield argument, current
					current = round(current + step, precision)
			else:
				if re.match(r'^\d+(?:\.\d+)?$', chunk_text):
					yield argument, float(chunk_text)
				else:
					yield argument, chunk_text

	argument_names = list(argument_grid_strs.keys())

	def __argument_generator(iterator_id = 0, argument_values = { }):
		if iterator_id == len(argument_names):
			yield argument_values.copy()
		else:
			for arg, value in __build_argument_iterator(argument_names[iterator_id], argument_grid_strs[argument_names[iterator_id]]):
				argument_values[arg] = value
				yield from __argument_generator(iterator_id + 1, argument_values)

	algorithm = algorithm.lower()

	for argument_values in __argument_generator():
		matcher = None
		if algorithm == 'coma':
			if 'use_instances' in argument_values:
				argument_values['use_instances'] = str(argument_values['use_instances']).strip().lower() == 'true'
			matcher = Coma(**argument_values)
		
		elif algorithm == 'cupid':
			matcher = Cupid(**argument_values)

		elif algorithm == 'distributionbased':
			matcher = DistributionBased(**argument_values)  
		
		elif algorithm == 'jaccarddistance':
			if 'distance_fun' in argument_values:
				distance_fun_name = argument_values['distance_fun'].strip().lower()
				distance_fun = None
				if distance_fun_name == 'levenshtein':
					distance_fun = StringDistanceFunction.Levenshtein
				elif distance_fun_name == 'dameraulevenshtein':
					distance_fun = StringDistanceFunction.DamerauLevenshtein
				elif distance_fun_name == 'hamming':
					distance_fun = StringDistanceFunction.Hamming
				elif distance_fun_name == 'jaro':
					distance_fun = StringDistanceFunction.Jaro
				elif distance_fun_name == 'jarowinkler':
					distance_fun = StringDistanceFunction.JaroWinkler
				elif distance_fun_name == 'exact':
					distance_fun = StringDistanceFunction.Exact
				else:
					raise ValueError(f"Unknown distance function: `{distance_fun_name}`.")
				argument_values['distance_fun'] = distance_fun
			matcher = JaccardDistanceMatcher(**argument_values)

		elif algorithm == 'similarityflooding':
			matcher = SimilarityFlooding(**argument_values)

		else:
			raise ValueError(f"Unknown algorithm `{algorithm}`.")
		
		yield argument_values, matcher
		
def get_first_matcher(algorithm_name, argument_grid_strs):
	_, matcher = next(get_matchers(algorithm_name, argument_grid_strs))
	return matcher

def valentine_match_grid_search(algorithm, argument_grid_strs, source_df, target_df, ground_truth):
	result = ResultAggregator()

	for arguments, matcher in get_matchers(algorithm, argument_grid_strs):
		matches = valentine_match(source_df, target_df, matcher)
		metrics = matches.get_metrics(ground_truth)
		result.update(arguments, matches, metrics)
	
	return result

def valentine_match_once(algorithm, argument_grid_strs, source_df, target_df, ground_truth = None):
	result = ResultAggregator()

	arguments, matcher = next(iter(get_matchers(algorithm, argument_grid_strs)), (None, None))
	if matcher:
		matches = valentine_match(source_df, target_df, matcher)
		metrics = matches.get_metrics(ground_truth) if ground_truth else None
		result.update(arguments, matches, metrics)
	
	return result

def prepare_source_target_names(source_name, target_name):
	if source_name == target_name:
		source_name += "_s"
		target_name += "_t"
	return source_name, target_name

def prefix_source_target_names(matching_dict, src_prefix, trg_prefix):
	for key in list(matching_dict.keys()):
		first_tuple, second_tuple = key
		updated_first_tuple = (first_tuple[0], f"{src_prefix}{first_tuple[1]}")
		updated_second_tuple = (second_tuple[0], f"{trg_prefix}{second_tuple[1]}")
		new_key = (updated_first_tuple, updated_second_tuple)
		matching_dict[new_key] = matching_dict.pop(key)

def instanciate_results(matching_dict):
	return MatcherResults(matching_dict)