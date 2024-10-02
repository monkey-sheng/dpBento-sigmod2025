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
    parser.parser.add_argument('--operation_size', type=int, choices=[100000, 300000, 1000000], required=True)
    parser.parser.add_argument('--operation_type', type=dict, required=True, help='Operation types with proportions.')
    parser.parser.add_argument('--data_distribution_type', type=str, choices=['zipfian', 'uniform', 'latest'], required=True)
    parser.parser.add_argument('--metrics', nargs='+', help='Metrics to collect.', default=['runtime', 'latency', 'throughput'])

    # 模拟参数
    args = parser.parse_arguments()
    args.operation_size = 1000000
    args.operation_type = {
        'readproportion': 0.4,
        'updateproportion': 0.4,
        'insertproportion': 0.1,
        'scanproportion': 0.1
    }
    args.data_distribution_type = 'latest'
    
    runner = KVSRunner(args)
    runner.run()

    kvs_runner = KVSRunner(args)
    kvs_runner.run_benchmark_test(args.operation_size,args.operation_type,args.data_distribution_type,args.metric)
