# MatchingHub: Usage Guide

**MatchingHub** is a CLI utility designed for executing schema matching pipelines. It operates on `.mt` files called *sessions*, which store data scenarios, algorithms, matchings, and final results. Broadly, the pipeline is formed of the following stages:

1. Running matching algorithms from the Valentine framework.
2. Transforming the resulting matchings into instances of the stable marriage problem.  
3. Formulating the stable marriage problem instances as QUBO.  
4. Solving the QUBO formulations using both classical methods and QAOA circuits.  

This contribution builds upon foundational work from the following references:  

1. C. Koutras, G. Siachamis, A. Ionescu, K. Psarakis, J. Brons, M. Fragkoulis, C. Lofi, A. Bonifati, and A. Katsifodimos, “Valentine: Evaluating Matching Techniques for Dataset Discovery,” in 2021 IEEE 37th International Conference on Data Engineering (ICDE). IEEE, 2021, pp. 468–479. [Online]. Available: https://doi.org/10.1109/ICDE51399.2021.00047
2. K. Fritsch and S. Scherzinger, “Solving Hard Variants of Database Schema Matching on Quantum Computers,” Proc. VLDB Endow., vol. 16, no. 12, p. 3990–3993, Aug. 2023. [Online]. Available: https://doi.org/10.14778/3611540.3611603
3. C. Roch, D. Winderl, C. Linnhoff-Popien, and S. Feld, “A Quantum Annealing Approach for Solving Hard Variants of the Stable Marriage Problem,” in Innovations for Community Services. Springer International Publishing, 2022, pp. 294–307. [Online]. Available: https://doi.org/10.1007/978-3-031-06668-9_21

This document is organised into sections dedicated to working with sessions, data scenarios, algorithms, matchings, QUBO formulations, and QAOA circuits. Each section presents commands for importing data, running pipelines, plotting results, and exporting final matchings and accuracy metrics.

Refer to the [demo sample](./experiments/1_demo_sample_small/README.md) for an example of running a concrete full pipeline.

**Note:** Use the following command to get help directly form the MatchingHub application regarding overall or specific commands:

```
matchinghub --help
```

```
matchinghub run --help # Replace `run` with the corresponding command to get relevant help.
```

## Sessions

A session is a plain SQLite database file of `.mt` extension.

The following presents commands for working with sessions.

### `initialise`

Initialises a new session file for schema matching. If the specified session file already exists, the command will terminate with an error.

#### Arguments

| Argument      | Description                                                                  | Type   | Required | Range                       | Default      |
|---------------|------------------------------------------------------------------------------|--------|----------|-----------------------------|--------------|
| session_file  | Path to the session file to initialise. The file should have a `.mt` extension. | str    | No       |                             | `"matching.mt"` |

#### Example

1. Using the default session file `matching.mt`:
   ```bash
   matchinghub initialise
   ```

2. Specifying a custom session file:
   ```bash
   matchinghub initialise custom_session.mt
   ```
   

---
## Scenarios

Data scenarios are composed of two relations to match alongside the ground truth which indicates how attributes from either relation correspond to attributes of the other relation. Actual data of scenarios is stored in an external centralised repository which is accessible by any session. Refer to the [scenario usage guide](./src/schema_matching_scenarios/README.md) for details about the centralised repository. Sessions store metadata and references to the scenarios in the external repository.

The following presents commands for working with scenarios.

### `list-repo-scenarios`

Lists all available schema matching scenarios in the external repository.

#### Arguments

| Argument | Description                                                                                                                                                                                                                                                                                           | Type  | Required | Range                     | Default   |
|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|----------|---------------------------|-----------|
| table    | If set, displays a detailed table with: - the name of the scenario - the cardinality of the matching - the number of columns in the source relation - the number of columns in the target relation - the size of the ground truth. If not set, only the names of the scenarios are displayed. | flag  | No       | `--table`, `--no-table`   | `--no-table` |

#### Example

1. Display the names of the scenarios:
   ```bash
   matchinghub list-repo-scenarios
   ```

2. Display a detailed table of the scenarios:
   ```bash
   matchinghub list-repo-scenarios --table
   ```

---

### `import-scenarios`

Imports scenario definitions from the external repository into the specified session file. Scenario definitions include metadata only and not any actual data.

