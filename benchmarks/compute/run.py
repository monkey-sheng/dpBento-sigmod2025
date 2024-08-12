import argparse
import os
import subprocess
import pandas as pd


TYPE_SIZE = [16, 32, 64, 128]
VALID_BENCHMARK_ITEMS = ['matrix', 'int', 'float']

ALL_METRICS_MATRIX = ['n_workers', 'matrix_size', 'total_ops', 'ops/s']
ALL_METRICS_INT = ['n_workers', 'data_size', 'total_ops', 'ops/s']
ALL_METRICS_FP = ALL_METRICS_INT

# Define the function to parse arguments, args include n_workers, data_size, running_time
def parse_arguments():
    parser = argparse.ArgumentParser(description='compute benchmark')
    parser.add_argument('--benchmark_items', type=str, default='matrix', help='Benchmark items to run')

    parser.add_argument('--n_workers', type=int, default=1, help='Number of workers')
    parser.add_argument('--data_size', type=int, default=32, help='Size of the data type, i.e. 32 for int32')
    parser.add_argument('--matrix_size', type=int, default=128, help='Size N of the matrix, i.e. NxN')
    parser.add_argument('--running_time', type=int, default=5, help='Run N seconds for each')
    
    args, _ = parser.parse_known_args()
    print(args)
    return args

def collect_results_matrix(out: str, args):
    '''
    This is done after each run(), collect results into a csv which will be aggregated by report.py;
    Need to append after the first write, i.e. will be adding more rows with each diff config run
    '''
    results_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'matrix')
    os.makedirs(results_dir, exist_ok=True)

    # last line of the output is metrics, then split the values
    result_values = out.splitlines()[-1].split()
    bogo_ops = int(result_values[4])
    ops_per_sec = round(float(result_values[8]))
    # write the results to a file
    result_file = os.path.join(results_dir, "result.csv")
    
    # if the file doesn't exist (first run)
    if not os.path.exists(os.path.join(results_dir, "result.csv")):
        # write the columns header, also include the benchmark item name
        fp = open(result_file, 'w')
        # fp.write(','.join(ALL_METRICS_MATRIX) + ',benchmark_item' + '\n')
        fp.write(','.join(ALL_METRICS_MATRIX) + '\n')
    else:
        fp = open(result_file, 'a')

    fp.write(','.join(map(str, [args.n_workers, args.matrix_size, bogo_ops, ops_per_sec])) + '\n')
    fp.close()

def collect_results_int(out: str, args):
    '''
    This is done after each run(), collect results into a csv which will be aggregated by report.py;
    Need to append after the first write, i.e. will be adding more rows with each diff config run
    '''
    results_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'int')
    os.makedirs(results_dir, exist_ok=True)

    # last line of the output is metrics, then split the values
    result_values = out.splitlines()[-1].split()
    bogo_ops = int(result_values[4])
    ops_per_sec = round(float(result_values[8]))
    # write the results to a file
    result_file = os.path.join(results_dir, "result.csv")
    
    # if the file doesn't exist (first run)
    if not os.path.exists(os.path.join(results_dir, "result.csv")):
        # write the columns header, also include the benchmark item name
        fp = open(result_file, 'w')
        # fp.write(','.join(ALL_METRICS_INT) + ',benchmark_item' + '\n')
        fp.write(','.join(ALL_METRICS_INT) + '\n')
    else:
        fp = open(result_file, 'a')

    fp.write(','.join(map(str, [args.n_workers, args.data_size, bogo_ops, ops_per_sec])) + '\n')
    fp.close()

def collect_results_float(out: str, args):
    '''
    This is done after each run(), collect results into a csv which will be aggregated by report.py;
    Need to append after the first write, i.e. will be adding more rows with each diff config run
    '''
    results_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'float')
    os.makedirs(results_dir, exist_ok=True)

    # last line of the output is metrics, then split the values
    result_values = out.splitlines()[-1].split()
    bogo_ops = int(result_values[4])
    ops_per_sec = round(float(result_values[8]))
    # write the results to a file
    result_file = os.path.join(results_dir, "result.csv")
    
    # if the file doesn't exist (first run)
    if not os.path.exists(os.path.join(results_dir, "result.csv")):
        # write the columns header, also include the benchmark item name
        fp = open(result_file, 'w')
        # fp.write(','.join(ALL_METRICS_FP) + ',benchmark_item' + '\n')
        fp.write(','.join(ALL_METRICS_FP) + '\n')
    else:
        fp = open(result_file, 'a')

    fp.write(','.join(map(str, [args.n_workers, args.data_size, bogo_ops, ops_per_sec])) + '\n')
    fp.close()


def run():
    args = parse_arguments()
    print(f"Running compute benchmark with {args.n_workers} workers, data size: {args.data_size}, running time: {args.running_time} seconds")
    # Run the benchmark
    for item in args.benchmark_items.split(','):
        print(f"Running {item} benchmark")
        stdout: str
        # pattern match against the item
        if item == 'matrix':
            stdout = subprocess.run(
                f"stress-ng --metrics --matrix {args.n_workers} --matrix-size {args.data_size} -t {args.running_time}s",
                check=True, capture_output=True, shell=True, text=True).stderr
            collect_results_matrix(stdout, args)
        elif item == 'int':
            if args.data_size in TYPE_SIZE:
                method = f"int{args.data_size}"
            else:
                print(f"Invalid data size {args.data_size} for int benchmark, requires one of {TYPE_SIZE}")
                exit(-1)
            stdout = subprocess.run(
                f"stress-ng --metrics --cpu {args.n_workers} --cpu-method {method} -t {args.running_time}s",
                check=True, capture_output=True, shell=True, text=True).stderr
            collect_results_int(stdout, args)
        elif item == 'float':
            if args.data_size in TYPE_SIZE:
                method = f"float{args.data_size}"
            else:
                print(f"Invalid data size {args.data_size} for float benchmark, requires one of {TYPE_SIZE}")
                exit(-1)
            stdout = subprocess.run(
                f"stress-ng --metrics --cpu {args.n_workers} --cpu-method {method} -t {args.running_time}s",
                check=True, capture_output=True, shell=True, text=True).stderr
            collect_results_float(stdout, args)
        else:
            print(f"Invalid benchmark item {item}, requires one of {VALID_BENCHMARK_ITEMS}")
            exit(-1)
        
        print(f"Finished running {item} benchmark")

if __name__ == '__main__':
    run()
    print(f"Finished running compute benchmarks")