from sqlalchemy import Boolean, Column, String, ForeignKey, Text, Float, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()

def generate_uuid():
	return str(uuid.uuid4())

class Algorithm(Base):
	__tablename__ = 'algorithm'

	id = Column(String(36), primary_key=True, default=generate_uuid)
	name = Column(String(50), nullable=False)
	parameters = Column(String(710), nullable=False)

	__table_args__ = (
		UniqueConstraint('name', 'parameters', name='_name_parameters_uc'),
	)

class Dataset(Base):
	__tablename__ = 'dataset'

	id = Column(String(36), primary_key=True, default=generate_uuid)
	name = Column(String(1000), unique=True, nullable=False)
	ground_truth_size = Column(Integer, nullable=False)
	source_column_count = Column(Integer, nullable=False)
	target_column_count = Column(Integer, nullable=False)
	matching_type = Column(String(50), nullable=False)

	def __repr__(self):
		return f"<Dataset(name={self.name})>"

class Matching(Base):
	__tablename__ = 'matching'

	id = Column(String(36), primary_key=True, default=generate_uuid)
	algorithm_id = Column(String(36), ForeignKey('algorithm.id'), nullable=False)
	dataset_id = Column(String(36), ForeignKey('dataset.id'), nullable=False)
	matchings = Column(Text, nullable=True)
	matchings_lev = Column(Text, nullable=True)
	len_matchings = Column(Integer, nullable=True)
	time_matchings = Column(Float, nullable=True)
	hash_matchings = Column(Text, nullable=True)
	hash_matchings_lev = Column(Text, nullable=True)
	precision = Column(Float, nullable=True)
	recall = Column(Float, nullable=True)
	f1score = Column(Float, nullable=True)
	precision_top_10_percent = Column(Float, nullable=True)
	recall_ground_truth_size = Column(Float, nullable=True)
	flip_input_matchings = Column(Text, nullable=True)
	flip_input_matchings_lev = Column(Text, nullable=True)
	len_flip_input_matchings = Column(Integer, nullable=True)
	time_flip_input_matchings = Column(Float, nullable=True)
	hash_flip_input_matchings = Column(Text, nullable=True)
	hash_flip_input_matchings_lev = Column(Text, nullable=True)
	is_symmetric = Column(Boolean, nullable=True)
	is_balanced = Column(Boolean, nullable=True)
	is_complete = Column(Boolean, nullable=True)
	has_ties = Column(Boolean, nullable=True)
	qubo_formula = Column(Text, nullable=True)
	qubo_number_of_variables = Column(Integer, nullable=True)
	qubo_number_of_linear_terms = Column(Integer, nullable=True)
	qubo_number_of_quadratic_terms = Column(Integer, nullable=True)
	qubo_active_variables = Column(Text, nullable=True)
	qubo_optimal_value = Column(Float, nullable=True)
	qubo_matchings = Column(Text, nullable=True)
	qubo_precision = Column(Float, nullable=True)
	qubo_recall = Column(Float, nullable=True)
	qubo_f1score = Column(Float, nullable=True)
	qubo_precision_top_10_percent = Column(Float, nullable=True)
	qubo_recall_ground_truth_size = Column(Float, nullable=True)
	qaoa_p = Column(Integer, nullable=True)
	qaoa_depth = Column(Integer, nullable=True)
	qaoa_width = Column(Integer, nullable=True)
	qaoa_time_ansatz = Column(Float, nullable=True)
	qaoa_time_transpile = Column(Float, nullable=True)
	qaoa_shots = Column(Integer, nullable=True)
	qaoa_active_variables = Column(Text, nullable=True)
	qaoa_optimal_value = Column(Float, nullable=True)
	qaoa_matchings = Column(Text, nullable=True)
	qaoa_precision = Column(Float, nullable=True)
	qaoa_recall = Column(Float, nullable=True)
	qaoa_f1score = Column(Float, nullable=True)
	qaoa_precision_top_10_percent = Column(Float, nullable=True)
	qaoa_recall_ground_truth_size = Column(Float, nullable=True)
	algorithm = relationship("Algorithm", back_populates="matchings")
	dataset = relationship("Dataset", back_populates="matchings")
	__table_args__ = (
		UniqueConstraint('algorithm_id', 'dataset_id', name='_algorithm_dataset_uc'),
	)

class UqSummary(Base):
	__tablename__ = 'uq_summary'
	
	id = Column(Integer, primary_key=True)
	algorithm_id = Column(String(36), nullable=True)
	dataset_id = Column(String(36), nullable=True)
	is_symmetric = Column(Boolean, nullable=True)
	is_balanced = Column(Boolean, nullable=True)
	is_complete = Column(Boolean, nullable=True)
	has_ties = Column(Boolean, nullable=True)
	
Algorithm.matchings = relationship("Matching", back_populates="algorithm")
Dataset.matchings = relationship("Matching", back_populates="dataset")