#!/usr/bin/env python3

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, Annotated, List
import os
import glob
import configparser
from matching_hub.repository import MatchingSession
from matching_hub.helper import *
from matching_hub.valentine_helper import *
from matching_hub.stable_marriage_helper import *
from matching_hub.qubo_helper import *
from plotting import qubo_dist, qubo_histogram, qubo_qaoa_dist, qaoa_dist, qaoa_histogram, recall_stats, data_dist, data_dist_3d, match_dist

from schema_matching_scenarios import load_scenario, scenario_names, get_source_target_names

console = Console()
app = typer.Typer()
session_file_arg_spec = typer.Option(None, "-s", help="Path to the session file.")
plot_output_file_arg_spec = typer.Argument(
	None,
	help=(
		"Path to the output file for the plot including the file extension. "
		"If not set, the plot is displayed on the screen. "
		"Supported extensions are: eps, jpg, pdf, png, svg, and tiff. "
		"If no extension is specified, it defaults to pdf."
	)
)
session_extension = "mt"
session_name_default = f"matching.{session_extension}"
precision = 7
cancelation_token = CancelationToken.get_token()

def __notification_fallback(message):
	typer.echo(message)

def __get_session(session_file):
	"""
	Helper function to load a session file.
	"""
	if not session_file:
		mt_files = glob.glob(f"*.{session_extension}")
		
		if len(mt_files) == 1:
			session_file = mt_files[0]
		elif len(mt_files) > 1:
			typer.echo("Error: Multiple session files found. Please specify the session explicitly.")
			raise typer.Exit()
		else:
			typer.echo("Error: No session found. Please specify a session name with -s <session_name>.")
			raise typer.Exit()
	
	if not os.path.exists(session_file):
		typer.echo(f"Error: Session '{session_file}' does not exist.")
		raise typer.Exit()

	session = MatchingSession(session_file, __notification_fallback)	
	return session

def __session_folders(session_file, *subfolder_names, validate_only=False):
	"""
	Helper function to build folder paths related to a session file.
	"""
	session_file_path = os.path.abspath(session_file)
	session_folder = os.path.dirname(session_file_path)

	base_folder_name = os.path.splitext(os.path.basename(session_file_path))[0]
	base_folder_path = os.path.join(session_folder, base_folder_name)

	subfolder_paths = [os.path.join(base_folder_path, name) for name in subfolder_names]

	if validate_only:
		if not os.path.exists(base_folder_path):
			raise FileNotFoundError(f"Base folder '{base_folder_path}' does not exist.")
		for path in subfolder_paths:
			if not os.path.exists(path):
				raise FileNotFoundError(f"Subfolder at '{path}' does not exist.")
	else:
		os.makedirs(base_folder_path, exist_ok=True)
		for path in subfolder_paths:
			os.makedirs(path, exist_ok=True)

	return (session_folder, base_folder_path, *subfolder_paths)

@app.command()
def initialise(
	session_file: Annotated[
		Optional[str], 
		typer.Argument(help=f"Path to the session file to initialise. The file should have a '.{session_extension}' extension.")
	] = session_name_default
):
	"""
	Initialise a new session file for schema matching.
	"""
	if os.path.exists(session_file):
		typer.echo(f"Error: Session file '{session_file}' already exists.")
		raise typer.Exit()
	
	session = MatchingSession(session_file, __notification_fallback)	
	typer.echo(session_file)

@app.command()
def list_repo_scenarios(
	table: Annotated[
		bool, 
		typer.Option(
			help=(
				"If set, it displays a table including"
				" - the name of the scenario"
				" - the cardinality of the matching"
				" - the number of columns in the source relation"
				" - the number of columns in the target relation"
				" - the size of the ground truth."
				" If not set, only the names of the scenarios are displayed."
			)
		)
	] = False
):
	"""
	List all available schema matching scenarios in the external repository.
	"""    
	if table:
		tbl = Table("No.", "Name", "Cardinality", "Source Column Count", "Target Column Count", "Ground Truth Size")
		scenarios = (load_scenario(scenario_name, False) for scenario_name in scenario_names())
		i = 1
		for scenario in cancelation_token.watch(scenarios):
			stats = scenario.get_stats()
			tbl.add_row(str(i), scenario.name, str(stats.matching_type), str(stats.source_column_count), str(stats.target_column_count), str(stats.ground_truth_size))
			i += 1
		console.print(tbl)
	else:
		for scenario_name in cancelation_token.watch(scenario_names()):
			console.print(scenario_name)

