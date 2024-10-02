import os
import sys

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

if base_dir not in sys.path:
    sys.path.append(base_dir)
    
from benchmarks.packages.kvs_parser import KVSParser
from benchmarks.packages.kvs_runner import KVSRunner

if __name__ == '__main__':
    # kvs_parser = KVSParser()
    # args = kvs_parser.parse_arguments()
    parser = KVSParser()
    # 模拟参数
    args = parser.parse_arguments()
    
    
    runner = KVSRunner(args)
    runner.run()

    kvs_runner = KVSRunner(args)
    kvs_runner.run_benchmark_test(args.operation_size,args.operation_type,args.data_distribution_type,args.metric)
