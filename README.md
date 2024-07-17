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

## How to configure the Json file as Dpu benchmark input(storage_test)

Check the example `/configs_user/customize_test.json` file and customize the experiment.

Sample JSON File
```
{
    "benchmark_name": "storage_test",
    "test_parameters": {
        "numjobs": [4],
        "block_sizes": ["1m", "2m", "4m", "8m", "16m", "32m"],
        "size": ["1G"],
        "runtime": ["30s"],
        "direct": [1],
        "iodepth": [32],
        "io_engine": ["io_ring"],
        "test_lst": ["randwrite", "randread", "write", "read"]
    },
    "dpdento_root": "/path/to/your/DPU_bench",
    "output_folder": "/path/to/your/output_folder"
}
```
### Step 1: Define Benchmark Name

Enter the name of the benchmark test in the `benchmark_name` field.

`"benchmark_name": "storage_test"`

### Step 2: Set Test Parameters
In the `test_parameters` field, define the various test parameters. Parameters include:

- **numjobs**: Number of jobs. This sets the number of threads or processes performing the I/O operations.  
  **Default value**: `[4]`  
  **Possible values**: Any positive integer (e.g., `[1]`, `[2]`, `[4]`, `[8]`).

- **block_sizes**: Block sizes. This specifies the sizes of the I/O operations.  
  **Default value**: `["1m"]`  
  **Possible values**: Any valid size string (e.g., `["1m"]`, `["2m"]`, `["4m"]`, `["8m"]`, `["16m"]`, `["32m"]`).

- **size**: Test file size. This sets the total size of the data to be tested.  
  **Default value**: `["1G"]`  
  **Possible values**: Any valid size string (e.g., `["1G"]`, `["2G"]`, `["4G"]`).

- **runtime**: Runtime duration. This sets the duration for which the test should run.  
  **Default value**: `["30s"]`  
  **Possible values**: Any valid time string (e.g., `["10s"]`, `["30s"]`, `["1m"]`).

- **direct**: Whether to use direct I/O. Direct I/O bypasses the buffer cache and performs raw I/O operations.  
  **Default value**: `[1]`  
  **Possible values**: `[0]` (disabled), `[1]` (enabled).

- **iodepth**: I/O depth. This sets the number of I/O operations to queue in advance.  
  **Default value**: `[32]`  
  **Possible values**: Any positive integer (e.g., `[1]`, `[16]`, `[32]`, `[64]`).

- **io_engine**: I/O engine. This specifies the I/O engine to be used for the operations.  
  **Default value**: `["io_ring"]`  
  **Possible values**: `["sync"]`, `["libaio"]`, `["io_uring"]`, `["mmap"]`, `["splice"]`.

- **test_lst**: List of tests. This specifies the types of I/O tests to perform.  
  **Default value**: `["randwrite"]`, `["randread"]`, `["write"]`, `["read"]`  
  **Possible values**: `["randwrite"]`, `["randread"]`, `["write"]`, `["read"]`, `["trim"]`, `["randtrim"]`.
  
### Step 3: Specify Paths
Enter the root directory path for the DPU benchmark in the `dpdento_root` field, and the output folder path in the `output_folder` field. For example:

`"dpdento_root": "/path/to/your/DPU_bench"`,

`"output_folder": "/path/to/your/output_folder"`

## How to Run the customize experiment by DPU-bench

`cd DPU-bench`

The `setup` script will install all dependencies and packages that we need

`python setup.py`

Assumption: User already configure the `/configs_user/customize_test.json` file.

`python3 run_dpbento.py`


