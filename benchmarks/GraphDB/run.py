import os
import argparse
import subprocess
#import json
import logging
import glob

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run graph benchmark.")
    parser.add_argument('--scale_factor', type=str, required=True, help="Scale Factor for dataset size")
    parser.add_argument('--num_threads', type=int, default=0, help='Number of threads to run kuzu with. 0 means max')
    parser.add_argument('--queries_to_execute', type=str, default="1,2,3,4,5,6,7,8,9", help="Which of the 9 queries to run (sorry, it has to be exactly in this format)")
    parser.add_argument('--execution_mode', type=str, default="cold", help="Run each query twice, only recording the 2nd input")
    parser.add_argument('--metrics', type=str, help="ignore")
    parser.add_argument('--benchmark_items', type=str, help="ignore")

    return parser.parse_args()

def run_benchmark(num_threads):
    benchmark_dir = os.path.dirname(os.path.abspath(__file__))
    run_command(["bash", benchmark_dir + "/kuz/init-and-load.sh"])
    if num_threads == 0:
        run_command(["bash", benchmark_dir + "/kuz/run.sh"])
    else:
        run_command(["bash", benchmark_dir + "/kuz/run.sh", str(num_threads)])
def run_command(command, check=True, shell=False):
    """Run a shell command."""
    logging.info(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=check, shell=shell)

def main():
    args = parse_arguments()
    benchmark_dir = os.path.dirname(os.path.abspath(__file__))
    max_sf = ''
    if float(args.scale_factor) < 1:
        max_sf = "1"
    else:
        max_sf = args.scale_factor
    with open(benchmark_dir + "/kuz/scratch/queries.txt", "w") as q:
        q.write(args.queries_to_execute)
    with open(benchmark_dir + "/kuz/scratch/exec_mode.txt", "w") as e:
        e.write(args.execution_mode)
    os.putenv("SF", args.scale_factor)
    os.putenv("MAX_SF", max_sf)
    
    if not os.path.exists(benchmark_dir + "/data/social-network-sf" + args.scale_factor + "-projected-fk") and not os.path.exists(benchmark_dir + "/data/social-network-sf" + args.scale_factor + "-projected-fk.tar.zst"): # NOTE: optimization may fail
        run_command(["bash", benchmark_dir + "/scripts/download-projected-fk-data-sets.sh"])

    run_benchmark(args.num_threads)

        

        
if __name__ == '__main__':
    main()
