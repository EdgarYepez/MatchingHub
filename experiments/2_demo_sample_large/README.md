# MatchingHub: Demo on Large Data Instances

This repository includes an automation script, `demo.sh`, designed to showcase the schema matching pipeline on large data scenarios. The scenarios are retrieved from a central repository according to their identifiers as specified in the `scenarios.txt` file. 

The pipeline executes matching algorithms, as specified in the `algorithms.ini` file, over the scenarios to produce a set of matchings. These matchings are then transformed into instances of the stable marriage problem and subsequently solved using both QUBO formulations and QAOA circuits. Finally, a table is presented comparing the Recall@GT measure of these solution approaches against the baseline execution of the matching algorithms.

### Execution

Run the experiment automation script with the following command:

```
./demo.sh
```

Inspect the generated QUBO formulations, the printed tables, and the generated `.pdf` plots. If running the automation script on the provided docker container with the default boot up configuration, use the following command to bridge the generated plots out to the main host system:

```
mv 1_scenario_dist.pdf 2_match_dist.pdf 3_qubo_dist.pdf 4_qubo_histogram.pdf 5_qubo_qaoa_dist.pdf 6_qaoa_dist.pdf 7_qaoa_histogram.pdf ../dkr/
```

### Scenarios

The `scenarios.txt` file retrieves the following scenarios for pipeline execution:

#### 1. _Valentine/ChEMBL/Joinable/assays_both_50_50_ac2_ev/source>>target

##### Source Relation: `source`

**Attributes**:

- `assay_id`
- `assay_type`
- `assay_test_type`
- `assay_tax_id`
- `assay_strain`
- `tid`
- `curated_by`
- `description`
- `src_assay_id`
- `chembl_id`
- `assay_category`
- `doc_id`
- `assay_organism`
- `assay_tissue`
- `assay_cell_type`
- `assay_subcellular_fraction`
- `relationship_type`

##### Target Relation: `target`

**Attributes**:

- `ASI`
- `ASSTY`
- `ASTTY`
- `ASSTI`
- `ASSTR`
- `Ti`
- `CURB`
- `Des`
- `SRASSI`
- `CHEI`
- `ASCATE`
- `CONSC`
- `SI`
- `CI`
- `BFOR`
- `TII`
- `VARII`

##### Ground Truth

- `source.assay_id` ↔ `target.ASI`
- `source.assay_type` ↔ `target.ASSTY`
- `source.assay_test_type` ↔ `target.ASTTY`
- `source.assay_tax_id` ↔ `target.ASSTI`
- `source.assay_strain` ↔ `target.ASSTR`
- `source.tid` ↔ `target.Ti`
- `source.curated_by` ↔ `target.CURB`
- `source.description` ↔ `target.Des`
- `source.src_assay_id` ↔ `target.SRASSI`
- `source.chembl_id` ↔ `target.CHEI`
- `source.assay_category` ↔ `target.ASCATE`