#### Arguments

| Argument            | Description                                                                                                   | Type  | Required | Range                     | Default      |
|---------------------|---------------------------------------------------------------------------------------------------------------|-------|----------|---------------------------|--------------|
| scenario_names_file | Path to the file containing the names of the scenarios to import.                                             | str   | Yes      |                           |              |
| override            | If set, existing scenarios in the session file will be overwritten by the imported ones. Otherwise, they are skipped. | flag  | No       | `--override`, `--no-override` | `--no-override` |
| session_file        | Path to the session file where scenarios will be imported.                                                   | str   | No       |                           | `"matching.mt"` |

#### Example

1. Import scenarios from a file without overwriting existing ones:
   ```bash
   matchinghub import-scenarios scenarios.txt
   ```

2. Import scenarios from a file and overwrite existing ones:
   ```bash
   matchinghub import-scenarios scenarios.txt --override
   ```

3. Import scenarios into a custom session file:
   ```bash
   matchinghub import-scenarios scenarios.txt --override -s custom_session.mt
   ```
---
### `list-scenarios`

List all schema matching scenarios currently imported into the specified session file.

#### Arguments

| Argument      | Description                                                                                                                        | Type  | Required | Range                     | Default      |
|---------------|------------------------------------------------------------------------------------------------------------------------------------|-------|----------|---------------------------|--------------|
| table         | If set, displays a detailed table including: - the name of the scenario - the cardinality of the matching - source and target columns - ground truth size. | flag  | No       | `--table`, `--no-table`   | `--no-table` |
| session_file  | Path to the session file.                                                                              | str   | No       |                           | `"matching.mt"` |

#### Example

1. Display the names of the scenarios in the default session file:
   ```bash
   matchinghub list-scenarios
   ```

2. Display a detailed table of the scenarios in the default session file:
   ```bash
   matchinghub list-scenarios --table
   ```

3. Display scenarios in a custom session file with a detailed table:
   ```bash
   matchinghub list-scenarios --table -s custom_session.mt
   ```
---

### `plot-scenario-dist`

Produces a scatter plot of the scenarios currently imported into the specified session file. The plot can be in 2D or 3D.

#### Arguments

| Argument      | Description                                                                                                            | Type  | Required | Range                             | Default      |
|---------------|------------------------------------------------------------------------------------------------------------------------|-------|----------|-----------------------------------|--------------|
| plot_3d       | Enable 3D plotting. If not set, the plot will be in 2D.                                                               | flag  | No       | `--3d`, `--no-3d`                 | `--no-3d`    |
| output_file   | Path to the output file for the plot, including the file extension. If not set, the plot is displayed on the screen.   | str   | No       | `eps`, `jpg`, `pdf`, `png`, `svg`, `tiff` |              |
| session_file  | Path to the session file containing the scenarios to plot.                                                            | str   | No       |                                   | `"matching.mt"` |

#### Example

1. Display a 2D plot on the screen:
   ```bash
   matchinghub plot-scenario-dist
   ```

2. Save a 2D plot to a file named `scenarios_plot.pdf`:
   ```bash
   matchinghub plot-scenario-dist scenarios_plot.pdf
   ```

3. Display a 3D plot on the screen:
   ```bash
   matchinghub plot-scenario-dist --3d
   ```

4. Save a 3D plot to a file using scenarios from a custom session file:
   ```bash
   matchinghub plot-scenario-dist --3d scenarios_plot_3d.png -s custom_session.mt
   ```
---
## Algorithms

Concrete implementations of matching algorithms are provided by the Valentine framework. Sessions store configurations of parameters for initialising the algorithms.

The following presents commands for working with algorithms.

### `import-algorithms`

Imports algorithm configurations from the Valentine framework into the specified session file. Algorithm configurations include parameters that allow automatic initialisation of the algorithms.

#### Arguments

| Argument                     | Description                                                                                                                         | Type  | Required | Range                     | Default      |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|-------|----------|---------------------------|--------------|
| algorithm_configurations_file | The path to a `.ini` file containing the algorithm configurations to import. Each section defines an algorithm, and properties define parameters. Multiple parameter values create configurations for all unique combinations. | str   | Yes      |                           |              |
| override                    | If set, existing algorithm configurations that conflict with the imported ones will be overwritten. Otherwise, they are skipped. | flag  | No       | `--override`, `--no-override` | `--no-override` |
| session_file                | Path to the session file where algorithm configurations will be imported.                                                          | str   | No       |                           | `"matching.mt"` |

