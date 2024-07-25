#!/bin/bash

# Default values
benchmark_name=""
output_folder=""
numjobs=4
block_sizes="1m"
size="1G"
runtime="30s"
direct=1
iodepth=32
io_engine="io_ring"
test_lst="randwrite,randread,write,read"
test_dir="/tmp/fio_test" 
log_file="fio_test_log.txt"

# Parse arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --benchmark_name)
      benchmark_name="$2"
      shift # past argument
      shift # past value
      ;;
    --output_folder)
      output_folder="$2"
      shift # past argument
      shift # past value
      ;;
    --numProc)
      numjobs="$2"
      shift # past argument
      shift # past value
      ;;
    --block_sizes)
      block_sizes="$2"
      shift # past argument
      shift # past value
      ;;
    --size)
      size="$2"
      shift # past argument
      shift # past value
      ;;
    --runtime)
      runtime="$2"
      shift # past argument
      shift # past value
      ;;
    --direct)
      direct="$2"
      shift # past argument
      shift # past value
      ;;
    --iodepth)
      iodepth="$2"
      shift # past argument
      shift # past value
      ;;
    --io_engine)
      io_engine="$2"
      shift # past argument
      shift # past value
      ;;
    --test_lst)
      test_lst="$2"
      shift # past argument
      shift # past value
      ;;
    *)
      shift # past argument
      ;;
  esac
done

# Ensure test_dir exists
if [ ! -d "$test_dir" ]; then
  mkdir -p "$test_dir"
fi

# Convert comma-separated strings to arrays
IFS=',' read -r -a test_lst_array <<< "$test_lst"

# Function to run FIO test and cleanup
run_fio_test() {
    local test_name=$1
    local block_size=$2
    local numjob=$3
    local size=$4
    local runtime=$5
    local direct=$6
    local iodepth=$7
    local ioengine=$8
    local run_count=5

    echo "Running FIO test: $test_name with block_size=$block_size, numjobs=$numjob, size=$size, runtime=$runtime, direct=$direct, iodepth=$iodepth, ioengine=$ioengine" | tee -a $log_file

    # Create the directory structure
    local test_run_dir="${output_folder}/${test_name}/${block_size}_${numjob}_${size}_${runtime}_${direct}_${iodepth}_${ioengine}"
    mkdir -p "$test_run_dir"

    for i in $(seq 1 $run_count); do
        local temp_output_file="${test_run_dir}/run${i}.txt"
        echo "Run #${i}" | tee -a $log_file
        fio --name=$test_name --ioengine=$ioengine --rw=$test_name --bs=$block_size --direct=$direct --size=$size --numjobs=$numjob --iodepth=$iodepth --runtime=$runtime --group_reporting --directory=$test_dir --output=$temp_output_file 2>&1 | tee -a $log_file
        
        echo "Results saved to $temp_output_file" | tee -a $log_file

        # Clean up test files for each run
        rm -rf ${test_dir}/*
    done
    echo "Cleaning up test files for: $test_name with block_size=$block_size, numjobs=$numjob, size=$size, runtime=$runtime, direct=$direct, iodepth=$iodepth, ioengine=$ioengine" | tee -a $log_file
}

# Run the actual benchmark
for test in "${test_lst_array[@]}"; do
    run_fio_test $test $block_sizes $numjobs $size $runtime $direct $iodepth $io_engine
done
