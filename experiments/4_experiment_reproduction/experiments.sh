#!/bin/bash

echo "Hi!"
echo "Welcome to the MatchingHub complete experiment suit!"

if [ -f "matching.mt" ] || [ -d "matching" ] || [ -f "matching_uq_ilt.mt" ] || [ -d "matching_uq_ilt" ]; then
    echo "Session files already exist! No data will be overwritten. Plots will be regenerated."
fi

echo "> Initialising session file 'matching.mt'"
matchinghub initialise

echo "> Importing algorithms"
matchinghub import-algorithms algorithms.ini

echo "> Importing scenarios"
matchinghub import-scenarios scenarios.txt

echo "> Producing scenario scatter plot"
matchinghub plot-scenario-dist "1_scenario_dist.pdf"

echo "> Running algorithms (timeout=300s)"
matchinghub run --direction both --timeout 300

echo "> Producing matching scatter plot according to Recall@GT"
matchinghub plot-match-dist "2_match_dist.pdf"

echo "> Running discretisation"
matchinghub compute-discretisation

echo "> Computing hash sum"
matchinghub compute-hash

echo "> Computing preference lists and related properties"
matchinghub compute-features

echo "> Generating complexity class view (ILT: NP-hard, CLTO: P-solvable classic, CLT/ILTO: P-solvable)"
matchinghub view-class

echo "> Exporting unique NP-hard matchings to 'matching_uq_ilt.mt'"
matchinghub export-uniques-by-class --complexity ilt matching_uq_ilt.mt

echo "> Switching to 'matching_uq_ilt.mt'"

echo "> Formulating stable marriage problems as QUBO"
matchinghub formulate-qubo -s matching_uq_ilt.mt

echo "> Producing QUBO scatter plot"
matchinghub plot-qubo-dist "3_qubo_dist.pdf" -s matching_uq_ilt.mt

echo "> Producing QUBO histogram"
matchinghub plot-qubo-histogram "4_qubo_histogram.pdf" -s matching_uq_ilt.mt

echo "> Solving QUBO formulations (max variables: 28)"
matchinghub solve-qubo --max-variables 28 -s matching_uq_ilt.mt

echo "> Comparing Recall@GT for QUBO solutions"
matchinghub print-recall-gt qubo -s matching_uq_ilt.mt

echo "> Building QAOA circuits (p=1, timeout=600s)"
matchinghub build-qaoa-circuit --p 1 --timeout 600 -s matching_uq_ilt.mt

echo "> Producing QUBO-QAOA scatter plot"
matchinghub plot-qubo-qaoa-dist "5_qubo_qaoa_dist.pdf" -s matching_uq_ilt.mt

echo "> Producing QAOA scatter plot"
matchinghub plot-qaoa-dist "6_qaoa_dist.pdf" -s matching_uq_ilt.mt

echo "> Producing QAOA histogram"
matchinghub plot-qaoa-histogram "7_qaoa_histogram.pdf" -s matching_uq_ilt.mt

echo "> Running QAOA circuits (shots=1024, max width: 28)"
matchinghub run-qaoa-circuit --shots 1024 --max-width 28 -s matching_uq_ilt.mt

echo "> Comparing Recall@GT for QAOA solutions"
matchinghub print-recall-gt qaoa -s matching_uq_ilt.mt

echo "Bye!"