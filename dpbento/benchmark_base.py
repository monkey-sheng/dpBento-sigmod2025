'''
This is a collection of base classes that the bento box benchmark implementers should inherit from.
The core class is `BenchmarkItem`, which is the base class for all benchmarks.
'''

from abc import ABC, abstractmethod
from enum import IntEnum
import argparse as ap
from dataclasses import dataclass

from typing import List, Optional, Set, Generic, Type, TypeVar, FrozenSet


class HWPlatform(IntEnum):
    '''
    Which hardware platform this test runs on
    '''
    # TODO: design decision to be made here.
    # do I want a single test to run on multiple platforms? or separate tests for each platform?
    HOST = 1
    BF2 = 2
    BF3 = 3
    UNDEFINED_LAST = 4  # keep this last

class BenchmarkCategory(IntEnum):
    '''
    The category of the benchmark.
    '''
    CPU = 1
    MEMORY = 2
    STORAGE = 3
    DATA_MOVEMENT = 4
    ACCELERATOR = 5
    END2END = 6
    UNDEFINED_LAST = 7  # keep this last


@dataclass
class BenchmarkOutputStructure(ABC):
    '''
    This is the structure of the output, e.g., csv file, for the test.
    Others who wish to use this can query this bento box to know what to expect as its output.

    Each test bento box should provide their own output structure's concrete class.
    '''
    ### latency: type = float
    ### throughput: type = float
    # something more

@dataclass
class BenchmarkMetadata:
    '''
    Relevant metadata pertaining to this test.
    '''
    name: str  # name of the test, should be unique
    desc: str  # succint description of the test, print out in help message
    category: FrozenSet[BenchmarkCategory]  # the category(s) of the test
    output_structure: BenchmarkOutputStructure  # the structure of the output of the test
    
    # TODO: singular or plural, I'm inclined with singular
    platform: HWPlatform  # which platform this test runs on
    # TODO: somthing more?


T = TypeVar("T")  # type for one of all the actual params used by this bento box
@dataclass(eq=True, frozen=True)
class BenchmarkParameters(Generic[T]):
    '''
    Parameters for the test, this will be parsed by the master runner.
    It is parameterized over the type of the actual param type, e.g. if --job_size takes an int, so T=int.

    Attributes:
        short_arg (Optional[str]): The short option flag, e.g. -i. This is optional.
        long_arg (str): The long option flag, e.g. --input. This is required.
        param_type (T): The type of the parameter, e.g. int, float, str, etc.
        help_str (str): The help message for this argument.
        default (Optional[T]): The default value for this argument.
    '''

    short_arg: Optional[str]
    long_arg: str
    help_str: str
    default: T
    param_type: type = Type[T]

    # def __init__(self, short_arg, long_arg, param_type, help_str, default) -> None:
    #     self.short_arg = short_arg
    #     self.long_arg = long_arg
    #     self.param_type = param_type
    #     self.help_str = help_str
    #     self.default = default

    # def __hash__(self):
    #     return hash((self.short_arg, self.long_arg, self.default, self.help_str))



class BenchmarkItem(ABC):
    """
    This is the base class for all boxes (tests).
    This provides an interface for the main runner to invoke each test.
    
    Each test should inherit from this class and implement the methods.

    """

    output_structure: BenchmarkOutputStructure
    metadata: BenchmarkMetadata
    params: FrozenSet[BenchmarkParameters]  # the parameters/input for this test

    def __init__(self, params: FrozenSet[BenchmarkParameters[T]],
                 metadata: BenchmarkMetadata) -> None:
        '''
        TODO: what happens here? nothing?
        '''
        self.params = params
        self.metadata = metadata

        ###raise NotImplementedError

    @abstractmethod
    def initialize(self) -> bool:
        '''
        This is called to setup the test environment by the master runner.
        Called once before the test is run.
        '''
        raise NotImplementedError
    
    # TODO: do I need this? runner should auto pickup relevant info from the bento box
    # @abstractmethod
    # def register_bento_box(self) -> None:
    #     '''
    #     Register the test box with the master.
    #     This includes the metadata such as name, desc, as well as specifics like
    #     output csv structure, and more importantly, registering the arguments.
    #     '''

    #     raise NotImplementedError
    
    # def _add_args(self, parser: ap.ArgumentParser) -> bool:
    #     '''
    #     This function will be used to parse the arguments relevant to this bento box,
    #     which will come from the command line arg parser.

    #     Args:
    #         parser: The argument parser from the master, should have every param this benchmark item needs.
    #     '''
        
    #     raise NotImplementedError

    @abstractmethod
    def run(self) -> bool:
        '''
        Actually running the test.
        Should probably call _parse_results() at the end,
        where results would be generated and parsed and stored to somewhere.

        Returns: run status, True if successful, False otherwise.
        '''
        raise NotImplementedError

    def _parse_results(self) -> bool:
        '''
        Parse the results of the test. Should be called at the end of run().
        This will store the results in a structured format (probably csv), which can be used by plot().

        Returns: parse status, True if successful, False otherwise.
        '''
        # TODO: implement this
        raise NotImplementedError

    def plot(self) -> bool:
        '''
        Plot the results of this benchmark, probably making use of the output schema and reading the parsed results.
        '''
        # TODO: implement this
        raise NotImplementedError

    