#### Example

1. Import algorithms from an `.ini` file without overwriting existing configurations:
   ```bash
   matchinghub import-algorithms algorithms.ini
   ```

2. Import algorithms and overwrite conflicting existing configurations:
   ```bash
   matchinghub import-algorithms algorithms.ini --override
   ```

3. Import algorithms into a custom session file:
   ```bash
   matchinghub import-algorithms algorithms.ini --override -s custom_session.mt
   ```
#### Note
Algorithm configurations are specified in `.ini` files. Sections in the file refer to specific algorithms and properties refer to parameters of that algorithm. Following is a sample configuration file:

```ini
[COMA]
max_n = 0
use_instances = false, true
java_xmx = 8192m

[CUPID]
leaf_w_struct = 0.2 : 0.2 : 0.6
w_struct = 0.2 : 0.2 : 0.6
th_accept = 0.3 : 0.1 : 0.8
th_high = 0.6
th_low = 0.35
c_inc = 1.2
c_dec = 0.9
th_ns = 0.5

[SIMILARITYFLOODING]
coeff_policy = inverse_average, inverse_product
formula = basic, formula_a, formula_b, formula_c

[JACCARDDISTANCE]
threshold_dist = 0.3 : 0.1 : 0.8
distance_fun = Levenshtein, DamerauLevenshtein, Hamming, Jaro, JaroWinkler, Exact

[DISTRIBUTIONBASED]
threshold1 = 0.15 : 0.1 : 0.85
threshold2 = 0.15 : 0.1 : 0.85
```

Properties support multiple values for generating combinations of algorithm configurations for each distinct value. For example, a number of configurations will be generated for the `JACCARDDISTANCE` algorithm with the `threshold_dist` parameter ranging from `0.3` to `0.8` with `0.1` step, bounds inclusive; and with the `distance_fun` as `Levenshtein`, `DamerauLevenshtein`, `Hamming`, `Jaro`, `JaroWinkler`, and `Exact`.

---

### `list-algorithms`

Lists all algorithm configurations currently imported into the specified session file.

#### Arguments

| Argument       | Description                                                                                              | Type  | Required | Range | Default      |
|----------------|----------------------------------------------------------------------------------------------------------|-------|----------|-------|--------------|
| algorithm_name | The name of a specific algorithm to display. If not specified, all algorithm configurations are listed. | str   | No       |       |              |
| session_file   | Path to the session file containing the algorithm configurations.                                       | str   | No       |       | `"matching.mt"` |

#### Example

1. List all algorithm configurations in the session file:
   ```bash
   matchinghub list-algorithms
   ```

2. List configurations for a specific algorithm (Cupid):
   ```bash
   matchinghub list-algorithms cupid
   ```

3. List algorithms from a custom session file:
   ```bash
   matchinghub list-algorithms -s custom_session.mt
   ```
---
## Matchings

Matchings result from executing the algorihtms over the data scenarios. A matching is a collection of correspondences between attributes of the two relations in the scenario. Each correspondences is accompanied by a confidence degree ranging from `0` to `1`.

The following presents commands for working with matchings.

### `run`

Run algorithms over the schema matching scenarios in the specified session file. Metrics for the solutions are also computed against the corresponding ground truth.

#### Arguments

| Argument              | Description                                                                                                                  | Type  | Required | Range                                  | Default      |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------|-------|----------|----------------------------------------|--------------|
| algorithm_name | The name of a specific algorithm to run. If not specified, all algorithms in the session file are run.                       | str   | No       |                                        |              |
| direction             | The direction of execution for schema matching: 'st' (source-to-target), 'ts' (target-to-source), or 'both'.       | str   | No       | `st`, `ts`, `both`                     | `"both"`     |
| override              | If set, existing matchings in the session will be overridden with new results.                                               | flag  | No       | `--override`, `--no-override`          | `--no-override` |
| timeout               | The timeout value in seconds for the algorithm execution. Supported only on non-Windows systems.                            | int   | No       | > 0                                    | No timeout |
| timeout_by_direction  | If set, the timeout value is applied to each direction of execution separately (`st` and `ts`).                              | flag  | No       | `--timeout-by-direction`, `--no-timeout-by-direction` | `--no-timeout-by-direction` |
| session_file          | Path to the session file containing the scenarios and algorithms to run.                                                     | str   | No       |                                        | `"matching.mt"` |

