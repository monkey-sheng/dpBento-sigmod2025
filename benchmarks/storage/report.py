import argparse
import json
import os
import re
import csv
import logging

# Regular expression patterns
iops_pattern = re.compile(r'IOPS=([\d.]+[kM]?)')
bw_pattern = re.compile(r'bw=([\d.]+[kM]?[KM]?iB/s)')
lat_avg_msec_pattern = re.compile(r'clat.*?lat \(msec\):.*?avg=([\d\.]+).*?clat percentiles', re.DOTALL)
lat_avg_usec_pattern = re.compile(r'clat.*?lat \(usec\):.*?avg=([\d\.]+).*?clat percentiles', re.DOTALL)
percentile_section_pattern = re.compile(r'clat percentiles.*?\n(.*?)bw', re.DOTALL)
percentiles_pattern = re.compile(r'\|\s+(\d+\.\d+th)=\s*\[\s*(\d+)\s*\]')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate report from benchmark test results.')
    parser.add_argument('--metrics', type=str, required=True, help='JSON string of metrics to report')
    return parser.parse_args()

# Convert values with suffixes (k, M, KiB, MiB) to appropriate units
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
        print(f"Extracted value: {match.group(1)}")  # Debug output
        return match.group(1)
    print("No match found.")  # Debug output
    return None

def extract_percentiles_section(text):
    match = percentile_section_pattern.search(text)
    if not match:
        print("No percentiles section match found.")  # Debug output
        print(f"Text content for debugging:\n{text}")  # Debug output
        return ""

    print(f"Percentiles section match found: {match.group(1)}")  # Debug output
    return match.group(1)

def extract_percentiles(percentiles_text):
    # Extracting percentiles using the updated pattern that accounts for spaces
    percentiles = re.findall(percentiles_pattern, percentiles_text)
    percentiles_dict = {percentile.strip(): int(value.strip()) for percentile, value in percentiles}
    print(f"Extracted percentiles: {percentiles_dict}")  # Debug output
    return percentiles_dict


def parse_benchmark_output(filepath, metrics):
    print(f"Parsing file: {filepath}")  # Debug output
    with open(filepath, 'r') as file:
        content = file.read()
    print(f"File content:\n{content}\n")  # Debug output

    result = {}
    if "IOPS" in metrics:
        result['IOPS'] = convert_value(extract_value(iops_pattern, content)) if extract_value(iops_pattern, content) else 0
        print(f"Extracted IOPS: {result['IOPS']}")  # Debug output
    if "bandwidth" in metrics:
        result['bandwidth'] = convert_value(extract_value(bw_pattern, content)) if extract_value(bw_pattern, content) else 0
        print(f"Extracted bandwidth: {result['bandwidth']}")  # Debug output
    if "avg_latency" in metrics:
        if extract_value(lat_avg_msec_pattern, content):
            result['avg_latency'] = float(extract_value(lat_avg_msec_pattern, content))
        elif extract_value(lat_avg_usec_pattern, content):
            result['avg_latency'] = float(extract_value(lat_avg_usec_pattern, content)) / 1000  # Convert usec to msec
        else:
            result['avg_latency'] = 0
        print(f"Extracted avg_latency: {result['avg_latency']}")  # Debug output

    # Check for percentile_clatency entries in metrics
    percentiles_section = extract_percentiles_section(content)
    if percentiles_section:
        percentiles = extract_percentiles(percentiles_section)
        for metric in metrics:
            if "percentile" in metric:
                percentile_key = metric.split()[0] + ".00th"
                if percentile_key in percentiles:
                    result[percentile_key] = percentiles[percentile_key]
                    print(f"Extracted {percentile_key}: {result[percentile_key]}")  # Debug output
                else:
                    print(f"Missing percentile: {percentile_key}")  # Debug output

    return result



