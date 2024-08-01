import json
import os
import subprocess
from itertools import product
import argparse
import logging


# we need these scripts to be executable within a benchmark item directory
BENCH_ITEM_SCRIPTS = ['prepare.py', 'run.py', 'report.py', 'clean.py']

class ExperimentRunner:
    def __init__(self, config_file):
        # Set up logging
        self.logger = self.setup_logging()

        self.config = self.load_config(config_file)
        # TODO: do we need this any more?
        # self.benchmark_name = self.config['benchmark_name']
        # self.test_parameters = self.config['test_parameters']
        # self.metrics = self.config['metrics']

        # make dpbento_root optional, use the current dir of this file.
        # self.dpbento_root = self.config['dpbento_root']
        self.dpbento_root = self.config.get('dpbento_root', os.path.dirname(__file__))
        self.benchmarks_dir = os.path.join(self.dpbento_root, 'benchmarks')

        # optional user provided benchmarks dir to load them from
        self.user_benchmarks_dir = self.config.get('user_benchmarks_dir', None)

        # make this optional too
        # self.output_folder = self.config['output_folder']
        self.output_dir = self.config.get('output_dir', os.path.join(self.dpbento_root, 'output'))

        self.bench_params: dict[str, dict] = {}
        '''dict of benchmark item paths to their corresponding params from the user config'''
        
        # get a list of path strs to the benchmarks to run, subsequently find scripts from these paths
        self.benchmarks_to_run = []
        self.collect_all_benchmarks_to_run()
        '''a list of paths to the benchmark items to run, including the user provided benchmarks'''

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

    def create_and_check_directories(self):
        try:
            os.makedirs(self.dpbento_root, exist_ok=True)
            if not os.access(self.dpbento_root, os.R_OK | os.W_OK | os.X_OK):
                raise PermissionError(f"Cannot access dpbento directory '{self.dpbento_root}'. Check your permissions.")
        except PermissionError as e:
            print(f"PermissionError: Cannot create directory '{self.dpbento_root}'. Check your permissions.")
            raise e

        try:
            os.makedirs(self.output_dir, exist_ok=True)
            if not os.access(self.output_dir, os.R_OK | os.W_OK | os.X_OK):
                raise PermissionError(f"Cannot access output directory '{self.output_dir}'. Check your permissions.")
        except PermissionError as e:
            print(f"PermissionError: Cannot create directory '{self.output_dir}'. Check your permissions.")
            raise e
        # also check permission for benchmark dir
        if not os.access(self.benchmarks_dir, os.R_OK | os.W_OK | os.X_OK):
            raise PermissionError(f"Cannot access benchmarks directory '{self.benchmarks_dir}'. Check your permissions.")
        # TODO: do the same for user provided benchmark dir

    def collect_all_benchmarks_to_run(self):
        '''
        Examine the user json config file and collect all benchmarks to run, including the user provided benchmarks.
        
        Will add the benchmark items (paths) to `self.benchmarks_to_run`,
        and the corresponding params to `self.bench_params`.
        
        Returns: None
        '''
        def add_bench_item_if_ok(item_path, bench_params: dict):
            '''
            Add the benchmark item (path) to the list of benchmarks to run,
            and add the params from user config to the dict `bench_params` where the key is the item path,
            if all the scripts look okay (are executable, for now).
            '''
            if all(map(lambda script: os.access(os.path.join(item_path, script), os.X_OK), BENCH_ITEM_SCRIPTS)):
                self.logger.info(f"registered benchmark '{item_path}'")
                self.benchmarks_to_run.append(item_path)
                self.bench_params[item_path] = bench_params
                self.logger.debug(f"bench_params: {bench_params}")

            else:
                self.logger.warn(f"missing executable benchmark script(s) for benchmark '{item_path}', ignoring it...")

        to_run = []
        benchmark: dict
        for benchmark in self.config['benchmarks']:
            bench_items = benchmark.get("benchmark_items", [])
            bench_class = benchmark["benchmark_class"]

            bench_class_path = os.path.join(self.benchmarks_dir, bench_class)
            if not os.access(bench_class_path, os.X_OK):
                self.logger.warn(f"Cannot access benchmark class '{bench_class}', ignoring...")
                continue
            
            bench_class_user_path = item_path if \
                self.user_benchmarks_dir and os.access(item_path:=os.path.join(self.user_benchmarks_dir, bench_class), os.F_OK)\
                else None
            self.logger.debug(f"bench_class_user_path: {bench_class_user_path}")
            
            # if no items provided, run all benchmark items in the benchmark class, user params will be empty for all
            if not bench_items:
                # get all bench items dirs in the bench class
                bench_items_paths = [item_path for item_dir in os.listdir(bench_class_path)
                                    if os.path.isdir(item_path:=os.path.join(bench_class_path, item_dir))]
                for bench_items_path in bench_items_paths:
                    # get the benchmark scripts and check if executable
                    add_bench_item_if_ok(bench_items_path, {})
                
                # if there are user benchmarks, add them too
                if bench_class_user_path:
                    bench_items_user_paths = [item_path for item_dir in os.listdir(bench_class_user_path)
                                            if os.path.isdir(item_path:=os.path.join(bench_class_user_path, item_dir))]
                    for bench_items_user_path in bench_items_user_paths:
                        # get the benchmark scripts and check if executable
                        add_bench_item_if_ok(bench_items_user_path, {})
                    self.logger.info(f"Adding all user benchmark items {bench_items_user_paths} in class '{bench_class}'")
            
            # run the specified benchmarks
            else:
                for item in bench_items:
                    bench_params = item['parameters']

                    bench_name = item['name']
                    bench_item_path_builtin = os.path.join(self.benchmarks_dir, bench_class, bench_name)
                    bench_item_path_user = None
                    if self.user_benchmarks_dir:
                        bench_item_path_user = os.path.join(self.user_benchmarks_dir, bench_class, bench_name)
                    access_ok_builtin = os.access(bench_item_path_builtin, os.X_OK)
                    access_ok_user = False
                    if bench_item_path_user:
                        access_ok_user = os.access(bench_item_path_user, os.X_OK)

                    if access_ok_builtin:
                        add_bench_item_if_ok(bench_item_path_builtin, bench_params)
                    if access_ok_user:
                        # if we were to add a user bench that shadows the builtin bench,
                        # it would be ambiguous which one to run when reading the user config
                        # TODO: is there a good way to handle this?
                        if (access_ok_builtin):
                            self.logger.warn(f"user benchmarks found for '{bench_class}/{bench_name}',
                                             but shadows builtin benchmark with same class and name,
                                             not adding the user benchmark...")
                        else:
                            add_bench_item_if_ok(bench_item_path_user, bench_params)
                    else:
                        self.logger.warn(f"Cannot access benchmark '{bench_class}/{bench_name}', ignoring...")
        
        self.logger.info(f"Collected benchmarks to run: {self.benchmarks_to_run}")

    
    def run_dpbento(self):
        '''
        This is the main function of the dpbento framework.
        '''

        def run_benchmark_script(script_name: str, benchmark: str, opts: list[str] = []):
            script_path = os.path.join(benchmark, script_name)
            commands = ['python3', script_path] + opts
            try:
                subprocess.run(['python3', script_path], check=True)
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Running {script_name.split('.')[0]} for {benchmark} failed with error: {e}")
                return False
            return True

        self.create_and_check_directories()

        # go through all benchmark items in benchmarks_to_run
        for benchmark in self.benchmarks_to_run:
            # run the prepare script
            if not run_benchmark_script('prepare.py', benchmark):
                continue
            

            # run the benchmark

            bench_params = self.bench_params[benchmark]
            # Generate all combinations of test parameters
            keys = self.bench_params.keys()

            # allow users to just use a scalar value; if it's not a list, we make it a list
            values = (v if isinstance(v := bench_params[key], list) else [v]
                    for key in keys)
            combinations = list(product(*values))
        
            # Run the experiments for all combinations
            for combination in combinations:
                params = list(zip(keys, combination))
                # XXX: whatever you (the user) need, put it in the json config
                # command = [
                #     "python", self.benchmark_scripts,
                #     "--benchmark_name", self.benchmark_name,
                #     "--output_folder", self.output_dir,
                #     "--metrics", json.dumps(self.metrics)  # Pass metrics as JSON string
                # ]
                
                # command = ["python3", os.path.join(benchmark, 'run.py')]
                # let's only put the options (and values) in there
                opts = self.kv_list_to_opts(params)
                
                self.logger.info(f"Running benchmark {benchmark} with: {' '.join(opts)}")
                if not run_benchmark_script('run.py', benchmark, opts=opts):
                    # probably don't want to report if the benchmark failed
                    continue

            # run the report script
            # TODO: report.py should generate the intermediate data,
            # which should include the structured output (csv etc.) and maybe some extra info,
            # the goal is to generate the final report and visualization from the intermediate data
            opts = []
            # TODO: what do we need here, metrics?
            metrics = # TODO: need a equivalent for bench_params, for metrics
            if not run_benchmark_script('report.py', benchmark, opts=opts):
                continue

    @staticmethod
    def kv_list_to_opts(kv_list):
        opts = []
        for key, value in kv_list:
            opts.append(f"--{key}")
            opts.append(str(value))
        return opts


def main():
    parser = argparse.ArgumentParser(description='Welcome to DPU Benchmark tests.')
    parser.add_argument('--config', type=str, required=True, help='Path to the configuration file')
    parser.add_argument('--clean', action='store_true', help='Run the clean script')
    args = parser.parse_args()

    runner = ExperimentRunner(args.config)

    # TODO: cleaning should be done for all (or maybe only the specified ones?)
    if args.clean:
        clean_script_path = runner.clean_script
        print(f"Running clean script: {clean_script_path}")
        try:
            subprocess.run(['bash', clean_script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Clean command failed with error: {e}")
    else:
        runner.run_dpbento()

if __name__ == '__main__':
    main()