#### Example

1. Run all algorithms on all scenarios with the default settings:
   ```bash
   matchinghub run
   ```

2. Run a specific algorithm (Cupid) in both directions with a timeout of 300 seconds:
   ```bash
   matchinghub run --algorithm_name cupid --timeout 300
   ```

3. Run all algorithms in the source-to-target direction only:
   ```bash
   matchinghub run --direction st
   ```

4. Run with the timeout applied to each direction separately:
   ```bash
   matchinghub run --timeout 300 --timeout-by-direction
   ```

5. Run algorithms from a custom session file:
   ```bash
   matchinghub run -s custom_session.mt
   ```
---

### `plot-match-dist`

Produces a scatter plot of matchings by ground truth size and the Recall@GT metric.

#### Arguments

| Argument      | Description                                                                                                            | Type  | Required | Range                                                                                   | Default      |
|---------------|------------------------------------------------------------------------------------------------------------------------|-------|----------|-----------------------------------------------------------------------------------------|--------------|
| output_file   | Path to the output file for the plot, including the file extension. If not set, the plot is displayed on the screen.   | str   | No       | `eps`, `jpg`, `pdf`, `png`, `svg`, `tiff`                                              |              |
| session_name  | Path to the session file containing the matchings to plot.                                                            | str   | No       |                                                                                         | `"matching.mt"` |

#### Example

1. Display the plot on the screen:
   ```bash
   matchinghub plot-match-dist
   ```

2. Save the plot to a file named `match_dist.pdf`:
   ```bash
   matchinghub plot-match-dist match_dist.pdf
   ```

3. Save the plot using matchings from a custom session file:
   ```bash
   matchinghub plot-match-dist match_dist.png -s custom_session.mt
   ```
---

### `compute-discretisation`

Transforms confidence degree values of the matchings in the specified session file into discrete ranks in ascending order. Discretisation assigns rank values to confidence degrees, with higher ranks for higher confidence levels.

#### Arguments

| Argument     | Description                                                                                       | Type  | Required | Range                                  | Default      |
|--------------|---------------------------------------------------------------------------------------------------|-------|----------|----------------------------------------|--------------|
| override     | If set, existing discretisation results in the session file will be overwritten.                 | flag  | No       | `--override`, `--no-override`          | `--no-override` |
| session_file | Path to the session file containing the matchings to discretise.                                  | str   | No       |                                        | `"matching.mt"` |

#### Example

1. Compute discretisation for matchings in the default session file without overwriting existing results:
   ```bash
   matchinghub compute-discretisation
   ```

2. Compute discretisation and overwrite existing results:
   ```bash
   matchinghub compute-discretisation --override
   ```

3. Compute discretisation for a custom session file:
   ```bash
   matchinghub compute-discretisation -s custom_session.mt
   ```
---

### `compute-hash`

Computes a hash from matchings in the specified session file.

#### Arguments

| Argument     | Description                                                                  | Type  | Required | Range                                  | Default      |
|--------------|------------------------------------------------------------------------------|-------|----------|----------------------------------------|--------------|
| override     | If set, existing hash values will be overwritten.                           | flag  | No       | `--override`, `--no-override`          | `--no-override` |
| session_file | Path to the session file containing the matchings to compute hashes for.    | str   | No       |                                        | `"matching.mt"` |

#### Example

1. Compute hashes for matchings in the default session file without overwriting existing hashes:
   ```bash
   matchinghub compute-hash
   ```

2. Compute hashes and overwrite existing ones:
   ```bash
   matchinghub compute-hash --override
   ```

3. Compute hashes for matchings in a custom session file:
   ```bash
   matchinghub compute-hash -s custom_session.mt
   ```
---

### `compute-features`

Transforms matchings in the specified session file into preference lists of the stable marriage problem and determines their features. The computed features include symmetry, balancedness, completeness, and the presence of ties.

#### Arguments

