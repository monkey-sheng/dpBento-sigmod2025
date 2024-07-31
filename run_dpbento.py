import json
import os
import subprocess
from itertools import product
import argparse
import logging

class ExperimentRunner:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.benchmark_name = self.config['benchmark_name']
        self.test_parameters = self.config['test_parameters']
        self.metrics = self.config['metrics']

        # make dpbento_root optional, use the current dir of this file.
        # self.dpbento_root = self.config['dpbento_root']
        self.dpbento_root = self.config.get('dpbento_root', os.path.dirname(__file__))

        # make this optional too
        # self.output_folder = self.config['output_folder']
        self.output_dir = self.config.get('output_dir', os.path.join(self.dpbento_root, 'output'))

        self.experiment_script = os.path.join(self.dpbento_root, 'experiments', self.benchmark_name, 'run_experiment.py')
        self.clean_script = os.path.join(self.dpbento_root, 'experiments', self.benchmark_name, 'clean.sh')

        # Set up logging
        self.logger = self.setup_logging()
        self.logger.debug('using output dir: %s, dpbento root: %s', self.output_dir, self.dpbento_root)

    @staticmethod
    def setup_logging():
        logger = logging.getLogger('dpbento')
        logger.setLevel(logging.DEBUG)

        # Create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(ch)
        return logger
    
    def load_config(self, config_file) -> dict:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config

    def create_directories(self):
        try:
            os.makedirs(self.dpbento_root, exist_ok=True)
        except PermissionError as e:
            print(f"PermissionError: Cannot create directory '{self.dpbento_root}'. Check your permissions.")
            raise e

        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except PermissionError as e:
            print(f"PermissionError: Cannot create directory '{self.output_dir}'. Check your permissions.")
            raise e

    def run_experiments(self):
        self.create_directories()
        
        # Generate all combinations of test parameters
        keys = self.test_parameters.keys()
        values = (self.test_parameters[key] for key in keys)
        combinations = list(product(*values))
        
        # Run the experiments for all combinations
        for combination in combinations:
            test_params = list(zip(keys, combination))
            command = [
                "python", self.experiment_script,
                "--benchmark_name", self.benchmark_name,
                "--output_folder", self.output_dir,
                "--metrics", json.dumps(self.metrics)  # Pass metrics as JSON string
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
    parser = argparse.ArgumentParser(description='Welcome to DPU Benchmark tests.')
    parser.add_argument('--config', type=str, required=True, help='Path to the configuration file')
    parser.add_argument('--clean', action='store_true', help='Run the clean script')
    args = parser.parse_args()

    runner = ExperimentRunner(args.config)

    if args.clean:
        clean_script_path = runner.clean_script
        print(f"Running clean script: {clean_script_path}")
        try:
            subprocess.run(['bash', clean_script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Clean command failed with error: {e}")
    else:
        runner.run_experiments()

if __name__ == '__main__':
    main()
