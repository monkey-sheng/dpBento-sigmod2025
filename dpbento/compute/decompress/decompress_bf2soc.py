from dataclasses import dataclass
from typing import Any, Optional, Set, FrozenSet
from dpbento.benchmark_base import \
BenchmarkCategory, BenchmarkItem, BenchmarkMetadata, BenchmarkParameters, BenchmarkOutputStructure, HWPlatform


# the master runner shall pick up these declarations and run the benchmarks accordingly

# declare the output structure here, as a dataclass
@dataclass
class DecompressBF2OutputStructure(BenchmarkOutputStructure):
    latency: type = float
    throughput: type = float

# declare the metadata here,
@dataclass
class DecompressBF2Metadata(BenchmarkMetadata):
    name: str = "decompress_bf2"
    desc: str = "Decompress raw deflate on BF2 SoC"
    category: FrozenSet[BenchmarkCategory] = frozenset({BenchmarkCategory.ACCELERATOR})
    output_structure: BenchmarkOutputStructure = DecompressBF2OutputStructure()
    platform: HWPlatform = HWPlatform.BF2


## declare the parameters here, each as an inherited dataclass of BenchmarkParameters

param_block_size = BenchmarkParameters[int](
    '-s', '--block_size',
    'Block/chunk size to decompress per call, default 4096',
    4096)
    
param_num_workers = BenchmarkParameters[int](
    '-w', '--workers',
    'Number of worker threads to use, default 1',
    1)

## this benchmark has 2 parameters, block size and number of workers

params_set: FrozenSet[BenchmarkParameters[Any]] = frozenset({
    param_block_size,
    param_num_workers
    })

# complete the abstract class with the actual implementation, runner should pick this up automatically
class DecompressBF2SoC(BenchmarkItem):
    def __init__(self, params: FrozenSet[BenchmarkParameters[Any]], metadata: BenchmarkMetadata) -> None:
        super().__init__(params, metadata)

    def initialize(self) -> bool:
        # do whatever initialization here, call external shell scripts, or whatever
        init_result = False
        pass
        return init_result
    
    def run(self) -> bool:
        run_result = False
        pass
        # do the actual running here, call external shell scripts, or whatever
        return run_result