def process_files(output_folder, metrics):
    results = []

    for test_lst in os.listdir(output_folder):
        test_lst_path = os.path.join(output_folder, test_lst)
        if os.path.isdir(test_lst_path):
            for test_params_dir in os.listdir(test_lst_path):
                test_params_path = os.path.join(test_lst_path, test_params_dir)
                if os.path.isdir(test_params_path):
                    params = test_params_dir.split('_')
                    if len(params) < 7:
                        logging.error(f"Unexpected directory name format: {test_params_dir}")
                        continue
                    
                    block_sizes = params[0]
                    numProc = params[1]
                    size = params[2]
                    runtime = params[3]
                    direct = params[4]
                    iodepth = params[5]
                    io_engine = '_'.join(params[6:])
                    
                    iops_list, bw_list, latency_list = [], [], []
                    percentile_lists = {metric.split()[0] + ".00th": [] for metric in metrics if "percentile" in metric}

                    for filename in os.listdir(test_params_path):
                        if filename.startswith('run') and filename.endswith('.txt'):
                            filepath = os.path.join(test_params_path, filename)
                            parsed_output = parse_benchmark_output(filepath, metrics)
                            if "IOPS" in metrics:
                                iops_list.append(parsed_output.get('IOPS', 0))
                            if "bandwidth" in metrics:
                                bw_list.append(parsed_output.get('bandwidth', 0))
                            if "avg_latency" in metrics:
                                latency_list.append(parsed_output.get('avg_latency', 0))
                            for percentile in percentile_lists.keys():
                                if percentile in parsed_output:
                                    percentile_lists[percentile].append(parsed_output[percentile])
                    
                    print(f"IOPS list: {iops_list}")  # Debug output
                    print(f"Bandwidth list: {bw_list}")  # Debug output
                    print(f"Latency list: {latency_list}")  # Debug output
                    print(f"Percentile lists: {percentile_lists}")  # Debug output

                    avg_iops = sum(iops_list) / len(iops_list) if iops_list else 0
                    avg_bw = sum(bw_list) / len(bw_list) if bw_list else 0
                    avg_latency = sum(latency_list) / len(latency_list) if latency_list else 0
                    avg_percentiles = {key: (sum(values) / len(values)) if values else None for key, values in percentile_lists.items()}

                    result = {
                        'test_lst': test_lst,
                        'block_sizes': block_sizes,
                        'numProc': numProc,
                        'size': size,
                        'runtime': runtime,
                        'direct': direct,
                        'iodepth': iodepth,
                        'io_engine': io_engine
                    }

                    if "avg_latency" in metrics:
                        result['avg_latency'] = avg_latency
                    if "bandwidth" in metrics:
                        result['bandwidth'] = avg_bw
                    if "IOPS" in metrics:
                        result['IOPS'] = avg_iops
                    result.update(avg_percentiles)

                    print(f"Result: {result}")  # Debug output

                    results.append(result)

    return results


def save_to_csv(results, output_folder, metrics):
    # Define the base fields that should always be included
    base_fields = ['test_lst', 'block_sizes', 'numProc', 'size', 'runtime', 'direct', 'iodepth', 'io_engine']
    # Define the possible metric fields
    metric_fields_map = {
        'avg_latency': 'avg_latency',
        'bandwidth': 'bandwidth',
        'IOPS': 'IOPS',
    }
    
    # Generate the required fields based on the metrics provided
    required_fields = base_fields[:]
    for metric in metrics:
        if "percentile" in metric:
            required_fields.append(metric.split()[0] + ".00th")
        elif metric in metric_fields_map:
            required_fields.append(metric_fields_map[metric])
    
    output_file = os.path.join(output_folder, 'results.csv')
    
    if not os.path.exists(output_file):
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=required_fields)
            writer.writeheader()
    
    with open(output_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=required_fields)
        for result in results:
            # Initialize row with all fields set to None
            row = {field: None for field in required_fields}
            # Update row with actual results
            row.update(result)
            writer.writerow(row)

def main():
    logging.basicConfig(level=logging.DEBUG)
    args = parse_arguments()
    try:
        metrics = json.loads(args.metrics)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing metrics: {e}")
        return

    output_folder = os.path.join(os.path.dirname(__file__), 'output')

    try:
        results = process_files(output_folder, metrics)
    except Exception as e:
        logging.error(f"Error processing files: {e}")
        return

    try:
        save_to_csv(results, output_folder, metrics)
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")

    print("Storage report.py successfully completed.")

if __name__ == '__main__':
    main()
