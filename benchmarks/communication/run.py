import os
import argparse
import subprocess
import paramiko
from getpass import getpass
import time

# TODO question: How should username and password be passed in? Also in configs_user json? 
# TODO question: SCP the code to host??
# TODO question: ssh connection cannot be stopped before process terminates, so I'll have to ssh into the host twice? Once to start the server and once to stop the server? 

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run communication benchmark tests.')
    
    # Dynamically add arguments based on the parameters passed from run_dpdbento.py (TCP/RDMA/DMA)
    parser.add_argument('--benchmark_items', type=str, required=True, help='Comma-separated list of benchmark items')
    
    # Add all possible parameters; any unused will remain default
    parser.add_argument('--data_size', type=int, default=8, help='Bytes to transfer')
    parser.add_argument('--queue_depth', type=int, default=1, help='Queue depth')
    parser.add_argument('--threads', type=int, default=1, help='Number of threads')
    parser.add_argument('--test_rounds', type=int, default=100, help='Total number of transfers')
    parser.add_argument('--host_pci', type=str, default="e1:00.1", help='PCI address of host')
    parser.add_argument('--dpu_pci', type=str, default="03:00.1", help='PCI address of DPU')
    parser.add_argument('--host_ip', type=str, default="10.10.1.2", help='IP address of host')
    parser.add_argument('--dpu_ip', type=str, default="10.10.1.42", help='IP address of dpu')
    parser.add_argument('--port', type=int, default=8080, help='Port number')
    
    return parser.parse_args()

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def ssh_into_host(hostname, username, command, log_file):
    password = getpass("Enter SSH password: ")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("Starting SSH into host...", file={log_file})
        ssh.connect(hostname, username=username, password=password)
        print(f"Connected to host...", file={log_file})
        
        command = f"""
        cd transfer/tcp;
        ./server.sh
        """
        
        stdin, stdout, stderr = ssh.exec_command(command)

        # Read the output from the command
        output = stdout.read().decode()
        errors = stderr.read().decode()

        # Capture the output and errors
        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')
        
        print("Command output:" + output, file={log_file})
        if errors:
            print("Command errors:" + errors, file={log_file})
            
    finally:
        time.sleep(10)
        ssh.close()

def run_benchmark(port, data_size, queue_depth, threads, test_rounds, host_pci, dpu_pci, host_ip, dpu_ip, output_folder, log_file, benchmark_item):
    print(f"Running {benchmark_item} test with block_size={data_size} bytes, queue depth={queue_depth}, threads={threads}, test_rounds={test_rounds}", file=log_file)
    
    test_run_dir = os.path.join(output_folder, benchmark_item, f"{data_size}_{queue_depth}_{threads}_{test_rounds}")
    create_directory(test_run_dir)    
    
    temp_output_file = os.path.join(test_run_dir, f"output.csv")
    
    if benchmark_item == "TCP":
        # TODO Where should the username and password be defined? 
        username = "temp"
        ssh_into_host(host_ip, username, log_file)
        
        print(f"SSH to host completed. Now starting the client on the DPU...", file=log_file)
        
        # initialize client
        client_directory = os.path.join(os.path.dirname(__file__), 'tcp/client')
        os.chdir(client_directory)

        try:
            subprocess.run(["gcc", "-o", "client", "client.c"], check=True)
            print(f"C program compiled successfully.", file={log_file})
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed: {e}", file={log_file})
            exit(1)

        # run the compiled client program with arguments
        try:
            subprocess.run(["./client", host_ip, port, data_size, threads, test_rounds, temp_output_file], check=True)
            print(f"Client program executed successfully.", file={log_file})
        except subprocess.CalledProcessError as e:
            print(f"Client execution failed: {e}", file={log_file})
            
        print(f"Results saved to {temp_output_file}", file=log_file)
   
def main():
    args = parse_arguments()
    
    communication_output_dir = os.path.join(os.path.dirname(__file__), 'output')
    create_directory(communication_output_dir)
    
    log_file_path = os.path.join(communication_output_dir, "benchmark_test_log.txt")
    
    with open(log_file_path, 'a') as log_file:
        benchmark_items = args.benchmark_items.split(',')

        for benchmark_item in benchmark_items:
            run_benchmark(args.port, args.data_size, args.queue_depth, args.threads, args.test_rounds, args.host_pci, args.dpu_pci, args.host_ip, args.dpu_ip, communication_output_dir, log_file, benchmark_item)
    
if __name__ == '__main__':
    main()
    print(f"Finished running communication benchmarks")
    