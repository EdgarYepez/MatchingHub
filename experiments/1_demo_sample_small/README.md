# MatchingHub: Demo on Small Data Instances

This repository includes an automation script, `demo.sh`, designed to showcase the schema matching pipeline on small data scenarios. The scenarios are retrieved from a central repository according to their identifiers as specified in the `scenarios.txt` file. 

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

#### 1. _Schematch/Pubs/pubs1_pubs5/discounts >> target_discounts

##### Source Relation: `discount`

**Attributes**:

- `discounttype`
- `stor_id`
- `lowqty`
- `highqty`
- `discount`

##### Target Relation: `target_discount`

**Attributes**:

- `discounttype`
- `stor_id`
- `lowqty`
- `highqty`
- `discount`

##### Ground Truth

- `discount.discounttype` ↔ `target_discount.discounttype`
- `discount.stor_id` ↔ `target_discount.stor_id`
- `discount.lowqty` ↔ `target_discount.lowqty`
- `discount.highqty` ↔ `target_discount.highqty`
- `discount.discount` ↔ `target_discount.discount`

#### 2. _Schematch/DeNorm/Books1/Books >> Borrow

##### Source Relation: `books`

**Attributes**:

- `BookID`
- `Title`
- `BorrowerID`
- `BorrowerName`
- `DueDate`

##### Target Relation: `borrow`

**Attributes**:

- `ID`
- `Name`
- `Person`
- `PName`
- `Date`

##### Ground Truth

- `books.BookID` ↔ `borrow.ID`
- `books.Title` ↔ `borrow.Name`
- `books.BorrowerID` ↔ `borrow.Person`
- `books.BorrowerName` ↔ `borrow.PName`
- `books.DueDate` ↔ `borrow.Date`