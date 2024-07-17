from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, FrozenSet
from benchmark_base import \
BenchmarkCategory, BenchmarkItem, BenchmarkMetadata, BenchmarkParameters, BenchmarkParametersSet,\
BenchmarkOutputStructure, HWPlatform


# the master runner shall pick up these declarations and run the benchmarks accordingly

# declare the output structure here, as a dataclass
@dataclass
class DecompressBF2OutputStructure(BenchmarkOutputStructure):
    latency: type = float
    throughput: type = float

# declare the metadata here
@dataclass
class DecompressBF2Metadata(BenchmarkMetadata):
    name: str = "decompress_bf2"
    desc: str = "Decompress raw deflate on BF2 SoC"
    category: FrozenSet[BenchmarkCategory] = frozenset({BenchmarkCategory.ACCELERATOR})
    output_structure: BenchmarkOutputStructure = DecompressBF2OutputStructure()
    platform: HWPlatform = HWPlatform.BF2

# declare all the parameters/inputs here, put them in a dataclass
# the BenchmarkItem will be passed an instance with the parameters set from the master runner aka command line
# for numerical values, like int here, you can optionally specify the range here, which the master runner will enforce
@dataclass
class DecompressBF2Params(BenchmarkParametersSet):
    block_size: BenchmarkParameters[int]
    num_workers: BenchmarkParameters[int]

# declare/specify the parameters here, each as an inherited dataclass of BenchmarkParameters
param_block_size = BenchmarkParameters[int](
    '-s', '--block_size',
    'Block/chunk size to decompress per call, default 4096',
    4096,
    parse_func=lambda x: int(x)
    )
    
param_num_workers = BenchmarkParameters[int](
    '-w', '--workers',
    'Number of worker threads to use, default 1',
    1,
    choices=range(1, 8)
    )

# then instantiate the BenchmarkParametersSet with these parameters
# the master runner will automatically pick it up and populate it from the command line
# TODO: on parse error, exit or continue with default values?
params_set = DecompressBF2Params(param_block_size, param_num_workers)

# param_query_numbers = BenchmarkParameters[List[int]](
#     '-q', '--query_numbers',
#     'list of queries to run, default all queries',
#     [1, 2, 3, 4, 5],
#     parse_func=lambda x: [int(i) for i in x.split(',')]
# )

### in short: this benchmark has 2 parameters, block size and number of workers
### and we've specified our parameters like above

# as implementor, we complete the abstract class with the actual implementation
# master runner should pick this class up automatically
class DecompressBF2SoC(BenchmarkItem):
    def __init__(self, params: DecompressBF2Params, metadata: BenchmarkMetadata) -> None:
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
