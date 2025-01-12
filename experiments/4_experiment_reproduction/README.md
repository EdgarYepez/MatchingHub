# MatchingHub: Experiment Reproduction

This repository includes an automation script, `experiments.sh`, designed to perform the complete experiments presented in the written report associated to MatchingHub.

### Execution

Run the experiment automation script with the following command:

```
./experiments.sh
```

Inspect the generated QUBO formulations, the printed tables, and the generated `.pdf` plots.

**Note:** The total uninterrupted running time for the experiments takes over 2.5 months and consumes over 60GB of storage.

### Data

The `scenarios.txt` file retrieves 835 scenarios from the centralised repository.

The `algorithms.ini` file describes 164 total configurations for initialising Valentine algorithms.