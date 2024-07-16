from dataclasses import dataclass
from typing import Any, Optional, Set, FrozenSet
from benchmark_base import \
BenchmarkCategory, BenchmarkItem, BenchmarkMetadata, BenchmarkParameters, BenchmarkOutputStructure, HWPlatform

# if bf2 and bf3 are super similar, then we can just piggyback off of bf2 with something like this
# TODO: check if this actually works in master runner
from .decompress_bf2soc import\
    DecompressBF2OutputStructure as DecompressBF3OutputStructure,\
    DecompressBF2Metadata as DecompressBF3Metadata,\
    params_set,\
    DecompressBF2SoC as DecompressBF3SoC

