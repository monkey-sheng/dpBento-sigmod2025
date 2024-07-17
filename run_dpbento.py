import json
import os
import subprocess
from itertools import product

class ExperimentRunner:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.benchmark_name = self.config['benchmark_name']
        self.test_parameters = self.config['test_parameters']
        self.dpdento_root = self.config['dpdento_root']
        self.output_folder = self.config['output_folder']
        self.experiment_script = os.path.join(self.dpdento_root, 'experiments', self.benchmark_name, 'run_experiment.sh')

    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config

    def run(self):
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Generate all combinations of test parameters
        keys = self.test_parameters.keys()
        values = (self.test_parameters[key] for key in keys)
        combinations = list(product(*values))
        
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
            subprocess.run(command, check=True)

def main():
    config_file = 'configs_user/customize_test.json'
    runner = ExperimentRunner(config_file)
    runner.run()

if __name__ == '__main__':
    main()
