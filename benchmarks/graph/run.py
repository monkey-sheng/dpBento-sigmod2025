import os
import argparse
import subprocess
#import json
import logging

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run memory benchmark.")
    parser.add_argument('--scale_factor', type=str, required=True, help="Scale Factor for dataset size")
    parser.add_argument('--num_threads', type=int, default=0, help='Number of threads to run kuzu with. 0 means max')

    return parser.parse_args()

def run_benchmark(env, num_threads):
    benchmark_dir = os.path.dirname(os.path.abspath(__file__))
    run_command(env + ["bash", benchmark_dir + "/kuz/init-and-load.sh"])
    if num_threads == 0:
        run_command(env + ["bash", benchmark_dir + "/kuz/run.sh"])
    else:
        run_command(env + ["bash", benchmark_dir + "/kuz/run.sh", str(num_threads)])
def run_command(command, check=True, shell=False):
    """Run a shell command."""
    logging.info(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=check, shell=shell)

def main():
    args = parse_arguments()
    benchmark_dir = os.path.dirname(os.path.abspath(__file__))
    env = []
    if float(args.scale_factor) < 1:
        env.append("SF=1")
    else:
        env.append("SF=" + str(args.scale_factor))
    run_command(env + ["bash", benchmark_dir + "/scripts/download-projected-fk-data-sets.sh"])
    run_benchmark(env, args.num_threads)

        

        
if __name__ == '__main__':
    main()
