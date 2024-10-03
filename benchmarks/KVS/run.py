# import os
# import sys
# import json

# base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# if base_dir not in sys.path:
#     sys.path.append(base_dir)
    
# from benchmarks.packages.kvs_parser import KVSParser
# from benchmarks.packages.kvs_runner import KVSRunner

# if __name__ == '__main__':
#     parser = KVSParser()
#     args = parser.parse_arguments()
#     args.operation_type = json.loads(args.operation_type)
    

#     kvs_runner = KVSRunner(args)
#     kvs_runner.run_benchmark_test(args.operation_size,args.operation_type,args.data_distribution_type)
