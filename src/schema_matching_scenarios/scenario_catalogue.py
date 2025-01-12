import inspect
import sys
import os
import pandas as pd
import json
import re
from pathlib import Path
	
class Scenario:
	
	def __init__(self, source_df, target_df, ground_truth):
		self.name = None
		self.source_df = source_df
		self.target_df = target_df
		self.source_name = None
		self.target_name = None
		self.ground_truth = ground_truth
		
	def ground_truth_as_tuples(self):
		return [(match['source_column'], match['target_column']) for match in self.ground_truth['matches']]
	
	def get_stats(self):
		return Scenario.Stats(self)
		
	class Stats:
		
		def __init__(self, scenario):
			self.matching_type = self.__class__.__compute_matching_type(scenario.ground_truth)
			self.ground_truth_size = len(scenario.ground_truth['matches'])
			self.source_column_count = scenario.source_df.shape[1]
			self.target_column_count = scenario.target_df.shape[1]
		
		@classmethod
		def __compute_matching_type(cls, ground_truth):
			def __is_one_to_n(left_getter, right_getter):
				left = {}
				for m in ground_truth['matches']:
					if not m[left_getter] in left:
						left[m[left_getter]] = []
					left[m[left_getter]].append(m)
					if (len(left[m[left_getter]]) > 1):
						right = set()
						for l in left[m[left_getter]]:
							right.add(l[right_getter])
						if (len(right) > 1):
							return True
				return False
			is_one_to_n = __is_one_to_n("source_column", "target_column")
			is_n_to_one = __is_one_to_n("target_column", "source_column")
			if is_one_to_n and is_n_to_one: return "n:n"
			if is_one_to_n: return "1:n"
			if is_n_to_one: return "n:1"
			return "1:1"

class _ScenarioLoader:

	class Helper:
		
		@classmethod
		def data_set_directory(cls):
			return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_sets")			

		@classmethod
		def load_json(cls, file_path):
			with open(file_path, 'r') as file:
				data = json.load(file)
				return data
	
		@classmethod
		def load_csv(cls, file_path, has_headers=True, load_data=True):
			try:
				header = 0 if has_headers else None
				nrows = None if load_data else 0
				df = pd.read_csv(file_path, header=header, nrows=nrows, encoding="utf-8")
				return df
			except Exception as e:
				print(f"Failed to load data from CSV file. Error: {e}")
				sys.exit(1)
		
		@classmethod
		def get_directories(cls, directory_path):
			return (d.name for d in Path(directory_path).iterdir() if d.is_dir())
		
		@classmethod
		def get_files(cls, directory_path, extension=None):
			return (
				f.name for f in Path(directory_path).iterdir()
				if f.is_file() and (extension is None or f.suffix.lower() == extension.lower())
			)

		@classmethod
		def contains_subdirectories(cls, directory_path, *subdirs):
			expected_subdirs = set(subdirs)
			actual_subdirs = list(cls.get_directories(directory_path))
			return expected_subdirs.issubset(actual_subdirs)
	
		@classmethod
		def contains_files(cls, directory_path, *files):
			expected_files = set(files)
			actual_files = list(cls.get_files(directory_path))
			return expected_files.issubset(actual_files)
	
	def __init__(self):
		self.data_dir = None
		self.source_table_name = None
		self.target_table_name = None

	def _transform_matches(ground_truth_matrix, source_table_name, source_headers, target_table_name, target_headers):
		matches = []
	
		for i, row in ground_truth_matrix.iterrows():
			for j, value in row.items():
				if value == 1:
					match = {
						"source_table": source_table_name,
						"source_column": source_headers[i],
						"target_table": target_table_name,
						"target_column": target_headers[j]
					}
					matches.append(match)

		return {"matches": matches}
	
