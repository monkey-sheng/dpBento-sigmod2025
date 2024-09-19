#!/bin/bash

# Default parameters
algorithm="sha256"
seconds=3
bytes=16
multi=1
async_jobs=0
misalign=0
output_file="openssl_speed_results.txt"

# Help function
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --algorithm ALGORITHM   Hash algorithm (default: sha256)"
    echo "  --seconds SECONDS       Test duration in seconds (default: 3)"
    echo "  --bytes BYTES           Data block size in bytes (default: 16)"
    echo "  --multi MULTI           Number of parallel operations (default: 1)"
    echo "  --async_jobs ASYNC_JOBS Number of async jobs (default: 0)"
    echo "  --misalign MISALIGN     Misalignment in bytes (default: 0)"
    echo "  --output OUTPUT_FILE    Output file name (default: openssl_speed_results.txt)"
    echo "  --help                  Show this help message"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --algorithm) algorithm="$2"; shift 2 ;;
        --seconds) seconds="$2"; shift 2 ;;
        --bytes) bytes="$2"; shift 2 ;;
        --multi) multi="$2"; shift 2 ;;
        --async_jobs) async_jobs="$2"; shift 2 ;;
        --misalign) misalign="$2"; shift 2 ;;
        --output) output_file="$2"; shift 2 ;;
        --help) show_help; exit 0 ;;
        *) echo "Unknown option $1"; show_help; exit 1 ;;
    esac
done

# Build OpenSSL speed command
command="openssl speed -elapsed -seconds $seconds -bytes $bytes -multi $multi"

# Add optional parameters
if [ $async_jobs -gt 0 ]; then
    command="$command -async_jobs $async_jobs"
fi

if [ $misalign -gt 0 ]; then
    command="$command -misalign $misalign"
fi

# Add algorithm
command="$command $algorithm"

# Run the test and redirect results to file
echo "Running OpenSSL speed test with the following parameters:" | tee "$output_file"
echo "Algorithm: $algorithm" | tee -a "$output_file"
echo "Test duration: $seconds seconds" | tee -a "$output_file"
echo "Data block size: $bytes bytes" | tee -a "$output_file"
echo "Parallel operations: $multi" | tee -a "$output_file"
echo "Async jobs: $async_jobs" | tee -a "$output_file"
echo "Misalignment: $misalign bytes" | tee -a "$output_file"
echo "" | tee -a "$output_file"

echo "Executing command: $command" | tee -a "$output_file"
echo "" | tee -a "$output_file"

$command 2>&1 | tee -a "$output_file"

echo "" | tee -a "$output_file"
echo "Test completed. Results saved to $output_file"