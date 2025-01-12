# Schema Matching Data Scenarios

This repository is a compendium of tabular datasets for performing schema matching across a variety of scenarios and provides a Python interface for consuming them.

Data hosted in this repository has been gathered from a number of appropriately referenced independent sources or works which were made available by their corresponding authors in their corresponding repositories. Nonetheless, data herein has been transformed to suit schema matching purposes.

This repository is organised into directories named after the source or work from which data was gathered. Inside each directory, a README file is included, referencing the original source and providing specific information on how its data was transformed to support schema matching scenarios.

## Install

Follow the next instructions to make this repository available to Python projects either globally or locally.

### Global project access

To enable access to this repository globally from any Python project, this repository has to be placed inside one of the directories referenced by the `PYTHONPATH` environment variable. To this end, check `PYTHONPATH` by running the following commands in a Python CLI and choose a convenient directory from the output list of directories. If working on a Python virtual environment, choosing the package directory of the virtual environment is advised.

```python
>>> import sys
>>> print(sys.path)
```

Navigate to the chosen directory and, inside it, create a new directory called `schema_matching_scenarios`. Then, place the contents of this repository inside this newly created directory.

### Local project access

To enable access to this repository for some current Python project, this repository has to be placed alongside the main Python script. To this end, create a new directory called `schema_matching_scenarios` inside the same directory where the main Python script lays and place the contents of this repository inside this newly created directory.

---

Regardless of local or global installation, the resulting file structure should read as follows:

```
schema_matching_scenarios
├── data_sets
├── __init__.py
├── README.md
└── scenario_catalogue.py
```

Finally, follow the usage guide to consume the data scenarios.

## Usage

### Setup

Import the required dependencies.

```python
from schema_matching_scenarios import load_scenario, scenario_names
```

### Exploring available data scenarios

Data scenarios are identified by a unique name. Use the `scenario_names` method to list the names of all available data scenarios.

```python
for scenario_name in scenario_names():
	print(scenario_name)
```

A data scenario name is formatted as follows:

```
{origin}/{organising_group}/{source_table_name}>>{target_table_name}
```

- `origin`: The name of the original source from where the corresponding data was gathered.
- `organising_group`: Some identifiers for organisation.
- `source_table_name`: The name of the source table to use for schema matching.
- `target_table_name`: The name of the target table to use for schema matching.

Example:

```
_Schematch/DeNorm/IDSystem/ID>>System
_Schematch/DeNorm/Student/Student>>Course
_Schematch/Efes-bib/s1a-s2b/article>>allbibs
_Schematch/Efes-bib/s1a-s2b/article>>journal
_Schematch/Efes-bib/s1a-s2b/article>>months
```

### Loading a data scenario

Load a given data scenario by providing its corresponding name to the the `load_scenario` method.

```python
scenario = load_scenario("_Schematch/DeNorm/IDSystem/ID>>System")
```

The returned `scenario` object is composed of three properties:

- `scenario.source_df`: A Pandas data frame containing the source table.

- `scenario.target_df`: A Pandas data frame containing the target table.

- `scenario.ground_truth`: A dictionary specifying the matchings between columns of the source table with columns of the target table. The dictionary is of the form:

  ```
  {
  	'matches': [
  		{
  			'source_table': 'ID',
  			'source_column': 'IDA',
  			'target_table': 'System',
  			'target_column': 'A'
  		},
  		{
  			'source_table': 'ID',
  			'source_column': 'IDB',
  			'target_table': 'System',
  			'target_column': 'B'
  		},
  		...
  	]
  }
  ```

#### Transforming the ground-truth representation

Use the `ground_truth_as_tuples` method of the `scenario` object to transform the ground-truth dictionary into a list of tuples of the form:

```
[
	('IDA', 'A'),
	('IDB', 'B'),
	...
]
```

### Retrieving statistics about a data scenario

Some basic statistics about a data scenario are available by calling the `get_stats` method of the `scenario` object.

```python
stats = scenario.get_stats()
```

The returned `stats` object is composed of the following properties:

- `stats.matching_type`: The type of matching between the source and target tables according to the ground-truth. Possible values are:
  - `1:1`: According to the ground-truth, each column of the source table matches to at most one column of the target table.
  - `1:n`: According to the ground-truth, there exists at least one column of the source table which matches to more than one column of the target table.
  - `n:1`: According to the ground-truth, there exists at least one column of the target table which is matched by more than one column of the source table.
  - `n:n`: According to the ground-truth, there exist columns from the source and target tables that respectively satisfy conditions for both `1:n` and `n:1` matchings. This does not necessarily imply that multiple columns of the source table match to multiple columns of the target table.
- `stats.ground_truth_size`: The number of matches between the source and target tables according to the ground-truth.
- `stats.source_column_count`: The total number of columns in the source table.
- `stats.target_column_count`: The total number of columns in the target table.

### Example

```python
from schema_matching_scenarios import scenario_names, load_scenario

for scenario_name in scenario_names():
	print(f"Scenario {scenario_name}:")
	
	scenario = load_scenario(scenario_name)
	stats = scenario.get_stats()

	print(f"\tNumber of columns in the source table: {stats.source_column_count}")
	print(f"\tNumber of columns in the target table: {stats.target_column_count}")
	print(f"\tNumber of matchings: {stats.ground_truth_size}")
	print(f"\tType of matching: {stats.matching_type}")
	
	# perform matching between scenario.source_df and scenario.target_df

	ground_truth_tuples = scenario.ground_truth_as_tuples()
	
	# compare matching result against ground_truth_tuples

	print("")

print("Done")
```
