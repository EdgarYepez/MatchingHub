from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from .models import Base

def sqlite_engine_builder(db_name):
	return lambda: create_engine(f'sqlite:///{db_name}')

def init_db(engine_builder):
	engine = engine_builder()
	Base.metadata.create_all(engine)
	__create_summary_view(engine)
	__drop_uq_summary_table(engine)
	__create_uq_summary_view(engine)
	return engine

def get_session(engine):
	Session = sessionmaker(bind=engine)
	return Session()

def __drop_uq_summary_table(engine):
	inspector = inspect(engine)
	views = inspector.get_view_names()
	if 'uq_summary' not in views:
		sql = """
			DROP TABLE IF EXISTS uq_summary;
		"""
		with engine.connect() as connection:
			connection.execute(text(sql))

def __create_uq_summary_view(engine):
	create_view_sql = """
		CREATE VIEW IF NOT EXISTS uq_summary AS
			SELECT *
			FROM (
				SELECT *, ROW_NUMBER() OVER (PARTITION BY hash_matchings_lev, hash_flip_input_matchings_lev ORDER BY len_matchings DESC) AS row_num
				FROM summary
				WHERE len_matchings > 0 and len_flip_input_matchings > 0
			)
			WHERE row_num = 1
	"""
	with engine.connect() as connection:
		connection.execute(text(create_view_sql))

def __create_summary_view(engine):
	create_view_sql = """
		CREATE VIEW IF NOT EXISTS summary AS
			SELECT 
				m.id,
				m.dataset_id,
				ds.name,
				ds.source_column_count,
				ds.target_column_count,
				ds.ground_truth_size,
				ds.matching_type,
				m.algorithm_id,
				alg.name AS alg_name,
				alg.parameters,
				m.len_matchings,
				m.time_matchings,
				m.hash_matchings,
				m.hash_matchings_lev,
				m.precision,
				m.recall,
				m.f1score,
				m.precision_top_10_percent,
				m.recall_ground_truth_size,
				m.len_flip_input_matchings,
				m.time_flip_input_matchings,
				m.hash_flip_input_matchings,
				m.hash_flip_input_matchings_lev,
				m.is_balanced,
				m.is_complete,
				m.is_symmetric,
				m.has_ties,
				m.qubo_formula,
				m.qubo_number_of_variables,
				m.qubo_number_of_linear_terms,
				m.qubo_number_of_quadratic_terms,
				m.qubo_active_variables,
				m.qubo_optimal_value,
				m.qubo_precision,
				m.qubo_recall,
				m.qubo_f1score,
				m.qubo_precision_top_10_percent,
				m.qubo_recall_ground_truth_size,
				m.qaoa_p,
				m.qaoa_depth,
				m.qaoa_width,
				m.qaoa_time_ansatz,
				m.qaoa_time_transpile,
				m.qaoa_shots,
				m.qaoa_active_variables,
				m.qaoa_optimal_value,
				m.qaoa_precision,
				m.qaoa_recall,
				m.qaoa_f1score,
				m.qaoa_precision_top_10_percent,
				m.qaoa_recall_ground_truth_size
			FROM dataset AS ds
			INNER JOIN matching AS m ON m.dataset_id = ds.id
			INNER JOIN algorithm AS alg ON m.algorithm_id = alg.id;
	"""
	with engine.connect() as connection:
		connection.execute(text(create_view_sql))