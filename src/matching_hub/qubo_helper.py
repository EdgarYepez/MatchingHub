from math import e
import os
import numpy as np
import pandas as pd
from .helper import *
import re

from .quantum_love import database_side
from .quantum_love import docplex_quantum_side

from qiskit_optimization import QuadraticProgram
from qiskit_optimization.translators import from_docplex_mp, to_docplex_mp
from qiskit_optimization.converters import QuadraticProgramToQubo

from qiskit_aer import AerSimulator

from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit.circuit.library import QAOAAnsatz
from qiskit import ClassicalRegister, QuantumCircuit, transpile

def formulate_as_qubo(matching, source_elements, target_elements):
	source_df = pd.DataFrame(columns=source_elements)
	target_df = pd.DataFrame(columns=target_elements)
	
	pairs, suitors, reviewers = database_side.get_pairs_and_men_and_women_with_preferences(matching, source_df, target_df)
	
	docplex_model = docplex_quantum_side.setup_docplex_model(pairs, None)
	
	quadratic_program = from_docplex_mp(docplex_model)
	qubo = QuadraticProgramToQubo().convert(quadratic_program)

	return qubo

def get_docplex_model(qubo):
	return to_docplex_mp(qubo)

def get_qaoa_cicuit(qubo, p, simulator = None):
	qubo_converter = QuadraticProgramToQubo()
	problem_op, offset = qubo_converter.convert(qubo).to_ising()

	qaoa_ansatz, time_ansatz = timer(lambda: QAOAAnsatz(problem_op, reps=p))

	if simulator is not None:
		parameter_values = {param: np.random.uniform(0, np.pi) for param in qaoa_ansatz.parameters}
		qaoa_ansatz = qaoa_ansatz.assign_parameters(parameter_values)

	if simulator is not None:
		transpiled_circuit, time_transpile = timer(lambda: transpile(qaoa_ansatz, simulator))
		
	else:
		transpiled_circuit, time_transpile = timer(lambda: transpile(qaoa_ansatz, basis_gates=['cx', 'u3', 'rx', 'rz']))

	transpiled_depth = transpiled_circuit.depth()
	transpiled_width = transpiled_circuit.width()

	return transpiled_circuit, transpiled_depth, transpiled_width, time_ansatz, time_transpile

def run_qaoa_cicuit(qubo, p, shots):
	simulator = AerSimulator()
	transpiled_circuit, transpiled_depth, transpiled_width, time_ansatz, time_transpile = get_qaoa_cicuit(qubo, p, simulator)

	num_qubits = transpiled_circuit.num_qubits
	classical_reg = ClassicalRegister(num_qubits)
	qaoa_measured_circuit = QuantumCircuit(transpiled_circuit.qubits, classical_reg)
	qaoa_measured_circuit.compose(transpiled_circuit, inplace=True)
	qaoa_measured_circuit.measure(range(num_qubits), range(num_qubits))

	sim_result = simulator.run(qaoa_measured_circuit, shots=shots).result()
	counts = sim_result.get_counts()

	most_observed_bitstring = max(counts, key=counts.get)

	variables = qubo.variables
	active_variables = [variables[index].name for index, bit in enumerate(most_observed_bitstring[::-1]) if bit == '1']

	objective_value = qubo.objective.evaluate([int(bit) for bit in most_observed_bitstring[::-1]])

	return active_variables, objective_value

def interpret_qubo_variables_as_matching(qubo_variables, source_name, target_name):
	matchings = {}
	for v in qubo_variables:
		m = re.search(r'src__(.*?)_trg__(.*)$', v)
		if m:
			source_element = m.group(1)
			target_element = m.group(2)
			matchings[((source_name, source_element), (target_name, target_element))] = 1
		else:
			pass
	return matchings