class _Schematch(_ScenarioLoader):
	
	@classmethod
	def __load(cls, data_dir, source_table_name, target_table_name, load_data):
		source_df = cls.Helper.load_csv(os.path.join(data_dir, f"source/{source_table_name}.csv"), load_data=load_data)
		source_headers = source_df.columns.tolist()
	
		target_df = cls.Helper.load_csv(os.path.join(data_dir, f"target/{target_table_name}.csv"), load_data=load_data)
		target_headers = target_df.columns.tolist()
	
		ground_truth = cls.Helper.load_csv(os.path.join(data_dir, f"ground_truth/{source_table_name}___{target_table_name}.csv"), False)

		matches = cls._transform_matches(ground_truth, source_table_name, source_headers, target_table_name, target_headers)

		return Scenario(source_df, target_df, matches)
	
	@classmethod
	def load(cls, scenario_name, load_data=True):
		m = re.match(r'([^\/]+)\/([^\/]+)\/(.*?)>>(.*)$', scenario_name)
		group1 = m.group(1)
		group2 = m.group(2)
		source_table_name = m.group(3)
		target_table_name = m.group(4)
		data_dir = os.path.join(cls.Helper.data_set_directory(), "schematch", group1, group2)
		ret = cls.__load(data_dir, source_table_name, target_table_name, load_data)
		ret.name = f'{cls.__name__}/{scenario_name}'
		ret.source_name = source_table_name
		ret.target_name = target_table_name
		return ret
	
	@classmethod
	def scenario_names(cls):
		data_dir_root = os.path.join(cls.Helper.data_set_directory(), "schematch")
		for group1 in cls.Helper.get_directories(data_dir_root):
			for group2 in cls.Helper.get_directories(os.path.join(data_dir_root, group1)):
				data_dir = os.path.join(data_dir_root, group1, group2)
				if cls.Helper.contains_subdirectories(data_dir, 'ground_truth', 'source', 'target'):
					data_dir = os.path.join(data_dir, 'ground_truth')
					for f in cls.Helper.get_files(data_dir, '.csv'):
						m = re.match(r'^(.+?)___(.+?)\.csv$', f, re.IGNORECASE)
						if m:
							source_table_name = m.group(1)
							target_table_name = m.group(2)
							yield f"{cls.__name__}/{group1}/{group2}/{source_table_name}>>{target_table_name}"		

class _Valentine(_ScenarioLoader):
	
	@classmethod
	def load(cls, scenario_name, load_data=True):
		m = re.match(r'([^\/]+)\/([^\/]+)\/([^\/]+)\/(.*?)>>(.*)$', scenario_name)		
		group1 = m.group(1)
		group2 = m.group(2)
		group3 = m.group(3)
		root_table_name = group3.lower()		
		data_dir = os.path.join(cls.Helper.data_set_directory(), "valentine", group1, group2, group3)	
		source_df = cls.Helper.load_csv(os.path.join(data_dir, f'{root_table_name}_source.csv'), load_data=load_data)
		target_df = cls.Helper.load_csv(os.path.join(data_dir, f'{root_table_name}_target.csv'), load_data=load_data)
		ground_truth = cls.Helper.load_json(os.path.join(data_dir, f'{root_table_name}_mapping.json'))
		ret = Scenario(source_df, target_df, ground_truth)
		ret.name = f'{cls.__name__}/{scenario_name}'
		ret.source_name = "source"
		ret.target_name = "target"
		return ret
	
	@classmethod
	def scenario_names(cls):
		data_dir_root = os.path.join(cls.Helper.data_set_directory(), "valentine")
		for group1 in cls.Helper.get_directories(data_dir_root):
			for group2 in cls.Helper.get_directories(os.path.join(data_dir_root, group1)):
				for group3 in cls.Helper.get_directories(os.path.join(data_dir_root, group1, group2)):
					data_dir = os.path.join(data_dir_root, group1, group2, group3)
					root_table_name = group3.lower()
					source_path = f'{root_table_name}_source.csv'
					target_path = f'{root_table_name}_target.csv'
					ground_truth_path = f'{root_table_name}_mapping.json'
					if cls.Helper.contains_files(data_dir, source_path, target_path, ground_truth_path):
						yield f"{cls.__name__}/{group1}/{group2}/{group3}/source>>target"
								
def __scenario_loaders(expected_name=None):
	def find_classes(namespace):
		for name, obj in list(namespace.items()):
			if inspect.isclass(obj) and issubclass(obj, _ScenarioLoader) and obj is not _ScenarioLoader:
				if expected_name is None or expected_name == name:
					yield obj
			if inspect.isclass(obj):
				yield from find_classes(vars(obj))
	yield from find_classes(globals())

def scenario_names():
	yield from (name for loader in __scenario_loaders() for name in loader.scenario_names())

def load_scenario(scenario_name, load_data=True):
	m = re.match(r'^([^\/]+)\/(.+?)$', scenario_name)
	if m:
		scenario_loader_name = m.group(1)
		scenario_name = m.group(2)
		scenario_loader = next(__scenario_loaders(scenario_loader_name), None)
		if scenario_loader:
			return scenario_loader.load(scenario_name, load_data)
		
def get_source_target_names(scenario_name):
	scenario_name = re.sub(r"(?:[^\/]+/)+", "", scenario_name)
	parts = scenario_name.split(">>")
	if scenario_name is None:
		return None, None
	parts = scenario_name.split(">>")
	source_name = parts[0] if len(parts) > 0 else None
	target_name = parts[1] if len(parts) > 1 else None	
	return source_name, target_name