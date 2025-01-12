#!/bin/bash

echo "Hi!"
echo "Welcome to the MatchingHub experiment results!"

echo "> Producing scenario scatter plot"
matchinghub plot-scenario-dist "1_scenario_dist.pdf"

echo "> Producing matching scatter plot according to Recall@GT"
matchinghub plot-match-dist "2_match_dist.pdf"

echo "> Generating complexity class view (ILT: NP-hard, CLTO: P-solvable classic, CLT/ILTO: P-solvable)"
matchinghub view-class

echo "> Producing QUBO scatter plot"
matchinghub plot-qubo-dist "3_qubo_dist.pdf"

echo "> Producing QUBO histogram"
matchinghub plot-qubo-histogram "4_qubo_histogram.pdf"

echo "> Comparing Recall@GT for QUBO solutions"
matchinghub print-recall-gt qubo

echo "> Producing QUBO-QAOA scatter plot"
matchinghub plot-qubo-qaoa-dist "5_qubo_qaoa_dist.pdf"

echo "> Producing QAOA scatter plot"
matchinghub plot-qaoa-dist "6_qaoa_dist.pdf"

echo "> Producing QAOA histogram"
matchinghub plot-qaoa-histogram "7_qaoa_histogram.pdf"

echo "> Comparing Recall@GT for QAOA solutions"
matchinghub print-recall-gt qaoa

echo "Bye!"