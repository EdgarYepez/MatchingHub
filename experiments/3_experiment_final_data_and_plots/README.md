# MatchingHub: Experiment Results

This folder contains the data resulting from the experiments described in the written report, and packs the following files:

#### **1. `qubo_qaoa_matchings.mt.zip`**
- Uncompresses to a file named `qubo_qaoa_matchings.mt`, which is a plain SQLite database file. It stores the results of the experiments, including:
  - 8139 unique matchings: NP-hard stable marriage problems.
  - 8139 references to QUBO formulations.
  - 3963 QAOA circuits.
  - 1597 QAOA solutions.
  - 1597 QUBO solutions.

#### **2. `qubo_qaoa_matchings_formulations.zip`**
- Multipart archive that uncompresses to 8139 individual `.lp` files, each representing a QUBO formulation produced during the experiments.
- The archive is composed of five 400MB part files with extension `.z01`, `.z02`, `.z03`, `.z04`, `.z05`, and one 300MB head file with extension `.zip`.
- The uncompressed files are stored inside a folder named `qubo_qaoa_matchings`. 
- The total uncompressed size is approximately 60GB.
- **Note:** The uncompressed `qubo_qaoa_matchings` folder must sit alongside the main `qubo_qaoa_matchings.mt` file in order for the MatchingHub application to load the QUBO formulations.

#### **3. `plots.sh`**
- Automation script for producing the plots presented in the final written report.
- It requires the `qubo_qaoa_matchings.mt` file only. Decompressing `qubo_qaoa_matchings_formulations.zip` is not necessary to produce the plots or exploring data.

### Execution

Run the experiment automation script with the following command:

```
./plots.sh
```

Inspect the printed tables as well as the generated `.pdf` plots. If running the automation script on the provided docker container with the default boot up configuration, use the following command to bridge the generated plots out to the main host system:

```
mv 1_scenario_dist.pdf 2_match_dist.pdf 3_qubo_dist.pdf 4_qubo_histogram.pdf 5_qubo_qaoa_dist.pdf 6_qaoa_dist.pdf 7_qaoa_histogram.pdf ../dkr/
```