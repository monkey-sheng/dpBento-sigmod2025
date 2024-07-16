'''
This is the main runner for the benchmark framework, more or less the entry point.
It will automatically handle the loading and some boilerplate setup process for the bento boxes and benchmarks.
'''

import argparse as ap
import inspect
import pkgutil
from typing import List

from benchmark_base import BenchmarkItem

# import all our prebuilt benchmarks modules here
# TODO: make everything under compute a dynamic import
# import compute.decompress
import compute
### from dpbento import compute ##circular import dpbento partially initialized

def final_plot():
    '''
    This plots the final results of all benchmarks across all perf aspects
    should be called after all benchmarks have been run.
    // TODO: think about what goes into the plots
    '''
    pass

if __name__ == '__main__':
    parser = ap.ArgumentParser(prog='dpbento', description='Run the dpbento benchmarking framework', add_help=True)

    parser.add_argument('--extras_dir', type=str, help='The directory to load extra user benchmarks from,\
                        which should contain dpbento(s), where each contain module(s), which are the benchmarks.',
                        required=False)    

    args = parser.parse_args()

    # TODO: maybe iter modules of compute, make decompress and others as dynamic imports
    decompress_submodules = [s for s in list(pkgutil.iter_modules(compute.__path__))]
    decompress_submodules = inspect.getmembers(compute, inspect.ismodule)
    for name, module in decompress_submodules:
        print(name, module)
    submodules = [module for _, module in decompress_submodules]
    print('submodules:', submodules)

    for module in submodules:
        benchmark_instances: List[BenchmarkItem] = [bench_item for _, bench_item in inspect.getmembers(
        module,
        lambda x: inspect.isclass(x) and issubclass(x, BenchmarkItem) and x is not BenchmarkItem)]#[j][1]
        print(benchmark_instances)

    print(inspect.getmembers(submodules[0], inspect.ismodule))
    

    # this should print all the classes that are subclasses of BenchmarkItem
    # benchmark_instance: BenchmarkItem = inspect.getmembers(
    #     decompress_submodules[1][1],#[i][1]
    #     lambda x: inspect.isclass(x) and issubclass(x, BenchmarkItem) and x is not BenchmarkItem)[0][1]#[j][1]
    ### print(benchmark_instance.__class__())


    # Load the user benchmarks
    # if args.dir:
    #     # TODO: load the user supplied benchmarks as modules
    #     pass