| Argument     | Description                                                                      | Type  | Required | Range                                  | Default      |
|--------------|----------------------------------------------------------------------------------|-------|----------|----------------------------------------|--------------|
| override     | If set, existing computed features will be overwritten.                         | flag  | No       | `--override`, `--no-override`          | `--no-override` |
| session_file | Path to the session file containing the matchings to compute features for.      | str   | No       |                                        | `"matching.mt"` |

#### Example

1. Compute features for matchings in the default session file without overwriting existing features:
   ```bash
   matchinghub compute-features
   ```

2. Compute features and overwrite existing ones:
   ```bash
   matchinghub compute-features --override
   ```

3. Compute features for matchings in a custom session file:
   ```bash
   matchinghub compute-features -s custom_session.mt
   ```
---

### `view-class`

View the complexity class for the stable marriage problems derived from the matchings in the specified session file.

#### Arguments

| Argument     | Description                                                               | Type  | Required | Range | Default      |
|--------------|---------------------------------------------------------------------------|-------|----------|-------|--------------|
| session_file | Path to the session file containing the matchings to classify.           | str   | No       |       | `"matching.mt"` |

#### Example

1. View the complexity class for matchings in the default session file:
   ```bash
   matchinghub view-class
   ```

2. View the complexity class for matchings in a custom session file:
   ```bash
   matchinghub view-class -s custom_session.mt
   ```
---

### `export-uniques-by-class`

Export unique matchings based on the specified complexity class of their derived stable marriage problem instances. Matchings that already exist in the destination session file are skipped.

#### Arguments

| Argument     | Description                                                                                           | Type  | Required | Range         | Default      |
|--------------|-------------------------------------------------------------------------------------------------------|-------|----------|---------------|--------------|
| destination  | The destination session file where the unique matchings will be exported. The file should have a `.mt` extension. | str   | Yes      |               |              |
| complexity   | The complexity class of the stable marriage problem instances to export. If not specified, unique matchings across all complexity classes are exported. | str   | No       | `ilt`,`ilto`, `clt`, `clto` |              |
| start        | The starting index of the range of matchings to export.                                               | int   | No       | >= 0          |              |
| end          | The ending index of the range of matchings to export.                                                 | int   | No       | >= start      |              |
| session_name | Path to the session file containing the matchings to export.                                          | str   | No       |               | `"matching.mt"` |

#### Example

1. Export all unique matchings across all complexity classes to a new session file:
   ```bash
   matchinghub export-uniques-by-class unique_matchings.mt
   ```

2. Export unique matchings of the `ilt` complexity class:
   ```bash
   matchinghub export-uniques-by-class unique_matchings.mt --complexity ilt
   ```

3. Export unique matchings from index 10 to 50:
   ```bash
   matchinghub export-uniques-by-class unique_matchings.mt --start 10 --end 50
   ```

4. Export unique matchings to a new session file using a custom source session file:
   ```bash
   matchinghub export-uniques-by-class unique_matchings.mt -s custom_session.mt
   ```
### Note

The range of values for the complexity argument stand for:

- **`ilt`:** Incomplete lists with ties.
- **`ilto`:** Incomplete lists and total order.
- **`clt`:** Complete lists with ties.
- **`clto`:** Complete lists and total order.

---
## QUBO Formulations

Matchings are formulated as QUBO based on the work of K. Fritsch et al. and C. Roch et al. The formulations are implemented using DOcplex models.

The following presents commands for working with QUBO formulations.

### `formulate-qubo`

Formulates matchings in the specified session file as QUBOs. The resulting QUBO formulations are written to separate files in a folder with the same name as the session file.

#### Arguments

| Argument     | Description                                                                                               | Type  | Required | Range            | Default      |
|--------------|-----------------------------------------------------------------------------------------------------------|-------|----------|------------------|--------------|
| start        | The starting index of the range of matchings for which QUBOs will be formulated.                         | int   | No       | >= 0             |              |
| end          | The ending index of the range of matchings for which QUBOs will be formulated.                           | int   | No       | >= start         |              |
| override     | If set, existing QUBO formulations will be overwritten.                                                  | flag  | No       | `--override`, `--no-override` | `--no-override` |
| session_file | Path to the session file containing the matchings to formulate as QUBOs.                                 | str   | No       |                  | `"matching.mt"` |

