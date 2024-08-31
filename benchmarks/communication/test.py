import os
import subprocess

def ssh_into_host(hostip, username, port, file_size, threads, total_requests):
    # HOST_USER="$1"
    # HOST_IP="$2"
    # PORT="$3"
    # FILE_SIZE="$4"
    # THREADS="$5"
    # TOTAL_REQUESTS="$6"
    # LOCAL_DIRECTORY="$7"
    # OUTPUT_FILE="$8"
    # REMOTE_DIRECTORY="/tmp" 

    
    file_path = os.path.join(os.path.dirname(__file__), "tcp")
    print(file_path)
    
    shell_script = os.path.join(file_path, "client.sh")
    print(shell_script)
    
    output_file = "/tmp/comm/output.csv"
    
    command = ["bash", shell_script, username, hostip, port, file_size, threads, total_requests, file_path, output_file]
    result = subprocess.run(command, capture_output=True, text=True)

ssh_into_host("10.70.60.11", "annali", "8080", "8", "2", "1000")

    