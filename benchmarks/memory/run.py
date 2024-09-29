import os
import argparse
import subprocess
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run memory benchmark.")
    parser.add_argument('--benchmark_items', type=str, required=True, help='"latency" XOR "bandwidth"')

    parser.add_argument('--num_threads_for_seq', type=int, default=0, help="Number of threads for bandwidth benchmark (0 for max)(ignored by latency test)")
    parser.add_argument('--starting_size', type=str, required=True, help='starting size for working set')
    parser.add_argument("--ending_size", type=str, required=True, help="ending size for working set")
    parser.add_argument("--test_duration_multiplier", type=int, default=8, help="increase test run duration, must be power of 2")

    return parser.parse_args()

def run_benchmark(test_name, numThreads, starting_size, ending_size, length_multipler):
    benchmark_dir = os.path.dirname(os.path.abspath(__file__))
    test = []
    out = ""
    if test_name == "bandwidth":
        test = [benchmark_dir + "/band.out", str(numThreads)]
        out = benchmark_dir + "/band.csv"
    else:
        test = [benchmark_dir + "/lat.out"]
        out = benchmark_dir + "/lat.csv"
    if starting_size[-1] == 'k':
        starting_size = int(starting_size[0:-1] * 1024)
    elif starting_size[-1] == 'm':
        starting_size = int(starting_size[0:-1] * 1024 * 1024)
    elif starting_size[-1] == 'g':
        starting_size = int(starting_size[0:-1] * 1024 * 1024 * 1024)
    if ending_size[-1] == 'k':
        ending_size= int(ending_size[0:-1] * 1024)
    elif ending_size[-1] == 'm':
        ending_size = int(ending_size[0:-1] * 1024 * 1024)
    elif ending_size[-1] == 'g':
        ending_size = int(ending_size[0:-1] * 1024 * 1024 * 1024)
    command = test + [str(starting_size), str(ending_size), str(length_multipler), out]
    subprocess.run(command, check=True)

def main():
    args = parse_arguments()
    if args.benchmark_items == "bandwidth":
        run_benchmark(args.benchmark_items, args.num_threads_for_seq, args.starting_size, args.ending_size, args.test_duration_multiplier)
    elif args.benchmark_items == "latency":
        run_benchmark(args.benchmark_items, args.num_threads_for_seq, args.starting_size, args.ending_size, args.test_duration_multiplier)
    else:
        run_benchmark("bandwidth", args.num_threads_for_seq, args.starting_size, args.ending_size, args.test_duration_multiplier)
        run_benchmark("latency", args.num_threads_for_seq, args.starting_size, args.ending_size, args.test_duration_multiplier)

        
if __name__ == '__main__':
    main()