@app.command()
def import_scenarios(
	scenario_names_file: Annotated[
		str,
		typer.Argument(
			help="Path to the file containing the names of the scenarios to import."
		)
	],
	override: Annotated[
		bool,
		typer.Option(
			help=(
				"If set, existing scenarios in the session file will be overwritten by the imported ones. "
				"If not set, existing scenarios will be skipped."
			)
		)
	] = False,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Import scenario definitions from the external repository into the specified session file.
	Scenario definitions include metadata only and not any actual data.
	"""
	session = __get_session(session_file)
	available_scenarios = set(scenario_names())
	loaded_scenario_count = 0
	try:
		with open(scenario_names_file, "r") as file:
			for line in cancelation_token.watch(file):
				scenario_name = line.strip()
				if scenario_name not in available_scenarios:
					typer.echo(f"Error: Scenario '{scenario_name}' not found in the repository.")
					raise typer.Exit()
				scenario = load_scenario(scenario_name, False)
				stats = scenario.get_stats()
				if session.upload_scenario(scenario, stats, override):
					loaded_scenario_count += 1

	except FileNotFoundError:
		typer.echo(f"Error: File '{scenario_names_file}' not found.")
		raise typer.Exit()

	finally:
		typer.echo(f"Imported {loaded_scenario_count} scenarios.")

@app.command()
def list_scenarios(
	table: Annotated[
		bool, 
		typer.Option(
			help=(
				"If set, it displays a table including"
				" - the name of the scenario"
				" - the cardinality of the matching"
				" - the number of columns in the source relation"
				" - the number of columns in the target relation"
				" - the size of the ground truth."
				" If not set, only the names of the scenarios are displayed."
			)
		)
	] = False,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	List all schema matching scenarios currently imported into the specified session file.
	"""
	session = __get_session(session_file)
	db_scenarios = session.get_all_scenarios()
	if table:
		tbl = Table("No.", "Name", "Cardinality", "Source Column Count", "Target Column Count", "Ground Truth Size")
		i = 1
		for db_scenario in cancelation_token.watch(db_scenarios):
			tbl.add_row(str(i), db_scenario.name, str(db_scenario.matching_type), str(db_scenario.source_column_count), str(db_scenario.target_column_count), str(db_scenario.ground_truth_size))
			i += 1
		console.print(tbl)
	else:
		for db_scenario in cancelation_token.watch(db_scenarios):
			console.print(db_scenario.name)

@app.command()
def plot_scenario_dist(
	plot_3d: Annotated[
		bool,
		typer.Option(
			"--3d",
			help="Enable 3D plotting. If not set, the plot will be in 2D."
		)
	] = False,
	output_file: Optional[str] = plot_output_file_arg_spec,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Produces a scatter plot of the scenarios currently imported into the specified session file. The plot can be in 2D or 3D
	"""
	session = __get_session(session_file)
	if plot_3d:
		data_dist_3d.plot_data_dist(session, output_file)
	else:
		data_dist.plot_data_dist(session, output_file)

@app.command()
def import_algorithms(
	algorithm_configurations_file: Annotated[
		str,
		typer.Argument(
			help=(
				"The path to a .ini file containing the algorithm configurations to import. "
				"A section in the file is dedicated to a specific algorithm, "
				"and properties correspond to parameters of that algorithm. "
				"Parameter values are not limited to a single one; but multiple values can be specified, "
				"resulting in a separate algorithm configuration being imported for each unique combination of values."
			)
		)
	],
	override: Annotated[
		bool,
		typer.Option(
			help=(
				"If set, existing algorithm configurations that conflict with the imported ones will be overwritten. "
				"If not set, existing configurations will be skipped."
			)
		)
	] = False,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Import algorithm configurations from the Valentine framework into the specified session file.
	Algorithm configurations include parameters that allow automatic initialisation of the algorithms. 
	"""
	session = __get_session(session_file)

	config = configparser.ConfigParser(allow_no_value=True)
	config.read(algorithm_configurations_file)

	loaded_count = 0
	for algorithm_name in cancelation_token.watch(config.sections()):
		parameter_grid_strs = config[algorithm_name]
		algorithm_name = algorithm_name.lower()
		for parameters, matcher in cancelation_token.watch(get_matchers(algorithm_name, parameter_grid_strs)):
			parameters_json = serialise_parameters(parameters)
			if session.upload_algorithm(algorithm_name, parameters_json, override):
				loaded_count += 1
				
	typer.echo(f"Imported {loaded_count} algorithms.")

@app.command()
def list_algorithms(
	algorithm_name: Annotated[
		Optional[str],
		typer.Argument(
			help=(
				"The name of a specific algorithm to display. "
				"If not specified, all algorithm configurations in the session file will be listed."
			)
		)
	] = None,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	List all algorithm configurations currently imported into the specified session file.
	"""
	session = __get_session(session_file)
	selected_algorithms = []
	if algorithm_name is None:
		selected_algorithms.extend(session.get_algorithm_names())
	else:
		selected_algorithms.append(algorithm_name)
	selected_algorithms = sorted(selected_algorithms)

	for algorithm_name in cancelation_token.watch(selected_algorithms):
		parameters = []
		typer.echo(f"Algorithm: {algorithm_name}")
		for algorithm in session.get_all_algorithms_of(algorithm_name):
			parameters.append(json_to_dict(algorithm.parameters))
		if len(parameters) == 0:
			typer.echo(f"No configurations found.")
		else:
			typer.echo(f"{len(parameters)} configurations")
			console.print(build_table(parameters))

@app.command()
def run(
	algorithm_name: Annotated[
		Optional[str],
		typer.Option(
			help="The name of a specific algorithm to run. If not specified, all algorithms in the session file are run."
		)
	] = None,
	direction: Annotated[
		Optional[str],
		typer.Option(
			help="The direction of execution for schema matching: 'st' (source-to-target), 'ts' (target-to-source), or 'both'."
		)
	] = "both",
	override: Annotated[
		bool,
		typer.Option(
			help="If set, existing matchings in the session will be overridden with new results."
		)
	] = False,
	timeout: Annotated[
		Optional[int],
		typer.Option(
			help="The timeout value in seconds for the algorithm execution. "
				 "This applies globally unless 'timeout_by_direction' is set. Supported only on non-Windows systems."
		)
	] = None,
	timeout_by_direction: Annotated[
		bool,
		typer.Option(
			help="If set, the timeout value is applied to each direction of execution separately (st and ts)."
		)
	] = False,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Run algorithms over the schema matching scenarios in the specified session file.
	Metrics for the solutions are also computed against the corresponding ground truth.
	"""
	if direction not in {"both", "st", "ts"}:
		typer.echo("Error: Direction must be one of 'both', 'st', or 'ts'.")
		raise typer.Exit()
	
	if timeout is not None and timeout <= 0:
		typer.echo("Error: Timeout must be greater than 0 if specified.")
		raise typer.Exit()

	session = __get_session(session_file)

	global_timeout = None
	individual_timeout = None
	if timeout_by_direction:
		individual_timeout = timeout
	else:
		global_timeout = timeout

	db_selected_scenarios = session.select_scenarios(None) # None, select all scenarios
	db_selected_algorithms = session.select_algorithms(algorithm_name, None) # None, select all configurations
	
	for db_scenario in cancelation_token.watch(db_selected_scenarios):
		scenario_data = load_scenario(db_scenario.name, True)
		if scenario_data is None:
			typer.echo(f"Scenario '{db_scenario.name}' from session not found in the repository.")
			continue
		
		typer.echo(f"{db_scenario.name}")
		i = 0
		
		for db_algorithm in cancelation_token.watch(db_selected_algorithms):
			i += 1
			print(f"\r{i}", end="")
			
			matcher = get_first_matcher(db_algorithm.name, json_to_dict(db_algorithm.parameters))
			source_name, target_name = prepare_source_target_names(scenario_data.source_name, scenario_data.target_name)
			db_exisitng_matching = session.get_matching(db_algorithm.id, db_scenario.id)
			
			def __do_matching():
				died = False
				if direction in ["both", "st"] and (override or db_exisitng_matching is None or db_exisitng_matching.matchings is None):
					try:
						matches, time_matches = timer(lambda: valentine_match(scenario_data.source_df, scenario_data.target_df, matcher, source_name, target_name), individual_timeout)
						metrics = matches.get_metrics(scenario_data.ground_truth_as_tuples())
						session.upload_matching(db_algorithm, db_scenario, matches, time_matches, metrics, override)
					except Exception as e:
						died = True
						typer.echo(e)
						
				if not died and direction in ["both", "ts"] and (override or db_exisitng_matching is None or db_exisitng_matching.flip_input_matchings is None):
					try:
						flip_input_matches, time_flip_input_matches = timer(lambda: valentine_match(scenario_data.target_df, scenario_data.source_df, matcher, target_name, source_name), individual_timeout)
						session.upload_flipped_matching(db_algorithm, db_scenario, flip_input_matches, time_flip_input_matches, override)
					except Exception as e:
						died = True
						typer.echo(e)
						
			try:
				timer(__do_matching, global_timeout)
			except Exception as e:
				typer.echo(e)

		print("")

@app.command()
def plot_match_dist(
	output_file: Optional[str] = plot_output_file_arg_spec ,
	session_name: Optional[str] = session_file_arg_spec
):
	"""
	Produces a scatter plot of matchings by ground truth size and the Recall@GT metric.
	"""
	session = __get_session(session_name)
	match_dist.plot_match_dist(session, output_file)

@app.command()
def compute_discretisation(
	override: Annotated[
		bool,
		typer.Option(
			help=(
				"If set, existing discretisation results in the session file will be overwritten. "
			)
		)
	] = False,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Transform confidence degree values of the matchings in the specified session file into discrete ranks in ascending order.
	Discretisation assigns rank values to confidence degrees, with higher ranks for higher confidence levels.
	"""
	session = __get_session(session_file)
	i = 1
	for db_matching in cancelation_token.watch(session.get_all_matchings()):
		print(f"\r{i}", end="")
		if db_matching.matchings is not None and (override or db_matching.matchings_lev is None):
			matches_lev = translate_probabilities_to_levels(round_dict_values(json_to_dict_with_tuples(db_matching.matchings), precision))
			session.upload_matching_as_preferences(db_matching.id, matches_lev)
			
		if db_matching.flip_input_matchings is not None and (override or db_matching.flip_input_matchings_lev is None):
			flip_input_matches_lev = translate_probabilities_to_levels(round_dict_values(json_to_dict_with_tuples(db_matching.flip_input_matchings), precision))
			session.upload_flipped_matching_as_preferences(db_matching.id, flip_input_matches_lev)
		i += 1
		
	print("")
	
@app.command()
def compute_hash(
	override: Annotated[
		bool,
		typer.Option(
			help=(
				"If set, existing hash values will be overwritten. "
			)
		)
	] = False,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Compute a hash from matchings in the specified session file.
	"""
	def __parse_matching_json(matching_json):
		# if json_to_dict_with_tuples is used instead of json.loads hashing won't take
		# into account the ordering of the inner elements (tuples) of the keys and thus
		# hashes will be equal between hash_matchings and hash_flip_input_matchings. this is NOT
		# desired behaviour, thus use json.loads only
		return round_dict_values(json.loads(matching_json), precision) 
	
	session = __get_session(session_file)
	i = 1
	for db_matching in cancelation_token.watch(session.get_all_matchings()):
		print(f"\r{i}", end="")
		if db_matching.matchings is not None and (override or db_matching.hash_matchings is None):
			hash_matchings = compute_object_hash(__parse_matching_json(db_matching.matchings))
			session.upload_matching_hash(db_matching.id, hash_matchings)
			
		if db_matching.matchings_lev is not None and (override or db_matching.hash_matchings_lev is None):
			hash_matchings_lev = compute_object_hash(__parse_matching_json(db_matching.matchings_lev))
			session.upload_matching_as_preferences_hash(db_matching.id, hash_matchings_lev)
			
		if db_matching.flip_input_matchings is not None and (override or db_matching.hash_flip_input_matchings is None):
			hash_flip_input_matchings = compute_object_hash(__parse_matching_json(db_matching.flip_input_matchings))
			session.upload_flipped_matching_hash(db_matching.id, hash_flip_input_matchings)
			
		if db_matching.flip_input_matchings_lev is not None and (override or db_matching.hash_flip_input_matchings_lev is None):
			hash_flip_input_matchings_lev = compute_object_hash(__parse_matching_json(db_matching.flip_input_matchings_lev))
			session.upload_flipped_matching_as_preferences_hash(db_matching.id, hash_flip_input_matchings_lev)
		i += 1

	print("")

@app.command()
def compute_features(
	override: Annotated[
		bool,
		typer.Option(
			help=(
				"If set, existing computed features will be overwritten. "
			)
		)
	] = False,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Transform matchings in the specified session file into preference lists of the stable marriage problem,
	and determine their features. The computed features include symmetry, balancedness, completeness,
	and the presence of ties.
	"""
	session = __get_session(session_file)
	i = 1
	for db_matching in cancelation_token.watch(session.get_all_matchings()):
		print(f"\r{i}", end="")
		if db_matching.matchings_lev is not None and db_matching.flip_input_matchings_lev is not None and (override or db_matching.is_symmetric is None):
			matchings = json_to_dict_with_tuples(db_matching.matchings_lev)
			pref_of_source, infer_pref_of_target = build_preference_lists(matchings)
					
			flip_input_matchings = json_to_dict_with_tuples(db_matching.flip_input_matchings_lev)
			pref_of_target, infer_pref_of_source = build_preference_lists(flip_input_matchings)

			is_symmetric = check_is_symmetric(pref_of_source, infer_pref_of_source, pref_of_target, infer_pref_of_target)
			is_complete = check_is_complete(pref_of_source, pref_of_target)
			has_ties = check_has_ties(pref_of_source) or check_has_ties(pref_of_target)
			is_balanced = check_is_balanced(pref_of_source, pref_of_target)
			
			session.upload_features(db_matching.id, is_symmetric, is_complete, has_ties, is_balanced)
		i += 1
		
	print("")

@app.command()
def view_class(session_file: Optional[str] = session_file_arg_spec):
	"""
	View the complexity class for the stable marriage problems derived from the matchings in the specified session file.
	"""
	session = __get_session(session_file)
	counts = session.get_matching_class_count()
	console.print(build_table([counts]))

@app.command()
def export_uniques_by_class(
	destination: Annotated[
		str,
		typer.Argument(
			help="The destination session file where the unique matchings will be exported. The file should have a .mt extension."
		)
	],
	complexity: Annotated[
		Optional[str],
		typer.Option(
			help=(
				"The complexity class of the stable marriage problem instances to export. "
				"If not specified, unique matchings across all complexity classes are exported."
			)
		)
	] = None,
	start: Annotated[
		Optional[int],
		typer.Option(
			help=(
				"The starting index of the range of matchings to export. "
				"If not specified, starts from the first matching."
			)
		)
	] = None,
	end: Annotated[
		Optional[int],
		typer.Option(
			help=(
				"The ending index of the range of matchings to export. "
				"If not specified, processes up to the last matching."
			)
		)
	] = None,
	session_name: Optional[str] = session_file_arg_spec
):
	"""
	Export unique matchings based on the specified complexity class of their derived stable marriage problem instances.
	Matchings that already exist in the destination session file are skipped.
	"""
	session = __get_session(session_name)	
	bkp = MatchingSession(destination, __notification_fallback)	
	session.export_representative_matchings(bkp, complexity, (start, end))
	
@app.command()
def formulate_qubo(
	start: Annotated[
		Optional[int],
		typer.Option(
			help=(
				"The starting index of the range of matchings in the session file for which QUBOs will be formulated. "
				"If not specified, starts from the first matching."
			)
		)
	] = None,
	end: Annotated[
		Optional[int],
		typer.Option(
			help=(
				"The ending index of the range of matchings in the session file for which QUBOs will be formulated. "
				"If not specified, processes up to the last matching."
			)
		)
	] = None,
	override: Annotated[
		bool,
		typer.Option(
			help=(
				"If set, existing QUBO formulations will be overwritten. "
			)
		)
	] = False,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Formulates matchings in the specified session file as QUBOs. The resulting QUBO formulations are written to separate files
	in a folder with the same name as the session file.
	"""
	def __get_source_and_target_elements(matchings, flip_input_matchings):
		source_elements, target_elements = extract_elements(matchings)
		source_elements_flip, target_elements_flip = extract_elements(flip_input_matchings)
		source_elements.update(target_elements_flip)
		target_elements.update(source_elements_flip)
		return list(source_elements), list(target_elements)

	session = __get_session(session_file)

	session_folder, base_folder_path, qubo_folder_path = __session_folders(session.session_file, "qubos")

	i = 1
	for db_matching in cancelation_token.watch(session.get_all_matchings((start, end))):
		print(f"\r{i}", end="")
		if db_matching.matchings_lev is not None and db_matching.flip_input_matchings_lev is not None and (override or db_matching.qubo_formula is None):
			matchings = json_to_dict_with_tuples(db_matching.matchings_lev)
			prefix_source_target_names(matchings, "src__", "trg__")
			flip_input_matchings = json_to_dict_with_tuples(db_matching.flip_input_matchings_lev)
			prefix_source_target_names(flip_input_matchings, "trg__", "src__")
			
			source_elements, target_elements = __get_source_and_target_elements(matchings, flip_input_matchings)
			
			full_matchings = {**matchings, **flip_input_matchings}
			
			qubo = formulate_as_qubo(full_matchings, source_elements, target_elements)

			number_of_variables = qubo.get_num_binary_vars()
			linear_terms = qubo.objective.linear.to_dict()
			quadratic_terms = qubo.objective.quadratic.to_dict()
			
			qubo_file_name = f"{db_matching.id}.lp"
			qubo_file_path = os.path.join(qubo_folder_path, qubo_file_name)
			qubo.write_to_lp_file(qubo_file_path)
			
			relative_qubo_path = os.path.relpath(qubo_file_path, base_folder_path)
			session.upload_qubo_formula(db_matching.id, relative_qubo_path, number_of_variables, len(linear_terms), len(quadratic_terms))
		i += 1

	print("")

@app.command()
def plot_qubo_dist(
	output_file: Optional[str] = plot_output_file_arg_spec ,
	session_name: Optional[str] = session_file_arg_spec
):
	"""
	Produces a scatter plot of QUBO formulations by number of linear terms and quadratic terms.
	"""
	session = __get_session(session_name)	
	qubo_dist.plot_qubo_dist(session, output_file)
	
@app.command()
def plot_qubo_histogram(
	output_file: Optional[str] = plot_output_file_arg_spec ,
	session_name: Optional[str] = session_file_arg_spec
):
	"""
	Produces a 2D histogram of QUBO formulations by number of linear terms and quadratic terms.
	"""
	session = __get_session(session_name)	
	qubo_histogram.plot_qubo_histogram(session, output_file)

@app.command()
def solve_qubo(
	max_variables: Annotated[
		Optional[int],
		typer.Option(
			help=(
				"The maximum number of variables in the QUBO formulations to be solved. "
				"Only QUBOs with up to this number of variables are solved; others are skipped."
			)
		)
	] = None,
	start: Annotated[
		Optional[int],
		typer.Option(
			help=(
				"The starting index of the range of matchings in the session file to solve QUBOs for. "
				"If not specified, starts from the first matching."
			)
		)
	] = None,
	end: Annotated[
		Optional[int],
		typer.Option(
			help=(
				"The ending index of the range of matchings in the session file to solve QUBOs for. "
				"If not specified, processes up to the last matching."
			)
		)
	] = None,
	timeout: Annotated[
		Optional[int],
		typer.Option(
			help="Timeout value in seconds for solving QUBOs (supported on all operating systems)."
		)
	] = None,
	override: Annotated[
		bool,
		typer.Option(
			help=(
				"If set, existing QUBO solutions will be overwritten. "
			)
		)
	] = False,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Solve QUBO formulations, using classical methods, for the matchings in the specified session file.
	Metrics for the solutions are also computed against the corresponding ground truth.
	"""
	session = __get_session(session_file)

	session_folder, base_folder_path = __session_folders(session.session_file)
	
	i = 1
	
	for db_matching in cancelation_token.watch(session.get_all_matchings((start, end))):
		print(f"\r{i}", end="")
		if db_matching.qubo_formula is not None and (override or db_matching.qubo_matchings is None):
			
			if max_variables is not None and db_matching.qubo_number_of_variables > max_variables:
				continue

			qubo_file_path = os.path.join(base_folder_path, db_matching.qubo_formula)
			qubo = QuadraticProgram()
			qubo.read_from_lp_file(qubo_file_path)
			docplex_model = get_docplex_model(qubo)
			
			try:
				if timeout is not None:
					docplex_model.context.cplex_parameters.timelimit = timeout
				solution = docplex_model.solve()
				opt_value = solution.get_objective_value()
				active_vars = [var.name for var in docplex_model.iter_variables() if solution.get_value(var) != 0]
				
				source_name, target_name = get_source_target_names(db_matching.dataset.name)
				matchings = interpret_qubo_variables_as_matching(active_vars, source_name, target_name)
				
				session.upload_qubo_matchings(db_matching.id, matchings, active_vars, opt_value)
				
				# metrics
				scenario_data = load_scenario(db_matching.dataset.name, False) # actual data is not needed. only the ground truths.
				matchings_as_valentine = instanciate_results(matchings)
				metrics = matchings_as_valentine.get_metrics(scenario_data.ground_truth_as_tuples())
				session.upload_qubo_matchings_metrics(db_matching.id, metrics)

			except Exception as e:
				typer.echo(e)
			
		i += 1

	print("")

@app.command()
def build_qaoa_circuit(
	p: Annotated[
		int,
		typer.Option(
			help="The number of layers in the QAOA circuit. Higher values increase the circuit depth."
		)
	] = 1,
	override: Annotated[
		bool,
		typer.Option(
			help=(
				"If set, existing properties of QAOA circuits will be overwritten. "
			)
		)
	] = False,
	timeout: Annotated[
		Optional[int],
		typer.Option(
			help="Timeout value in seconds for building individual QAOA circuits. Supported only on non-Windows systems."
		)
	] = None,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Build QAOA circuits from QUBO formulations in the specified session file. Properties of circuits are computed, including depth and width.
	"""
	if p < 1:
		typer.echo("Error: The number of layers 'p' must be greater than or equal to 1.")
		raise typer.Exit()

	session = __get_session(session_file)

	session_folder, base_folder_path = __session_folders(session.session_file)
	
	i = 1

	for db_matching in cancelation_token.watch(session.get_all_matchings_order_by_qubo_size()):
		print(f"\r{i}", end="")

		if db_matching.qubo_formula is not None and (override or db_matching.qaoa_depth is None):			
			qubo_file_path = os.path.join(base_folder_path, db_matching.qubo_formula)
			qubo = QuadraticProgram()
			qubo.read_from_lp_file(qubo_file_path)

			def __do_build_circuit():
				circuit, depth, width, time_ansatz, time_transpile = get_qaoa_cicuit(qubo, p)
				session.upload_qaoa_circuit_metadata(db_matching.id, p, depth, width, time_ansatz, time_transpile)
			
			try:
				timer(__do_build_circuit, timeout)
			except Exception as e:
				typer.echo(e)
				
		i += 1
		
	print("")
	
@app.command()
def run_qaoa_circuit(
	shots: Annotated[
		int,
		typer.Option(
			help=(
				"The number of shots for each individual QAOA circuit. "
			)
		)
	] = 1024,
	max_width: Annotated[
		Optional[int],
		typer.Option(
			help=(
				"The maximum width for QAOA circuits to be executed. "
				"Only circuits with a width up to this value will be executed; others are skipped."
			)
		)
	] = None,
	override: Annotated[
		bool,
		typer.Option(
			help=(
				"If set, existing execution results will be overwritten. "
			)
		)
	] = False,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Execute QAOA circuits from the specified session file.
	Metrics for the solutions are also computed against the corresponding ground truth.
	"""
	if shots < 1:
		typer.echo("Error: The number of shots must be greater than or equal to 1.")
		raise typer.Exit()
	
	session = __get_session(session_file)
	
	session_folder, base_folder_path = __session_folders(session.session_file)
	
	i = 1

	for db_matching in cancelation_token.watch(session.get_all_matchings()):
		print(f"\r{i}", end="")
		
		if db_matching.qubo_formula is not None and (override or db_matching.qaoa_matchings is None):
			
			if max_width is not None and db_matching.qaoa_width > max_width:
				continue
			
			qubo_file_path = os.path.join(base_folder_path, db_matching.qubo_formula)
			qubo = QuadraticProgram()
			qubo.read_from_lp_file(qubo_file_path)
			
			source_name, target_name = get_source_target_names(db_matching.dataset.name)
			active_vars, opt_value = run_qaoa_cicuit(qubo, db_matching.qaoa_p, shots)
			matchings = interpret_qubo_variables_as_matching(active_vars, source_name, target_name)
			
			session.upload_qaoa_matchings(db_matching.id, shots, matchings, active_vars, opt_value)

			# metrics
			scenario_data = load_scenario(db_matching.dataset.name, False) # actual data is not needed. only the ground truths.
			matchings_as_valentine = instanciate_results(matchings)
			metrics = matchings_as_valentine.get_metrics(scenario_data.ground_truth_as_tuples())
			session.upload_qaoa_matchings_metrics(db_matching.id, metrics)

		i += 1

	print("")
	
@app.command()
def plot_qubo_qaoa_dist(
	output_file: Optional[str] = plot_output_file_arg_spec ,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Produces a box plot of the distribution of QAOA circuits according to their depth, grouped by the size of the QUBO formulations from which they were built.
	"""
	session = __get_session(session_file)
	qubo_qaoa_dist.plot_qubo_qaoa_dist(session, output_file)
	
@app.command()
def plot_qaoa_dist(
	output_file: Optional[str] = plot_output_file_arg_spec ,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Produces a scatter plot of the distribution of QAOA circuits according to their width and depth.
	"""
	session = __get_session(session_file)
	qaoa_dist.plot_qaoa_dist(session, output_file)

@app.command()
def plot_qaoa_histogram(
	output_file: Optional[str] = plot_output_file_arg_spec ,
	session_file: Optional[str] = session_file_arg_spec
):
	"""
	Produces a histogram of QAOA circuits according to width.
	"""
	session = __get_session(session_file)
	qaoa_histogram.plot_qaoa_histogram(session, output_file)

@app.command()
def print_recall_gt(
	group: Annotated[
		str,
		typer.Argument(
			help="Group to filter by: 'qubo' for QUBO optimisation or 'qaoa' for QAOA circuits."
		)
	],
	session_file: Optional[str] = session_file_arg_spec
):
	"""	
	Produces a comparison of the mean Recall@GT metric between matchings obtained from schema matching algorithms,
	QAOA circuits, and QUBO optimisation.
	"""
	if group not in {"qubo", "qaoa"}:
		typer.echo("Invalid group. Must be 'qubo' or 'qaoa'.")
		raise typer.Exit()

	session = __get_session(session_file)

	head = group.upper()
	for bin_key, recall_stats_df in recall_stats.generate_recall_tables(session, group):		
		tbl = Table(title=f"Statistics for {bin_key}")

		tbl.add_column("Source", justify="left")
		tbl.add_column("Algs Recall@GT Mean", justify="right")
		tbl.add_column("Algs Recall@GT Std", justify="right")
		tbl.add_column(f"{head} Recall@GT Mean", justify="right")
		tbl.add_column(f"{head} Recall@GT Std", justify="right")
		tbl.add_column("Percentage", justify="right")
		tbl.add_column("Improvement", justify="center")

		for _, row in recall_stats_df.iterrows():
			tbl.add_row(
				str(row["Source"]),
				f"{row['Algs_Recall_GT_Mean']:.2f}",
				f"{row['Algs_Recall_GT_Std']:.2f}",
				f"{row[f'{head}_Recall_GT_Mean']:.2f}",
				f"{row[f'{head}_Recall_GT_Std']:.2f}",
				f"{row['Percentage']:.2f}%",
				row["Improvement"],
			)

		console.print(tbl)
	
if __name__ == "__main__":
	app()
