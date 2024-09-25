import argparse
import subprocess
import sys
import json
import os
from datetime import datetime

def generate_filename(args):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    params = [
        f"alg-{args.algorithm}",
        f"sec-{args.seconds}",
        f"bytes-{args.bytes}",
        f"multi-{args.multi}",
        f"async-{args.async_jobs}",
        f"misalign-{args.misalign}"
    ]
    return f"openssl_speed_{'_'.join(params)}_{timestamp}.txt"

def run_openssl_speed_test(args):
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename with parameters
    output_filename = generate_filename(args)
    output_file_path = os.path.join(output_dir, output_filename)

    # Build OpenSSL speed command
    command = [
        "openssl", "speed", "-elapsed",
        "-seconds", args.seconds,
        "-bytes", args.bytes,
        "-multi", str(args.multi)
    ]

    # Add optional parameters
    if args.async_jobs > 0:
        command.extend(["-async_jobs", str(args.async_jobs)])

    if args.misalign > 0:
        command.extend(["-misalign", str(args.misalign)])

    # Add algorithm
    command.append(args.algorithm)

    # Open output file
    with open(output_file_path, 'w') as output_file:
        # Write test parameters
        output_file.write("Running OpenSSL speed test with the following parameters:\n")
        output_file.write(f"Algorithm: {args.algorithm}\n")
        output_file.write(f"Test duration: {args.seconds} seconds\n")
        output_file.write(f"Data block size: {args.bytes} bytes\n")
        output_file.write(f"Parallel operations: {args.multi}\n")
        output_file.write(f"Async jobs: {args.async_jobs}\n")
        output_file.write(f"Misalignment: {args.misalign} bytes\n")
        output_file.write(f"Benchmark items: {args.benchmark_items}\n")
        output_file.write(f"Metrics: {args.metrics}\n\n")

        output_file.write(f"Executing command: {' '.join(command)}\n\n")

        # Run the command and capture output
        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            output_file.write(result.stdout)
        except subprocess.CalledProcessError as e:
            output_file.write(f"Error running OpenSSL speed test: {e}\n")
            output_file.write(e.stdout)
            return False

        output_file.write(f"\nTest completed. Results saved to {output_file_path}\n")

    print(f"Results saved to {output_file_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Run OpenSSL speed test')
    parser.add_argument('--algorithm', default='sha256', help='Hash algorithm')
    parser.add_argument('--seconds', default='3', help='Test duration in seconds')
    parser.add_argument('--bytes', default='16', help='Data block size in bytes')
    parser.add_argument('--multi', type=int, default=1, help='Number of parallel operations')
    parser.add_argument('--async_jobs', type=int, default=0, help='Number of async jobs')
    parser.add_argument('--misalign', type=int, default=0, help='Misalignment in bytes')
    parser.add_argument('--benchmark_items', help='Comma-separated list of benchmark items')
    parser.add_argument('--metrics', type=json.loads, default=[], help='JSON string of metrics')

    args = parser.parse_args()

    if run_openssl_speed_test(args):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()