# DP-Bento

A customizable and modular benchmarking framework for DPU & SmartNICs
Uses standard Python as the driver and automatically handles dependencies of all benchmarks.

## Development environment setup

We recommend at least Python 3.8 or higher.


## Experiment Configuration Guide (Developer)

Refer to the `/configs_user` directory to learn about the configuration details and to customize the experiments.

### Adding a New Configuration Directory

You can create your own configuration directories as needed. For instance, if you want to add a new configuration directory called `compression`, you can create the following path:
`/configs_user/compression/compression_test.json`

### Designing `compression_test.json`

Additionally, you will need to design the `compression_test.json` file. Below is a sample configuration:

Define your own parameters and metrics based on the specific needs of your experiment

```
{
    "benchmarks": [
        {
            "benchmark_class": "compression",
            "benchmark_items": ["Specify the tool you intend to use"],
            "parameters": {
                "algorithm": [algo],
                "seconds": [3,5,10],
                "bytes": [4,8],
                "multi": [2],
                "async_jobs": [4],
                "misalign": [0]
            },
            "metrics": [A,B,C]
        }
    ]
}
```
The key point is that the json file needs to have this specific structure, the actual parameters can be whatever you want them to be.

## Create Benchmark `compression`

Create a new directory named `compression` (ensure that the directory name matches the `benchmark_class` field in your JSON file).

There are four scripts you need to create in this directory: `prepare.py`, `report.py`, `run.py`, and `clean.py`.

### `prepare.py`

This script is responsible for installing all dependencies and performing necessary configurations for the benchmark.

### `run.py`

This script receives commands from `run_dpbento.py`. The `run_dpbento.py` script will pass the arguments for the Cartesian product of the parameters defined in your JSON file's `parameters` field. However, the `metrics` field will not be included in this Cartesian product.

For example, based on the JSON file provided earlier, `run.py` will receive the following commands invoked by `run_dpbento.py`:


```
run.py --algorithm [algo] --seconds [3] --bytes [4] --muti[2] --async_jobs[4] --msalign[0] --metrics[A,B,C]
 run.py --algorithm [algo] --seconds [5] --bytes [4] --muti[2] --async_jobs[4] --msalign[0] --metrics[A,B,C]
 run.py --algorithm [algo] --seconds [10] --bytes [4] --muti[2] --async_jobs[4] --msalign[0] --metrics[A,B,C]
 run.py --algorithm [algo] --seconds [3] --bytes [8] --muti[2] --async_jobs[4] --msalign[0] --metrics[A,B,C]
 run.py --algorithm [algo] --seconds [5] --bytes [8] --muti[2] --async_jobs[4] --msalign[0] --metrics[A,B,C]
 run.py --algorithm [algo] --seconds [10] --bytes [8] --muti[2] --async_jobs[4] --msalign[0] --metrics[A,B,C]
```

Ensure that your `run.py` script is equipped to handle these commands and their respective arguments.

### `report.py`

This script will receive the `metrics` passed from `run_dpbento.py` and generate an `output.csv` file under your benchmark directory, capturing the results of the run.

### `clean.py`

When the user executes the command:
`python3 run_dpbento.py --config /configs_user/compression/compression_test.json --clean`


This script will remove all dependencies installed during the preparation phase and delete any intermediate files generated during the benchmark.

## Run Benchmark(s), e.g. using the `compression` configuration

`python3 run_dpbento.py --config /configs_user/compression/compression_test.json`

## Results

All results should be automatically generated into the `output/` directory, within sub directories of the corresponding name, e.g., `output/compression/`. The results should be all in CSV format.

