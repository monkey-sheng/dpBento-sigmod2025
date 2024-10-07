import os
import argparse
import subprocess
import shutil

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run storage benchmark tests.')
    
    # Dynamically add arguments based on the parameters passed from run_dpdbento.py
    parser.add_argument('--benchmark_items', type=str, required=True, help='Comma-separated list of benchmark items')
    
    # Add all possible parameters; any unused will remain default
    parser.add_argument('--numProc', type=int, default=4, help='Number of jobs')
    parser.add_argument('--block_sizes', type=str, default="1m", help='Block sizes')
    parser.add_argument('--size', type=str, default="1G", help='Size of the test file')
    parser.add_argument('--runtime', type=str, default="30s", help='Runtime of the test')
    parser.add_argument('--direct', type=int, default=1, help='Direct I/O flag')
    parser.add_argument('--iodepth', type=int, default=32, help='I/O depth')
    parser.add_argument('--io_engine', type=str, default="io_uring", help='I/O engine to use')
    parser.add_argument('--test_lst', type=str, default="randwrite,randread,write,read", help='Comma-separated list of tests')
    parser.add_argument('--runtimes', type=int, default=5, help='Number of runtimes')
    parser.add_argument('--metrics', type=str, help='Metrics to collect (not used in run.py)')
    
    return parser.parse_args()

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def clean_directory(directory):
    """Clean up the directory by removing its contents."""
    if os.path.exists(directory):
        shutil.rmtree(directory)
    create_directory(directory)

def run_benchmark(test_name, block_size, numjobs, size, runtime, direct, iodepth, ioengine, test_dir, output_folder, log_file, runtimes, benchmark_item):
    print(f"Running {benchmark_item} test: {test_name} with block_size={block_size}, numjobs={numjobs}, size={size}, runtime={runtime}, direct={direct}, iodepth={iodepth}, ioengine={ioengine}", file=log_file)
    
    test_run_dir = os.path.join(output_folder, test_name, f"{block_size}_{numjobs}_{size}_{runtime}_{direct}_{iodepth}_{ioengine}")
    create_directory(test_run_dir)
    
    # Ensure test_dir exists and clean it before running the benchmark
    clean_directory(test_dir)
    
    combined_output_file = os.path.join(test_run_dir, "combined_results.txt")

    with open(combined_output_file, 'a') as combined_file:
        for i in range(1, runtimes + 1):
            print(f"Run #{i}", file=log_file)
            print(f"\nRun #{i}\n{'-'*10}\n", file=combined_file)
            
            command = [
                benchmark_item,
                f"--name={test_name}", 
                f"--ioengine={ioengine}", 
                f"--rw={test_name}", 
                f"--bs={block_size}", 
                f"--direct={direct}", 
                f"--size={size}", 
                f"--numjobs={numjobs}", 
                f"--iodepth={iodepth}", 
                f"--runtime={runtime}", 
                "--group_reporting", 
                f"--directory={test_dir}"
            ]
            
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                combined_file.write(result.stdout)
                print(f"Results appended to {combined_output_file}", file=log_file)
            except subprocess.CalledProcessError as e:
                print(f"Error during run {i}: {e}", file=log_file)
                print(f"stderr: {e.stderr}", file=log_file)
                print(f"stdout: {e.stdout}", file=log_file)
            
            # Clean the test directory after each run
            clean_directory(test_dir)

def main():
    args = parse_arguments()
    
    # Create output directory inside storage
    storage_output_dir = os.path.join(os.path.dirname(__file__), 'output')
    create_directory(storage_output_dir)
    
    log_file_path = os.path.join(storage_output_dir, "benchmark_test_log.txt")

    # Create or clean /tmp/fio_test directory before running the tests
    test_directory = "/tmp/fio_test"
    clean_directory(test_directory)

    with open(log_file_path, 'a') as log_file:
        benchmark_items = args.benchmark_items.split(',')
        test_lst = args.test_lst.split(',')

        for benchmark_item in benchmark_items:
            for test in test_lst:
                run_benchmark(test, args.block_sizes, args.numProc, args.size, args.runtime, args.direct, args.iodepth, args.io_engine, test_directory, storage_output_dir, log_file, args.runtimes, benchmark_item)

if __name__ == '__main__':
    main()
