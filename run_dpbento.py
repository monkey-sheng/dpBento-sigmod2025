import json
import os
import subprocess
from itertools import product
import argparse
import logging

# These scripts need to be executable in the benchmark item directory
BENCH_ITEM_SCRIPTS = ['prepare.py', 'run.py', 'report.py', 'clean.py']

class ExperimentRunner:
    def __init__(self, config_file):
        # Set up logging
        self.logger = self.setup_logging()

        self.config = self.load_config(config_file)

        # Get the directory of the current script as the dpbento root directory
        self.dpbento_root = os.path.dirname(os.path.abspath(__file__))
        self.benchmarks_dir = os.path.join(self.dpbento_root, 'benchmarks')

        # Set the output directory
        self.output_dir = os.path.join(self.dpbento_root, 'output')

        self.bench_params = {}
        '''Dictionary mapping benchmark item paths to parameters from the user config'''

        self.bench_metrics = {}
        '''Dictionary mapping benchmark item paths to metrics from the user config'''

        # Get the list of benchmark paths to run, and then find scripts in these paths
        self.benchmarks_to_run = []
        self.collect_all_benchmarks_to_run()
        '''List of benchmark item paths to run, including user-provided benchmarks'''

        self.logger.debug('Using output directory: %s, dpbento root directory: %s', self.output_dir, self.dpbento_root)

    @staticmethod
    def setup_logging():
        logger = logging.getLogger('dpbento')
        logger.setLevel(logging.DEBUG)

        # Create a console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(ch)
        return logger
    
    def load_config(self, config_file) -> dict:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config

    def create_and_check_directories(self):
        try:
            os.makedirs(self.dpbento_root, exist_ok=True)
            if not os.access(self.dpbento_root, os.R_OK | os.W_OK | os.X_OK):
                raise PermissionError(f"Cannot access dpbento directory '{self.dpbento_root}'. Please check your permissions.")
        except PermissionError as e:
            print(f"PermissionError: Unable to create directory '{self.dpbento_root}'. Please check your permissions.")
            raise e

        try:
            os.makedirs(self.output_dir, exist_ok=True)
            if not os.access(self.output_dir, os.R_OK | os.W_OK | os.X_OK):
                raise PermissionError(f"Cannot access output directory '{self.output_dir}'. Please check your permissions.")
        except PermissionError as e:
            print(f"PermissionError: Unable to create directory '{self.output_dir}'. Please check your permissions.")
            raise e

        # Also check permissions for the benchmark directory
        if not os.access(self.benchmarks_dir, os.R_OK | os.W_OK | os.X_OK):
            raise PermissionError(f"Cannot access benchmark directory '{self.benchmarks_dir}'. Please check your permissions.")
        self.logger.info(f"Benchmark directory and permissions verified.")

    def collect_all_benchmarks_to_run(self):
        '''
        Check the user JSON config file and collect all benchmarks to run, including user-provided benchmarks.
        
        Add benchmark items (paths) to `self.benchmarks_to_run`,
        and add parameters from the user config to the `self.bench_params` dictionary.
        
        Returns: None
        '''
        def add_bench_item_if_ok(item_path, bench_params: dict, metrics: list[str]):
            '''
            Add benchmark items (paths) to the list of benchmarks to run,
            and add parameters from the user config to the `bench_params` dictionary where the key is the item path,
            if all scripts look okay (currently executable).
            '''
            if all(map(lambda script: os.access(os.path.join(item_path, script), os.X_OK), BENCH_ITEM_SCRIPTS)):
                self.logger.info(f"Registering benchmark '{item_path}'")
                self.benchmarks_to_run.append(item_path)
                self.bench_params[item_path] = bench_params
                self.bench_metrics[item_path] = metrics
                self.logger.debug(f"bench_params: {bench_params}")
            else:
                self.logger.warning(f"Benchmark '{item_path}' missing executable scripts, ignoring...")

        benchmark: dict

        for benchmark in self.config['benchmarks']:
            bench_class = benchmark["benchmark_class"]
            bench_params = benchmark["parameters"]
            metrics = benchmark.get("metrics", [])
            bench_class_path = os.path.join(self.benchmarks_dir, bench_class)
            if not os.access(bench_class_path, os.X_OK):
                self.logger.warning(f"Cannot access benchmark class '{bench_class}', ignoring...")
                continue

            add_bench_item_if_ok(bench_class_path, bench_params, metrics)

        self.logger.info(f"Collected benchmarks to run: {self.benchmarks_to_run}")

    def run_dpbento(self):
        '''
        This is the main function for the dpbento framework.
        '''

        def run_benchmark_script(script_name: str, benchmark: str, opts: list[str] = []):
            script_path = os.path.join(benchmark, script_name)
            commands = ['python3', script_path] + opts
            try:
                subprocess.run(commands, check=True)
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Running {script_name.split('.')[0]} for {benchmark} failed, error: {e}")
                return False
            return True

        self.create_and_check_directories()

        for benchmark in self.benchmarks_to_run:
            if not run_benchmark_script('prepare.py', benchmark):
                continue

            bench_params = self.bench_params[benchmark]
            keys = bench_params.keys()
            values = (v if isinstance(v, list) else [v] for v in bench_params.values())
            combinations = list(product(*values))

            for combination in combinations:
                params = list(zip(keys, combination))
                opts = self.kv_list_to_opts(params)
                
                self.logger.info(f"Running benchmark {benchmark} with: {' '.join(opts)}")
                if not run_benchmark_script('run.py', benchmark, opts=opts):
                    continue

            # Add metrics parameters and run report.py
            metrics_opts = [f"--metrics={json.dumps(self.bench_metrics[benchmark])}"]
            if not run_benchmark_script('report.py', benchmark, opts=metrics_opts):
                continue

    @staticmethod
    def kv_list_to_opts(kv_list):
        opts = []
        for key, value in kv_list:
            opts.append(f"--{key}")
            opts.append(str(value))
        return opts

    def clean_benchmarks(self):
        '''
        Run the clean.sh script to remove intermediate files for each benchmark class and reset state.
        '''
        for benchmark in self.benchmarks_to_run:
            clean_script_path = os.path.join(benchmark, 'clean.sh')
            if os.path.exists(clean_script_path) and os.access(clean_script_path, os.X_OK):
                self.logger.info(f"Running clean script: {clean_script_path}")
                try:
                    subprocess.run(['bash', clean_script_path], check=True)
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Running clean.sh for {benchmark} failed, error: {e}")
            else:
                self.logger.warning(f"Clean script not found or not executable: {benchmark}")

def main():
    parser = argparse.ArgumentParser(description='Welcome to DPU benchmarking.')
    parser.add_argument('--config', type=str, required=True, help='Path to the configuration file')
    parser.add_argument('--clean', action='store_true', help='Run clean scripts')
    args = parser.parse_args()

    runner = ExperimentRunner(args.config)

    if args.clean:
        runner.clean_benchmarks()
    else:
        runner.run_dpbento()

if __name__ == '__main__':
    main()
