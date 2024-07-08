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