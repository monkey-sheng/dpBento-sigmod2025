import argparse
import json
import os
import re
import csv
import logging
import numpy as np

# Regular expression patterns
iops_pattern = re.compile(r'IOPS=([\d.]+[kM]?)')
bw_pattern = re.compile(r'bw=([\d.]+[kM]?[KM]?iB/s)')
lat_avg_msec_pattern = re.compile(r'clat.*?lat \(msec\):.*?avg=([\d\.]+)', re.DOTALL)
lat_avg_usec_pattern = re.compile(r'clat.*?lat \(usec\):.*?avg=([\d\.]+)', re.DOTALL)

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
        return match.group(1)
    return None

def parse_benchmark_output(filepath):
    with open(filepath, 'r') as file:
        content = file.read()

    result = {}

    result['IOPS'] = convert_value(extract_value(iops_pattern, content)) if extract_value(iops_pattern, content) else 0
    result['bandwidth'] = convert_value(extract_value(bw_pattern, content)) if extract_value(bw_pattern, content) else 0
    
    if extract_value(lat_avg_msec_pattern, content):
        result['avg_latency'] = float(extract_value(lat_avg_msec_pattern, content))
    elif extract_value(lat_avg_usec_pattern, content):
        result['avg_latency'] = float(extract_value(lat_avg_usec_pattern, content)) / 1000  # Convert usec to msec
    else:
        result['avg_latency'] = 0

    return result

def process_files(output_folder, metrics):
    results = []
    percentiles_to_calculate = [int(metric.split()[0]) for metric in metrics if "percentile" in metric]

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

                    for filename in os.listdir(test_params_path):
                        if filename.startswith('run') and filename.endswith('.txt'):
                            filepath = os.path.join(test_params_path, filename)
                            parsed_output = parse_benchmark_output(filepath)
                            iops_list.append(parsed_output.get('IOPS', 0))
                            bw_list.append(parsed_output.get('bandwidth', 0))
                            latency_list.append(parsed_output.get('avg_latency', 0))

                    avg_iops = sum(iops_list) / len(iops_list) if iops_list else 0
                    avg_bw = sum(bw_list) / len(bw_list) if bw_list else 0
                    avg_latency = sum(latency_list) / len(latency_list) if latency_list else 0

                    result = {
                        'test_lst': test_lst,
                        'block_sizes': block_sizes,
                        'numProc': numProc,
                        'size': size,
                        'runtime': runtime,
                        'direct': direct,
                        'iodepth': iodepth,
                        'io_engine': io_engine,
                        'avg_latency': avg_latency,  # Always store avg_latency
                    }

                    if "bandwidth" in metrics:
                        result['bandwidth'] = avg_bw
                    if "IOPS" in metrics:
                        result['IOPS'] = avg_iops

                    logging.debug(f"latency list : {latency_list}")

                    if latency_list and percentiles_to_calculate:
                        latency_distribution = np.array(latency_list)
                        for percentile in percentiles_to_calculate:
                            percentile_value = np.percentile(latency_distribution, percentile)
                            result[f'{percentile}th_percentile_latency'] = percentile_value

                    results.append(result)

    return results

def save_to_csv(results, output_folder, metrics):
    base_fields = ['test_lst', 'block_sizes', 'numProc', 'size', 'runtime', 'direct', 'iodepth', 'io_engine']
    
    metric_fields_map = {
        'avg_latency': 'avg_latency',
        'bandwidth': 'bandwidth',
        'IOPS': 'IOPS',
    }
    
    required_fields = base_fields[:]
    for metric in metrics:
        if "percentile" in metric:
            percentile = metric.split()[0]
            required_fields.append(f'{percentile}th_percentile_latency')
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
            row = {field: None for field in required_fields}
            row.update({k: v for k, v in result.items() if k in required_fields})
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
