from sqlalchemy import distinct, text, and_
from sqlalchemy.exc import IntegrityError
from .db_setup import init_db, get_session, sqlite_engine_builder
from .helper import *
from .models import Algorithm, Dataset, Matching, UqSummary
from functools import wraps
from sqlalchemy.exc import OperationalError
import time
from filelock import FileLock

class MatchingSession:
	
	def __init__(self, session_file, notification_fallback):
		engine_builder = sqlite_engine_builder(session_file)
		self.session_file = session_file
		self.__session = get_session(init_db(engine_builder))
		self.__notification_fallback = notification_fallback
		self.__lock = FileLock(f"{session_file}.lock")

	@staticmethod
	def retry_commit(delay=1):
		def decorator(func):
			@wraps(func)
			def wrapper(*args, **kwargs):
				self = args[0]
				session = self.__session
				result = func(*args, **kwargs)

				with self.__lock:
					while True:
						try:
							session.commit()
							return result
						except OperationalError as e:
							if "database is locked" in str(e):
								time.sleep(delay)
							else:
								raise
			return wrapper
		return decorator

	def __warn(self, message):
		if self.__notification_fallback:
			self.__notification_fallback(message)
		
	def __error(self, message):
		if self.__notification_fallback:
			self.__notification_fallback(message)
			
	def __query_uq_summary(self, criteria=None, range_tuple=None):
		query = self.__session.query(UqSummary.id, UqSummary.algorithm_id, UqSummary.dataset_id)
		
		if range_tuple is not None:
			start, end = range_tuple
			if start is not None or end is not None:
				if start < 0 or end < 0:
					raise ValueError("start and end must be non-negative integers.")
		
				if end < start:
					raise ValueError("end must be greater than or equal to start.")
				
				query = query.offset(start).limit(end - start + 1)
				
		if criteria == "ilt":
			query = query.filter(and_(UqSummary.is_complete == 0, UqSummary.has_ties == 1))
		elif criteria == "ilto":
			query = query.filter(and_(UqSummary.is_complete == 0, UqSummary.has_ties == 0))
		elif criteria == "clto":
			query = query.filter(and_(UqSummary.is_complete == 1, UqSummary.has_ties == 0))
		elif criteria == "clt":
			query = query.filter(and_(UqSummary.is_complete == 1, UqSummary.has_ties == 1))
		elif criteria is None or criteria.strip() == "":
			pass
		else:
			self.__error(f"Unknown filter condition '{criteria}'.")
			return

		matching_ids = set()
		algorithm_ids = set()
		dataset_ids = set()

		batch_size = 1
		for result in query.yield_per(batch_size):
			matching_ids.add(result.id)
			algorithm_ids.add(result.algorithm_id)
			dataset_ids.add(result.dataset_id)

		return matching_ids, algorithm_ids, dataset_ids

	def get_scenario(self, dataset_name):
		return self.__session.query(Dataset).filter_by(name=dataset_name).first()
	
	def get_all_scenarios(self):
		return self.__session.query(Dataset).all()
	
	def select_scenarios(self, scenario_names):
		selected_scenarios = []
		if scenario_names:
			for scenario_name in scenario_names:
				scenario = self.get_scenario(scenario_name)
				if scenario is None:
					self.__error(f"Error: No scenario '{scenario_name}' loaded into the current session.")
					return
				selected_scenarios.append(scenario)
		else:
			selected_scenarios.extend(self.get_all_scenarios())
		return selected_scenarios
		
	def upload_scenario(self, scenario, stats, override):
		existing_dataset = self.get_scenario(scenario.name)
		if existing_dataset:
			if override:
				self.__session.delete(existing_dataset)
				self.__session.commit()
			else:
				self.__warn(f"{scenario.name} already exists. Skipping.")
				return False
	
		stats = scenario.get_stats()
		dataset = Dataset(
			name=scenario.name,
			ground_truth_size=stats.ground_truth_size,
			source_column_count=stats.source_column_count,
			target_column_count=stats.target_column_count,
			matching_type=stats.matching_type
		)
		self.__session.add(dataset)
		self.__session.commit()
		
		return True

	def get_algorithm_names(self):
		result = self.__session.query(distinct(Algorithm.name)).all()
		return [row[0] for row in result]

	def get_all_algorithms_of(self, algorithm_name):
		return self.__session.query(Algorithm).filter_by(name=algorithm_name).all()

	def get_all_algorithms(self):
		return self.__session.query(Algorithm).all()
	
	def get_single_algorithm(self, algorithm_name, parameters):
		return self.__session.query(Algorithm).filter_by(name=algorithm_name, parameters=parameters).first()
	
	def select_algorithms(self, algorithm_name, parameter_ids):
		selected_algorithms = []
		if algorithm_name:
			selected_algorithms.extend(self.get_all_algorithms_of(algorithm_name))
			if parameter_ids:
				algo_dict = {str(idx + 1): algo for idx, algo in enumerate(selected_algorithms)}
				temp_list = list(parameter_ids)
				for t_id in range(len(temp_list)):
					idx = temp_list[t_id].strip()
					temp_list[t_id] = algo_dict.pop(idx, None)
				selected_algorithms = [algo for algo in temp_list if algo is not None]
		elif parameter_ids is not None:
			self.__error("Error: Provide an algorithm name with the --algorithm option when using the --parameter option.")
			return
		else:
			selected_algorithms.extend(self.get_all_algorithms())			
		return selected_algorithms

	def upload_algorithm(self, algorithm_name, parameters, override):
		existing_algorithm = self.get_single_algorithm(algorithm_name, parameters)
		if existing_algorithm:
			if override:
				self.__session.delete(existing_algorithm)
				self.__session.commit()
			else:
				self.__warn(f"Algorithm '{algorithm_name}' already exists. Skipping.")
				return False
		algorithm = Algorithm(name=algorithm_name, parameters=parameters)
		self.__session.add(algorithm)
		self.__session.commit()
		return True

	def get_all_matchings_order_by_qubo_size(self):
		query = (
			self.__session.query(Matching)
			.filter(
				Matching.qubo_number_of_linear_terms.isnot(None),
				Matching.qubo_number_of_quadratic_terms.isnot(None)
			)
			.order_by(
				(Matching.qubo_number_of_linear_terms + Matching.qubo_number_of_quadratic_terms).asc()
			)
		)
		batch_size = 1
		return query.yield_per(batch_size)

	def get_all_matchings(self, range_tuple=None):
		query = self.__session.query(Matching)
		
		if range_tuple is not None:
			start, end = range_tuple
			if start is not None or end is not None:
				if start < 0 or end < 0:
					raise ValueError("start and end must be non-negative integers.")
		
				if end < start:
					raise ValueError("end must be greater than or equal to start.")
				
				query = query.offset(start).limit(end - start + 1)
	
		batch_size = 1
		return query.yield_per(batch_size)

	def get_matching(self, algorithm_id, dataset_id):
		return self.__session.query(Matching).filter_by(algorithm_id=algorithm_id, dataset_id=dataset_id).first()

	def get_matching_by_id(self, matching_id):
		return self.__session.query(Matching).filter_by(id=matching_id).first()

	@retry_commit(delay=2)
	def upload_matching(self, algorithm, dataset, matchings, time, metrics, override):
		existing_matching = self.get_matching(algorithm.id, dataset.id)
		if existing_matching is None:
			matching = Matching(
				algorithm=algorithm,
				dataset=dataset,
				matchings=dict_with_tuples_to_json(matchings),
				len_matchings=len(matchings),
				time_matchings=time,
				precision=metrics["Precision"],
				recall=metrics["Recall"],
				f1score=metrics["F1Score"],
				precision_top_10_percent=metrics["PrecisionTop10Percent"],
				recall_ground_truth_size=metrics["RecallAtSizeofGroundTruth"]
			)
			self.__session.add(matching)
		else:
			if override or existing_matching.matchings is None:
				existing_matching.matchings = dict_with_tuples_to_json(matchings)
				existing_matching.len_matchings = len(matchings)
				existing_matching.time_matchings = time
				existing_matching.precision = metrics["Precision"]
				existing_matching.recall = metrics["Recall"]
				existing_matching.f1score = metrics["F1Score"]
				existing_matching.precision_top_10_percent = metrics["PrecisionTop10Percent"]
				existing_matching.recall_ground_truth_size = metrics["RecallAtSizeofGroundTruth"]

	@retry_commit(delay=2)
	def upload_flipped_matching(self, algorithm, dataset, matchings, time, override):
		existing_matching = self.get_matching(algorithm.id, dataset.id)
		if existing_matching is None:
			matching = Matching(
				algorithm=algorithm,
				dataset=dataset,
				flip_input_matchings=dict_with_tuples_to_json(matchings),
				len_flip_input_matchings = len(matchings),
				time_flip_input_matchings = time
			)
			self.__session.add(matching)
		else:
			if override or existing_matching.flip_input_matchings is None:
				existing_matching.flip_input_matchings = dict_with_tuples_to_json(matchings)
				existing_matching.len_flip_input_matchings = len(matchings)
				existing_matching.time_flip_input_matchings = time
				
	@retry_commit(delay=2)
	def upload_matching_as_preferences(self, matching_id, matchings):
		matching = self.get_matching_by_id(matching_id)		
		matching.matchings_lev = dict_with_tuples_to_json(matchings)

	@retry_commit(delay=2)
	def upload_flipped_matching_as_preferences(self, matching_id, matchings):
		matching = self.get_matching_by_id(matching_id)		
		matching.flip_input_matchings_lev = dict_with_tuples_to_json(matchings)

	@retry_commit(delay=2)
	def upload_matching_hash(self, matching_id, hash_value):
		matching = self.get_matching_by_id(matching_id)
		matching.hash_matchings = hash_value
		
	@retry_commit(delay=2)
	def upload_flipped_matching_hash(self, matching_id, hash_value):
		matching = self.get_matching_by_id(matching_id)
		matching.hash_flip_input_matchings = hash_value
			
	@retry_commit(delay=2)
	def upload_matching_as_preferences_hash(self, matching_id, hash_value):
		matching = self.get_matching_by_id(matching_id)
		matching.hash_matchings_lev = hash_value
			
	@retry_commit(delay=2)
	def upload_flipped_matching_as_preferences_hash(self, matching_id, hash_value):
		matching = self.get_matching_by_id(matching_id)
		matching.hash_flip_input_matchings_lev = hash_value
			
	@retry_commit(delay=2)
	def upload_features(self, matching_id, is_symmetric, is_complete, has_ties, is_balanced):
		matching = self.get_matching_by_id(matching_id)
		matching.is_symmetric = is_symmetric
		matching.is_complete = is_complete
		matching.has_ties = has_ties
		matching.is_balanced = is_balanced

	def get_matching_class_count(self):
		sql = """
			SELECT
				COUNT(CASE WHEN is_complete = 0 AND has_ties = 0 THEN 1 END) AS ilto,
				COUNT(CASE WHEN is_complete = 0 AND has_ties = 1 THEN 1 END) AS ilt,
				COUNT(CASE WHEN is_complete = 1 AND has_ties = 0 THEN 1 END) AS clto,
				COUNT(CASE WHEN is_complete = 1 AND has_ties = 1 THEN 1 END) AS clt
			FROM uq_summary;
		"""
		result = self.__session.execute(text(sql))
		row = result.fetchone()
		return dict(row._mapping)

	def export_representative_matchings(self, bkp_session, criteria, range_tuple):
		matching_ids, algorithm_ids, scenario_ids = self.__query_uq_summary(criteria, range_tuple)
		src = self.__session
		trg = bkp_session.__session
	
		try:
			scenarios = src.query(Dataset).filter(Dataset.id.in_(scenario_ids)).all()
			for scenario in scenarios:
				exists = trg.query(Dataset).filter_by(id=scenario.id).first()
				if not exists:
					detached_scenario = Dataset(**{col.name: getattr(scenario, col.name) for col in Dataset.__table__.columns})
					trg.add(detached_scenario)

			algorithms = src.query(Algorithm).filter(Algorithm.id.in_(algorithm_ids)).all()
			for algorithm in algorithms:
				exists = trg.query(Algorithm).filter_by(id=algorithm.id).first()
				if not exists:
					detached_algorithm = Algorithm(**{col.name: getattr(algorithm, col.name) for col in Algorithm.__table__.columns})
					trg.add(detached_algorithm)

			matchings = src.query(Matching).filter(Matching.id.in_(matching_ids)).yield_per(1)
			for matching in matchings:
				exists = trg.query(Matching).filter_by(id=matching.id).first()
				if not exists:
					detached_matching = Matching(**{col.name: getattr(matching, col.name) for col in Matching.__table__.columns})
					trg.add(detached_matching)

			trg.commit()

		except IntegrityError as e:
			trg.rollback()
			print(f"Error during migration: {e}")
		finally:
			src.close()
			trg.close()

	@retry_commit(delay=2)
	def upload_qubo_formula(self, matching_id, qubo_formula, number_of_variables, number_of_linear_terms, number_of_quadratic_terms):
		matching = self.get_matching_by_id(matching_id)
		matching.qubo_formula = qubo_formula
		matching.qubo_number_of_variables = number_of_variables
		matching.qubo_number_of_linear_terms = number_of_linear_terms
		matching.qubo_number_of_quadratic_terms = number_of_quadratic_terms
	
	@retry_commit(delay=2)
	def upload_qubo_matchings(self, matching_id, matchings, active_variables, opt_value):
		matching = self.get_matching_by_id(matching_id)
		matching.qubo_matchings = dict_with_tuples_to_json(matchings)
		matching.qubo_active_variables = ",".join(active_variables)
		matching.qubo_optimal_value = opt_value

	@retry_commit(delay=2)
	def upload_qubo_matchings_metrics(self, matching_id, metrics):
		matching = self.get_matching_by_id(matching_id)
		matching.qubo_precision = metrics["Precision"]
		matching.qubo_recall = metrics["Recall"]
		matching.qubo_f1score = metrics["F1Score"]
		matching.qubo_precision_top_10_percent = metrics["PrecisionTop10Percent"]
		matching.qubo_recall_ground_truth_size = metrics["RecallAtSizeofGroundTruth"]

	@retry_commit(delay=2)
	def upload_qaoa_circuit_metadata(self, matching_id, p, depth, width, time_ansatz, time_transpile):
		matching = self.get_matching_by_id(matching_id)
		matching.qaoa_p = p
		matching.qaoa_depth = depth
		matching.qaoa_width = width
		matching.qaoa_time_ansatz = time_ansatz
		matching.qaoa_time_transpile = time_transpile
	
	@retry_commit(delay=2)
	def upload_qaoa_matchings(self, matching_id, shots, matchings, active_variables, opt_value):
		matching = self.get_matching_by_id(matching_id)
		matching.qaoa_shots = shots
		matching.qaoa_matchings = dict_with_tuples_to_json(matchings)
		matching.qaoa_active_variables = ",".join(active_variables)
		matching.qaoa_optimal_value = opt_value

	@retry_commit(delay=2)
	def upload_qaoa_matchings_metrics(self, matching_id, metrics):
		matching = self.get_matching_by_id(matching_id)
		matching.qaoa_precision = metrics["Precision"]
		matching.qaoa_recall = metrics["Recall"]
		matching.qaoa_f1score = metrics["F1Score"]
		matching.qaoa_precision_top_10_percent = metrics["PrecisionTop10Percent"]
		matching.qaoa_recall_ground_truth_size = metrics["RecallAtSizeofGroundTruth"]

