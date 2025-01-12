# MatchingHub

This repository contains the source code for the CLI MatchingHub utility, along with scripts and data to support experiment reproduction.

The application and experiments focus on evaluating a schema matching pipeline designed to address uncertainty. This is achieved by expressing a schema matching scenario as a stable marriage problem and solving it through QUBO formulations and QAOA circuits. Refer to the main written report for details.

The tool provides a final comparison of the accuracy achieved by the different solution approaches against the results obtained from executing state-of-the-art schema matching algorithms without further processing.

## Organisation

The repository is organised into two main directories: `src` and `experiments`. A third directory called `dkr` serves as a placeholder for running the application on Docker, as introduced later on.

### Source and data sets

The `src` directory stores the main source code of the application alongside archives packing data sets for schema matching. 

The application is implemented as a CLI utility based on Python 3.10. It is organised into modules dedicated to managing schema matching data sets, running schema matching pipelines, and plotting resulting experiment data and statistics.

The module for managing data sets is stored in the `schema_matching_scenarios` directory. Inside, archives pack data scenarios from two different external repositories: the Valentine framework and the Schematch project. Appropriate references to the source repositories sit alongside the archives in dedicated folders. Instructions on how to unpack the archives are provided in the corresponding `README.md` files. Refer to the [scenario usage guide](./src/schema_matching_scenarios/README.md) for details about the repositories.

### Experiments

The  `experiments` directory contains four automation shell scripts to run the MatchingHub application, each stored in dedicated subdirectories.

Two scripts are designed as toy examples of running the complete schema matching pipeline on both a *small* and a *large* data scenario. The scripts sit in the `1_demo_sample_small` and `2_demo_sample_large` directories respectively. Each script represents a standalone pipeline and thus already contains references to the required input data. Details about the scripts is presented in the corresponding `README.md` file.

A third script, stored in the `3_experiment_final_data_and_plots` directory, is designed to produce the plots from the main performed experiments. The resulting data from the experiments sits alongside the script in order to support generation of the plots. It also allows for manual exploration. Details about this data and the script is presented in the corresponding `README.md` file.

One last script, stored in the `4_experiment_reproduction` directory, is designed for completely reproducing the main experiments from start to end. It packs references to the required input data and is configured according to considerations presented in the main written report. A `README.md` file presents details about the script.

## Installation

MatchingHub depends on a number of external libraries. To ease execution and usage of the application, this repository packs a Docker configuration file for seamless bootstrap of the appropriate running environment.

### Docker

A stable installation of Docker is required to use this repository.

Clone this repository and build a Docker image from the provided configuration file with the following command:

```
docker build -t mthub . --no-cache
```

The image will be created with the appropriate versions of the dependencies, as well as the main source code and data scenarios.  The configuration file is designed to install the MatchingHub application as a system-wide command invoked as `matchinghub`. See `Dockerfile` for more details.

Run an interactive container based on the created image with the following command:

```
docker run -it -v ./dkr:/home/dkr mthub bash
```

The container will boot up directly to the `experiments` directory, from where the whole setup and experiments can be executed by running the corresponding automation scripts.

The command will configure the `dkr` directory as a shared virtual folder inside the container. This folder can be used to bridge plots and data produced inside the container out to the host system.

**Note:** On Windows host systems, a `\` character should be used in place of the `/` character as part of the definition of the host placeholder directory in the command. Concretely, the full argument should be: `-v .\dkr:/home/dkr`.

Inside the container, execute the following command in order to test for a successful installation:

```
matchinghub --help 
```

A list of all available commands to the MatchingHub application will be displayed.

## Usage guide

Refer to the [usage guide](./Usage.md) for a complete description of the MatchingHub commands as well as practical usage examples.

