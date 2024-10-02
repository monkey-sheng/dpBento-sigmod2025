import os
import sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if base_dir not in sys.path:
    sys.path.append(base_dir)

from benchmarks.packages.rdb_parser import E2EParser
from benchmarks.packages.rdb_runner import E2ERunner

if __name__ == '__main__':
    e2e_parser = E2EParser()
    args = e2e_parser.parse_arguments()
    
    e2e_runner = E2ERunner(args)
    e2e_runner.run_benchmark_test(args.scale_factors, args.query, args.execution_mode, e2e_runner.output_dir)
