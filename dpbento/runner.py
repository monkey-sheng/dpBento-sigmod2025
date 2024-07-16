'''
This is the master runner that powers the dpbento framework.
Handles the front end interfacing with end users, the loading and running of benchmarks,
and whatever else that follows.
'''

import argparse as ap
import inspect
import pkgutil
from typing import List

from benchmark_base import BenchmarkItem

class DPBentoRunner:

    arg_parser: ap.ArgumentParser  # for the raw command line arguments

    # TODO: use `nargs` for lists, `choices` for auto validating values
    # TODO: use metavar for useful example of inputs in help msg?
    # TODO: check out parents= for constructing a hierarchy of parsers
    # TODO: add_subparsers for subcommands?

    def __init__(self):
        self.arg_parser = ap.ArgumentParser(
            prog='dpbento', description='DP-Bento: the benchmarking framework for SmartNICs', add_help=True
        )
        self.arg_parser.add_argument_group('General Options', )
        pass

    def load_benchmarks(self):
        '''
        Load all the pre baked benchmarks from dpbento.
        '''
        pass

    def load_extra_benchmarks(self, extras_dir: str):
        '''
        Load extra benchmarks from the user specified directory.
        Not necessarily called for a run.
        '''
        pass

    def construct_arg_parser(self):
        '''
        Construct the argument parser from the benchmark items' module.
        TODO: should use module name as prefix, and check for conflicts.
        '''
        pass
    
    def handle_cmdline_args(self):
        '''
        Parse the command line arguments, perform relevant validation then assign to benchmark items' parameter set.
        '''
        pass

    def run(self):
        pass