#### Example

1. Formulate QUBOs for all matchings in the default session file:
   ```bash
   matchinghub formulate-qubo
   ```

2. Formulate QUBOs for matchings from index 10 to 50:
   ```bash
   matchinghub formulate-qubo --start 10 --end 50
   ```

3. Formulate QUBOs and overwrite existing formulations:
   ```bash
   matchinghub formulate-qubo --override
   ```

4. Formulate QUBOs for matchings in a custom session file:
   ```bash
   matchinghub formulate-qubo -s custom_session.mt
   ```
---

### `plot-qubo-dist`

Produces a scatter plot of QUBO formulations by the number of linear terms and quadratic terms.

#### Arguments

| Argument      | Description                                                                                                            | Type  | Required | Range                                                                                   | Default      |
|---------------|------------------------------------------------------------------------------------------------------------------------|-------|----------|-----------------------------------------------------------------------------------------|--------------|
| output_file   | Path to the output file for the plot, including the file extension. If not set, the plot is displayed on the screen.   | str   | No       | `eps`, `jpg`, `pdf`, `png`, `svg`, `tiff`                                              |              |
| session_name  | Path to the session file containing the QUBO formulations to plot.                                                    | str   | No       |                                                                                         | `"matching.mt"` |

#### Example

1. Display the plot on the screen:
   ```bash
   matchinghub plot-qubo-dist
   ```

2. Save the plot to a file named `qubo_dist.pdf`:
   ```bash
   matchinghub plot-qubo-dist qubo_dist.pdf
   ```

3. Save the plot using QUBO formulations from a custom session file:
   ```bash
   matchinghub plot-qubo-dist qubo_dist.png -s custom_session.mt
   ```
---

### `plot-qubo-histogram`

Produces a 2D histogram of QUBO formulations by the number of linear terms and quadratic terms.

#### Arguments

| Argument      | Description                                                                                                            | Type  | Required | Range                                                                                   | Default      |
|---------------|------------------------------------------------------------------------------------------------------------------------|-------|----------|-----------------------------------------------------------------------------------------|--------------|
| output_file   | Path to the output file for the histogram, including the file extension. If not set, the histogram is displayed on the screen.   | str   | No       | `eps`, `jpg`, `pdf`, `png`, `svg`, `tiff`                                              |              |
| session_name  | Path to the session file containing the QUBO formulations to create the histogram for.                                | str   | No       |                                                                                         | `"matching.mt"` |

#### Example

1. Display the histogram on the screen:
   ```bash
   matchinghub plot-qubo-histogram
   ```

2. Save the histogram to a file named `qubo_histogram.pdf`:
   ```bash
   matchinghub plot-qubo-histogram qubo_histogram.pdf
   ```

3. Save the histogram using QUBO formulations from a custom session file:
   ```bash
   matchinghub plot-qubo-histogram qubo_histogram.png -s custom_session.mt
   ```
---

### `solve-qubo`

Solve QUBO formulations, using classical methods, for the matchings in the specified session file. Metrics for the solutions are also computed against the corresponding ground truth.

#### Arguments

| Argument       | Description                                                                                               | Type  | Required | Range            | Default      |
|----------------|-----------------------------------------------------------------------------------------------------------|-------|----------|------------------|--------------|
| max_variables  | The maximum number of variables in the QUBO formulations to be solved.                                    | int   | No       | >= 0             | No limit |
| start          | The starting index of the range of matchings for which QUBOs will be solved.                              | int   | No       | >= 0             |              |
| end            | The ending index of the range of matchings for which QUBOs will be solved.                                | int   | No       | >= start         |              |
| timeout        | Timeout value in seconds for solving QUBOs.                                                              | int   | No       | > 0              | No timeout |
| override       | If set, existing QUBO solutions will be overwritten.                                                     | flag  | No       | `--override`, `--no-override` | `--no-override` |
| session_file   | Path to the session file containing the QUBOs to solve.                                                  | str   | No       |                  | `"matching.mt"` |

#### Example

1. Solve all QUBOs in the default session file:
   ```bash
   matchinghub solve-qubo
   ```

2. Solve QUBOs with a maximum of 28 variables:
   ```bash
   matchinghub solve-qubo --max-variables 28
   ```

