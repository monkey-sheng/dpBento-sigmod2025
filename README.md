# DP-Bento

A customizable and modular benchmarking framework for DPU & SmartNICs
Uses standard Python as the driver program without any extra package dependencies (I hope, //TODO: add requirements if extra packages needed)

## Development environment setup

Install this as a pip package. First go to the root directory `cd dpbento`, then

```
pip -e install .
```

The base is at `benchmark_base.py`, take a look at the mock example at `compute/`, how it's structured and especially `decompress_bf2soc.py` for a concrete example. Also, for identical or highly similar benchmarks, we can probably piggyback off of just one, for example take a look at `decompress_bf3soc.py`

## Extension guide

DP-Bento will come with a set of prebuilt "bento boxes" of benchmarks, in 6 categories:

- compute
- memory
- data movement (including network)
- storage
- hardware accelerators
- end-to-end apps

DP-Bento will also allow the use of external user supplied "bento boxes" of benchmarks, for flexibility and extensibility. //TODO: this is still WIP


## How to configure the Json file as Dpu benchmark input(end_to_end_test)

Check the example `/configs_user/customize_test.json` file and customize the experiment.

Sample JSON File

{
    "benchmark_name": "e2e_test",
    "test_parameters": {
        "scale_factors": [1, 3, 10],
        "query_numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    },
    "dpdento_root": "/path/to/your/DPU_bench",
    "output_folder": "/path/to/your/output_folder"
}


### Step 1: Define Benchmark Name

Enter the name of the benchmark test in the `benchmark_name` field.

`"benchmark_name": "e2e_test"`

### Step 2: Set Test Parameters

[](https://github.com/fardatalab/DPU-bench/tree/Chihan_Storage_test#step-2-set-test-parameters)

In the `test_parameters` field, define the various test parameters. Parameters include:

* **scale_factors** : Define a list of different scale factors. Possible values are any positive integers.
* **query_numbers** : Define a list of different query numbers. Possible values are any integers between 1 and 22.

Enter the root directory path for the DPU benchmark in the `dpdento_root` field, and the output folder path in the `output_folder` field. For example:

`"dpdento_root": "/path/to/your/DPU_bench"`,

`"output_folder": "/path/to/your/output_folder"`

## How to Run the customize experiment by DPU-bench `cd DPU-bench`

The `setup` script will install all dependencies and packages that we need

`python setup.py`

Assumption: User already configure the `/configs_user/customize_test.json` file.

`python3 run_dpbento.py`
