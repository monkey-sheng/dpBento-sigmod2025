import os
import argparse
import subprocess
import shutil
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run memory benchmark.")
    parser.add_argument('--test type', type=str, required=True, help='"latency" XOR "bandwidth"')

    parser.add_argument('--numThreads', type=int, default=0, help="Number of threads for bandwidth benchmark (0 for max)(ignored by latency test)")
    parser.add_argument('--starting_size', type=str, required=True, help='starting size for working set')
    parser.add_argument("--ending_size", type=str, required=True, help="ending size for working set")
    parser.add_argument("--length_multipler", type=int, default=8, help="increase test run duration, must be power of 2")

    return parser.parse_args()

def run_benchmark(test_name, numThreads, starting_size, ending_size, length_multipler):
    test = []
    out = ""
    if test_name == "bandwidth":
        test = ["band.out", str(numThreads)]
        out = "band.csv"
    else:
        test = ["lat.out"]
        out = "lat.csv"
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
    command = test + [str(starting_size), str(ending_size), length_multipler, out]
    subprocess.run(command, check=True)

def main():
    args = parse_arguments()
    run_benchmark(args.test_name, args.numThreads, args.starting_size, args.ending_size, args.length_multipler)
if __name__ == '__main__':
    main()
