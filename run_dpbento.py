import json
import os
import subprocess
from itertools import product

import inspect
import pkgutil

import experiments.storage_test.run_experiment

class ExperimentRunner:
    def __init__(self, config_file):
        self.config: dict = self.load_user_config(config_file)
        self.benchmark_name = self.config['benchmark_name']
        self.test_parameters = self.config['test_parameters']

        # XXX: do we even need this at all?
        self.dpbento_root = self.config.get('dpbento_root', None)  # optional

        # TODO: directory where user written benchmarks are to be loaded from, revisit this later
        self.user_benchmarks_dir = self.config.get('user_benchmarks_dir', None)  # optional

        self.output_folder = self.config['output_folder']
        self.experiment_script = os.path.join(self.dpbento_root, 'experiments', self.benchmark_name, 'run_experiment.sh')

    def load_user_config(self, config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config

    # NOTE: we should maybe treat dpbento as a python package, that can be released and pip installed
    def get_all_benchmarks(self):
        '''
        Get all the benchmarks available built in, and also in the user_benchmarks_dir
        '''


    
    # if we want/need to load the descriptions or help msgs etc., then we need this
    # otherwise, maybe remove this
    def load_benchmark_config(self, benchmark_name):
        '''Load the benchmark config file for the given benchmark name'''
        # TODO: load the implementor's benchmark config file

    def create_directories(self):
        # XXX: why do we need this, if there's no such directory and we create one, experiment scripts won't exist at all?
        try:
            os.makedirs(self.dpbento_root, exist_ok=True)
        except PermissionError as e:
            print(f"PermissionError: Cannot create directory '{self.dpbento_root}'. Check your permissions.")
            raise e

        # XXX: output folder should probably be part of per box setup, unless we want to collect all results in one place?
        try:
            os.makedirs(self.output_folder, exist_ok=True)
        except PermissionError as e:
            print(f"PermissionError: Cannot create directory '{self.output_folder}'. Check your permissions.")
            raise e

    def run(self):
        self.create_directories()
        
        # Generate all combinations of test parameters
        keys = self.test_parameters.keys()

        # let's allow the flexibility of either using a scalar or a list for each parameter
        # if it's a scalar, we convert it to a list, else we keep it as is, v may well be list of lists
        values = (v if type(v := self.test_parameters[key]) is list else [v] for key in keys)
        combinations = list(product(*values))
        
        # XXX: this is at the top level, we should iterate through all benchmarks first
        # Run the experiments for all combinations
        for combination in combinations:
            test_params = list(zip(keys, combination))
            command = [
                "bash", self.experiment_script,
                "--benchmark_name", self.benchmark_name,
                "--output_folder", self.output_folder
            ]
            for key, value in test_params:
                command.append(f"--{key}")
                command.append(str(value))
            
            print(f"Running command: {' '.join(command)}")
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Command failed with error: {e}")

def main():
    # TODO: probably do some argument parsing here
    config_file = 'configs_user/customize_test.json'
    runner = ExperimentRunner(config_file)
    runner.run()

if __name__ == '__main__':
    main()
