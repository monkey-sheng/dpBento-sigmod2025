import argparse
import os
import subprocess

# Default values
benchmark_name = ""
output_folder = ""
numjobs = 4
block_sizes = "1m"
size = "1G"
runtime = "30s"
direct = 1
iodepth = 32
io_engine = "io_ring"
test_lst = "randwrite,randread,write,read"
test_dir = "/tmp/fio_test"
log_file = "fio_test_log.txt"
run_count = 5

# TODO: not a good idea to parse cmdline arg at per box level
# Argument parsing
parser = argparse.ArgumentParser(description="FIO benchmark runner")
parser.add_argument("--benchmark_name", type=str, default=benchmark_name)
parser.add_argument("--output_folder", type=str, default=output_folder)
parser.add_argument("--numProc", type=int, default=numjobs)
parser.add_argument("--block_sizes", type=str, default=block_sizes)
parser.add_argument("--size", type=str, default=size)
parser.add_argument("--runtime", type=str, default=runtime)
parser.add_argument("--direct", type=int, default=direct)
parser.add_argument("--iodepth", type=int, default=iodepth)
parser.add_argument("--io_engine", type=str, default=io_engine)
parser.add_argument("--test_lst", type=str, default=test_lst)
args = parser.parse_args()

### minor: you don't need this block anyway
# Update variables with parsed arguments
benchmark_name = args.benchmark_name
output_folder = args.output_folder
numjobs = args.numProc
block_sizes = args.block_sizes
size = args.size
runtime = args.runtime
direct = args.direct
iodepth = args.iodepth
io_engine = args.io_engine
test_lst = args.test_lst
###

# Ensure test_dir exists
if not os.path.exists(test_dir):
    os.makedirs(test_dir)

# Convert comma-separated strings to lists
test_lst_array = test_lst.split(',')

# Function to run FIO test and cleanup
def run_fio_test(test_name, block_size, numjob, size, runtime, direct, iodepth, ioengine):
    with open(log_file, 'a') as log:
        log.write(f"Running FIO test: {test_name} with block_size={block_size}, numjobs={numjob}, size={size}, runtime={runtime}, direct={direct}, iodepth={iodepth}, ioengine={ioengine}\n")
        
        test_run_dir = os.path.join(output_folder, test_name, f"{block_size}_{numjob}_{size}_{runtime}_{direct}_{iodepth}_{ioengine}")
        os.makedirs(test_run_dir, exist_ok=True)
        
        for i in range(1, run_count + 1):
            temp_output_file = os.path.join(test_run_dir, f"run{i}.txt")
            log.write(f"Run #{i}\n")
            
            fio_command = [
                "fio", f"--name={test_name}", f"--ioengine={ioengine}", f"--rw={test_name}",
                f"--bs={block_size}", f"--direct={direct}", f"--size={size}", f"--numjobs={numjob}",
                f"--iodepth={iodepth}", f"--runtime={runtime}", "--group_reporting",
                f"--directory={test_dir}", f"--output={temp_output_file}"
            ]
            result = subprocess.run(fio_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            log.write(result.stdout.decode())
            log.write(f"Results saved to {temp_output_file}\n")
            
            # Clean up test files for each run
            for f in os.listdir(test_dir):
                os.remove(os.path.join(test_dir, f))
        
        log.write(f"Cleaning up test files for: {test_name} with block_size={block_size}, numjobs={numjob}, size={size}, runtime={runtime}, direct={direct}, iodepth={iodepth}, ioengine={ioengine}\n")

# don't run it as a script
# Run the actual benchmark
for test in test_lst_array:
    run_fio_test(test, block_sizes, numjobs, size, runtime, direct, iodepth, io_engine)

# for example, we can define a function with a signature like this
# which will then be imported and run by run_dpbento.py
def run_bento(*args, **kwargs):
    # maybe just call you `run_fio_test`, or do something more complex
    pass