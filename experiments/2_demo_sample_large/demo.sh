#!/bin/bash

echo "Hi!"
echo "Welcome to the MatchingHub demo on large data instances!"

if [ -f "matching.mt" ] || [ -d "matching" ]; then
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

echo "> Running algorithms (no timeout)"
matchinghub run

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

echo "> Formulating stable marriage problems as QUBO"
matchinghub formulate-qubo

echo "> Producing QUBO scatter plot"
matchinghub plot-qubo-dist "3_qubo_dist.pdf"

echo "> Producing QUBO histogram"
matchinghub plot-qubo-histogram "4_qubo_histogram.pdf"

echo "> Solving QUBO formulations (no max variable limit)"
matchinghub solve-qubo

echo "> Comparing Recall@GT for QUBO solutions"
matchinghub print-recall-gt qubo

echo "> Building QAOA circuits (p=1, no timeout)"
matchinghub build-qaoa-circuit

echo "> Producing QUBO-QAOA scatter plot"
matchinghub plot-qubo-qaoa-dist "5_qubo_qaoa_dist.pdf"

echo "> Producing QAOA scatter plot"
matchinghub plot-qaoa-dist "6_qaoa_dist.pdf"

echo "> Producing QAOA histogram"
matchinghub plot-qaoa-histogram "7_qaoa_histogram.pdf"

echo "> Running QAOA circuits (shots=1024, no max width limit)"
matchinghub run-qaoa-circuit

echo "> Comparing Recall@GT for QAOA solutions"
matchinghub print-recall-gt qaoa

echo "Bye!"