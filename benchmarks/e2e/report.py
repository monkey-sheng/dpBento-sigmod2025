import argparse
import json
import os
import re
import csv

# Regular expression patterns
iops_pattern = re.compile(r'IOPS=([\d.]+[kM]?)')
bw_pattern = re.compile(r'bw=([\d.]+[kM]?[KM]?iB/s)')
lat_avg_msec_pattern = re.compile(r'clat.*?lat \(msec\):.*?avg=([\d\.]+).*?clat percentiles', re.DOTALL)
lat_avg_usec_pattern = re.compile(r'clat.*?lat \(usec\):.*?avg=([\d\.]+).*?clat percentiles', re.DOTALL)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate report from FIO test results.')
    parser.add_argument('--metrics', type=str, required=True, help='JSON string of metrics to report')
    parser.add_argument('--output_folder', type=str, required=True, help='Output folder for results')
    return parser.parse_args()

# Convert values with suffixes (k, M, KiB, MiB) to MiB or proper units
def convert_value(value):
    if value.endswith('k'):
        return float(value[:-1]) * 1e3
    elif value.endswith('M'):
        return float(value[:-1]) * 1e6
    elif value.endswith('KiB/s'):
        return float(value[:-5]) / 1024  # Convert KiB/s to MiB/s
    elif value.endswith('MiB/s'):
        return float(value[:-5])
    elif value.endswith('KB/s'):
        return float(value[:-4]) / 1024  # Convert KB/s to MiB/s
    elif value.endswith('MB/s'):
        return float(value[:-4])
    return float(value)

def extract_value(pattern, text):
    match = pattern.search(text)
    if match:
        return match.group(1)
    return None

def parse_fio_output(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
        
    iops = convert_value(extract_value(iops_pattern, content)) if extract_value(iops_pattern, content) else 0
    bw = convert_value(extract_value(bw_pattern, content)) if extract_value(bw_pattern, content) else 0
    if extract_value(lat_avg_msec_pattern, content):
        latency = float(extract_value(lat_avg_msec_pattern, content))
    elif extract_value(lat_avg_usec_pattern, content):
        latency = float(extract_value(lat_avg_usec_pattern, content)) / 1000  # convert usec to msec
    else:
        latency = 0

    print(f"Parsed values from {filepath} -> IOPS: {iops}, Bandwidth: {bw} MiB/s, Latency: {latency} ms")
    return iops, bw, latency

def process_files(output_folder):
    iops_list, bw_list, latency_list = [], [], []

    for subdir, _, files in os.walk(output_folder):
        for filename in files:
            if filename.startswith('run') and filename.endswith('.txt'):
                filepath = os.path.join(subdir, filename)
                iops, bw, latency = parse_fio_output(filepath)
                iops_list.append(iops)
                bw_list.append(bw)
                latency_list.append(latency)

    avg_iops = sum(iops_list) / len(iops_list) if iops_list else 0
    avg_bw = sum(bw_list) / len(bw_list) if bw_list else 0
    avg_latency = sum(latency_list) / len(latency_list) if latency_list else 0

    print(f"Calculated averages -> IOPS: {avg_iops}, Bandwidth: {avg_bw} MiB/s, Latency: {avg_latency} ms")
    return avg_iops, avg_bw, avg_latency

def save_to_csv(output_folder, test_params, avg_iops, avg_bw, avg_latency):
    # Save the results.csv file in the parent directory of the output_folder
    output_file = os.path.join(os.path.dirname(output_folder), 'results.csv')
    # Define the required fields
    required_fields = ['numProc', 'block_sizes', 'size', 'runtime', 'direct', 'iodepth', 'io_engine', 'test_lst', 'avg_latency', 'avg_bandwidth', 'avg_IOPS']
    headers = required_fields
    
    # Filter test_params to include only required fields
    filtered_test_params = {key: test_params[key] for key in required_fields if key in test_params}
    
    # Prepare the row with average metrics
    row = {**filtered_test_params, 'avg_latency': avg_latency, 'avg_bandwidth': avg_bw, 'avg_IOPS': avg_iops}

    if not os.path.exists(output_file):
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
    
    with open(output_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writerow(row)

def main():
    args = parse_arguments()
    metrics = json.loads(args.metrics)

    # Extract environment variables for test parameters
    test_params = {key: os.environ[key] for key in ['numProc', 'block_sizes', 'size', 'runtime', 'direct', 'iodepth', 'io_engine', 'test_lst']}
    output_folder = args.output_folder

    avg_iops, avg_bw, avg_latency = process_files(output_folder)
    
    save_to_csv(output_folder, test_params, avg_iops, avg_bw, avg_latency)

if __name__ == '__main__':
    main()