3. Solve QUBOs from index 10 to 50:
   ```bash
   matchinghub solve-qubo --start 10 --end 50
   ```

4. Solve QUBOs with a timeout of 300 seconds:
   ```bash
   matchinghub solve-qubo --timeout 300
   ```

5. Solve QUBOs and overwrite existing solutions:
   ```bash
   matchinghub solve-qubo --override
   ```

6. Solve QUBOs from a custom session file:
   ```bash
   matchinghub solve-qubo -s custom_session.mt
   ```
---
## QAOA Circuits

QAOA circuits are implemented using the Qistkit library.

The following presents commands for working with QAOA circuits.

### `build-qaoa-circuit`

Build QAOA circuits from QUBO formulations in the specified session file. Properties of circuits, including depth and width, are computed.

#### Arguments

| Argument       | Description                                                                                               | Type  | Required | Range            | Default      |
|----------------|-----------------------------------------------------------------------------------------------------------|-------|----------|------------------|--------------|
| p              | The number of layers in the QAOA circuit. Higher values increase the circuit depth.                      | int   | No       | >= 1             | `1`          |
| override       | If set, existing properties of QAOA circuits will be overwritten.                                        | flag  | No       | `--override`, `--no-override` | `--no-override` |
| timeout        | Timeout value in seconds for building individual QAOA circuits.                                          | int   | No       | > 0              | No timeout |
| session_file   | Path to the session file containing the QUBO formulations to build QAOA circuits for.                    | str   | No       |                  | `"matching.mt"` |

#### Example

1. Build QAOA circuits with default settings (1 layer):
   ```bash
   matchinghub build-qaoa-circuit
   ```

2. Build QAOA circuits with 3 layers:
   ```bash
   matchinghub build-qaoa-circuit --p 3
   ```

3. Build QAOA circuits and overwrite existing circuit metadata:
   ```bash
   matchinghub build-qaoa-circuit --override
   ```

4. Build QAOA circuits with a timeout of 300 seconds for each circuit:
   ```bash
   matchinghub build-qaoa-circuit --timeout 300
   ```

5. Build QAOA circuits from a custom session file:
   ```bash
   matchinghub build-qaoa-circuit -s custom_session.mt
   ```
---

### `run-qaoa-circuit`

Execute QAOA circuits from the specified session file. Metrics for the solutions are also computed against the corresponding ground truth.

#### Arguments

| Argument       | Description                                                                                               | Type  | Required | Range            | Default      |
|----------------|-----------------------------------------------------------------------------------------------------------|-------|----------|------------------|--------------|
| shots          | The number of shots for each individual QAOA circuit.                                                    | int   | No       | >= 1             | `1024`       |
| max_width      | The maximum width for QAOA circuits to be executed. Only circuits with a width up to this value are executed. | int   | No       | >= 1             |              |
| override       | If set, existing execution results will be overwritten.                                                  | flag  | No       | `--override`, `--no-override` | `--no-override` |
| session_file   | Path to the session file containing the QAOA circuits to execute.                                         | str   | No       |                  | `"matching.mt"` |

#### Example

1. Run QAOA circuits with default settings (1024 shots):
   ```bash
   matchinghub run-qaoa-circuit
   ```

2. Run QAOA circuits with 2048 shots:
   ```bash
   matchinghub run-qaoa-circuit --shots 2048
   ```

3. Run QAOA circuits with a maximum width of 28:
   ```bash
   matchinghub run-qaoa-circuit --max-width 28
   ```

4. Run QAOA circuits and overwrite existing execution results:
   ```bash
   matchinghub run-qaoa-circuit --override
   ```

5. Run QAOA circuits for a custom session file:
   ```bash
   matchinghub run-qaoa-circuit -s custom_session.mt
   ```
---

### `plot-qubo-qaoa-dist`

Produces a box plot of the distribution of QAOA circuits according to their depth, grouped by the size of the QUBO formulations from which they were built.

#### Arguments

