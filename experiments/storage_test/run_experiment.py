import os
import argparse
import subprocess
import shutil
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run FIO benchmark tests.')
    
    parser.add_argument('--metrics', type=str, required=True, help='JSON string of metrics to report')
    parser.add_argument('--output_folder', type=str, required=True, help='Output folder for results')
    parser.add_argument('--numProc', type=int, default=4, help='Number of jobs')
    parser.add_argument('--block_sizes', type=str, default="1m", help='Block sizes')
    parser.add_argument('--size', type=str, default="1G", help='Size of the test file')
    parser.add_argument('--runtime', type=str, default="30s", help='Runtime of the test')
    parser.add_argument('--direct', type=int, default=1, help='Direct I/O flag')
    parser.add_argument('--iodepth', type=int, default=32, help='I/O depth')
    parser.add_argument('--io_engine', type=str, default="io_uring", help='I/O engine to use')
    parser.add_argument('--test_lst', type=str, default="randwrite,randread,write,read", help='Comma-separated list of tests')
    parser.add_argument('--benchmark_name', type=str, required=True, help='Name of the benchmark')
    
    return parser.parse_args()

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def run_setup_script(benchmark_name):
    setup_script_path = os.path.join(os.path.dirname(__file__), 'setup.sh')
    subprocess.run(['bash', setup_script_path, benchmark_name], check=True)

def run_clean_script():
    clean_script_path = os.path.join(os.path.dirname(__file__), 'clean.sh')
    subprocess.run(['bash', clean_script_path], check=True)

def run_fio_test(test_name, block_size, numjobs, size, runtime, direct, iodepth, ioengine, test_dir, output_folder, log_file):
    run_count = 5
    print(f"Running FIO test: {test_name} with block_size={block_size}, numjobs={numjobs}, size={size}, runtime={runtime}, direct={direct}, iodepth={iodepth}, ioengine={ioengine}", file=log_file)
    
    test_run_dir = os.path.join(output_folder, test_name, f"{block_size}_{numjobs}_{size}_{runtime}_{direct}_{iodepth}_{ioengine}")
    create_directory(test_run_dir)
    
    # Ensure test_dir exists
    create_directory(test_dir)
    
    for i in range(1, run_count + 1):
        temp_output_file = os.path.join(test_run_dir, f"run{i}.txt")
        print(f"Run #{i}", file=log_file)
        command = [
            "fio", 
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
            f"--directory={test_dir}", 
            f"--output={temp_output_file}"
        ]
        subprocess.run(command, check=True)
        print(f"Results saved to {temp_output_file}", file=log_file)
        shutil.rmtree(test_dir)
        create_directory(test_dir)

def run_report_script(metrics, test_params, output_folder):
    report_script_path = os.path.join(os.path.dirname(__file__), 'report.py')
    metrics_str = json.dumps(metrics)
    command = ["python", report_script_path, "--metrics", metrics_str, "--output_folder", output_folder]
    env_vars = os.environ.copy()
    for key, value in test_params.items():
        env_vars[key] = str(value)
    
    subprocess.run(command, check=True, env=env_vars)

def main():
    args = parse_arguments()
    metrics = json.loads(args.metrics)
    
    log_file_path = os.path.join(args.output_folder, "fio_test_log.txt")

    # Run setup script
    run_setup_script(args.benchmark_name)
    
    with open(log_file_path, 'a') as log_file:
        create_directory(args.output_folder)
        
        
        
        test_lst = args.test_lst.split(',')
        test_params = vars(args)  # Convert args to a dictionary
        test_params.pop('metrics')  # Remove metrics from test_params

        for test in test_lst:
            run_fio_test(test, args.block_sizes, args.numProc, args.size, args.runtime, args.direct, args.iodepth, args.io_engine, "/tmp/fio_test", args.output_folder, log_file)
        
        # Run report script after all tests
        run_report_script(metrics, test_params, args.output_folder)
        
    
    # Run clean script after all tests
    # run_clean_script()

if __name__ == '__main__':
    main()