| Argument      | Description                                                                                                            | Type  | Required | Range                                                                                   | Default      |
|---------------|------------------------------------------------------------------------------------------------------------------------|-------|----------|-----------------------------------------------------------------------------------------|--------------|
| output_file   | Path to the output file for the plot, including the file extension. If not set, the plot is displayed on the screen.   | str   | No       | `eps`, `jpg`, `pdf`, `png`, `svg`, `tiff`                                              |              |
| session_file  | Path to the session file containing the QUBO and QAOA circuit data for plotting.                                      | str   | No       |                                                                                         | `"matching.mt"` |

#### Example

1. Display the box plot on the screen:
   ```bash
   matchinghub plot-qubo-qaoa-dist
   ```

2. Save the box plot to a file named `qubo_qaoa_dist.pdf`:
   ```bash
   matchinghub plot-qubo-qaoa-dist qubo_qaoa_dist.pdf
   ```

3. Save the box plot using data from a custom session file:
   ```bash
   matchinghub plot-qubo-qaoa-dist qubo_qaoa_dist.png -s custom_session.mt
   ```
---

### `plot-qaoa-dist`

Produces a scatter plot of the distribution of QAOA circuits according to their width and depth.

#### Arguments

| Argument      | Description                                                                                                            | Type  | Required | Range                                                                                   | Default      |
|---------------|------------------------------------------------------------------------------------------------------------------------|-------|----------|-----------------------------------------------------------------------------------------|--------------|
| output_file   | Path to the output file for the plot, including the file extension. If not set, the plot is displayed on the screen.   | str   | No       | `eps`, `jpg`, `pdf`, `png`, `svg`, `tiff`                                              |              |
| session_file  | Path to the session file containing the QAOA circuit data for plotting.                                               | str   | No       |                                                                                         | `"matching.mt"` |

#### Example

1. Display the scatter plot on the screen:
   ```bash
   matchinghub plot-qaoa-dist
   ```

2. Save the scatter plot to a file named `qaoa_dist.pdf`:
   ```bash
   matchinghub plot-qaoa-dist qaoa_dist.pdf
   ```

3. Save the scatter plot using data from a custom session file:
   ```bash
   matchinghub plot-qaoa-dist qaoa_dist.png -s custom_session.mt
   ```
---

### `plot-qaoa-histogram`

Produces a histogram of QAOA circuits according to width.

#### Arguments

| Argument      | Description                                                                                                            | Type  | Required | Range                                                                                   | Default      |
|---------------|------------------------------------------------------------------------------------------------------------------------|-------|----------|-----------------------------------------------------------------------------------------|--------------|
| output_file   | Path to the output file for the plot, including the file extension. If not set, the plot is displayed on the screen.   | str   | No       | `eps`, `jpg`, `pdf`, `png`, `svg`, `tiff`                                              |              |
| session_file  | Path to the session file containing the QAOA circuit data for plotting.                                               | str   | No       |                                                                                         | `"matching.mt"` |

#### Example

1. Display the histogram on the screen:
   ```bash
   matchinghub plot-qaoa-histogram
   ```

2. Save the histogram to a file named `qaoa_histogram.pdf`:
   ```bash
   matchinghub plot-qaoa-histogram qaoa_histogram.pdf
   ```

3. Save the histogram using data from a custom session file:
   ```bash
   matchinghub plot-qaoa-histogram qaoa_histogram.png -s custom_session.mt
   ```
---
## Results

### `print-recall-gt`

Produces a comparison of the mean Recall@GT metric between matchings obtained from schema matching algorithms, QAOA circuits, and QUBO optimisation.

#### Arguments

| Argument      | Description                                                                                           | Type  | Required | Range              | Default      |
|---------------|-------------------------------------------------------------------------------------------------------|-------|----------|--------------------|--------------|
| group         | Group to filter by: 'qubo' for QUBO optimisation or 'qaoa' for QAOA circuits.                         | str   | Yes      | `qubo`, `qaoa`    |              |
| session_file  | Path to the session file containing the data for computing Recall@GT metrics.                         | str   | No       |                    | `"matching.mt"` |

#### Example

1. Print Recall@GT comparison for QUBO optimisation:
   ```bash
   matchinghub print-recall-gt qubo
   ```

2. Print Recall@GT comparison for QAOA circuits:
   ```bash
   matchinghub print-recall-gt qaoa
   ```

3. Print Recall@GT comparison for a custom session file:
   ```bash
   matchinghub print-recall-gt qubo -s custom_session.mt
   ```
