import argparse
import json
import os
import re
import csv
import logging
import numpy as np

iops_pattern = re.compile(r'IOPS=([\d.]+[kM]?)')
bw_pattern = re.compile(r'BW=([\d.]+[kM]?[KM]?iB/s)')
lat_pattern = re.compile(r'^\s*lat \((\w+)\):\s*min=[\d.]+,\s*max=[\d.]+,\s*avg=([\d.]+),\s*stdev=[\d.]+', re.MULTILINE)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate report from benchmark test results.')
    parser.add_argument('--metrics', type=str, required=True, help='JSON string of metrics to report')
    return parser.parse_args()

def convert_value(value):
    if isinstance(value, str):
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

    runs = content.split("\nRun #")
    results = []

    for run in runs[1:]:  # Skip the first split part before 'Run1'
        result = {}

        # Find the section containing clat and lat information
        clat_lat_section = re.search(r'clat.*?lat.*?clat percentiles', run, re.DOTALL)
        if clat_lat_section:
            lat_match = lat_pattern.search(clat_lat_section.group())
            if lat_match:
                unit, value = lat_match.groups()
                if unit == 'nsec':
                    result['avg_latency'] = float(value) / 1e6  # Convert nsec to msec
                elif unit == 'usec':
                    result['avg_latency'] = float(value) / 1e3  # Convert usec to msec
                elif unit == 'msec':
                    result['avg_latency'] = float(value)  # Already in msec
                else:
                    logging.warning(f"Unknown latency unit: {unit}")
                    continue
            else:
                logging.warning(f"Could not find lat information in the clat-lat section")
                continue
        else:
            logging.warning(f"Could not find clat-lat section in a run")
            continue

        iops = extract_value(iops_pattern, run)
        bw = extract_value(bw_pattern, run)
        
        result['IOPS'] = convert_value(iops) if iops else 0
        result['bandwidth'] = convert_value(bw) if bw else 0
        
        results.append(result)

    return results

def process_files(output_folder, metrics):
    results = []
    percentiles_to_calculate = [int(metric.split()[0]) for metric in metrics if "percentile" in metric]

    for test_type in ['randread', 'randwrite', 'read', 'write']:
        test_type_dir = os.path.join(output_folder, test_type)
        if not os.path.isdir(test_type_dir):
            continue

        for dir_name in os.listdir(test_type_dir):
            dir_path = os.path.join(test_type_dir, dir_name)
            if not os.path.isdir(dir_path):
                continue

            filepath = os.path.join(dir_path, "combined_results.txt")
            if not os.path.exists(filepath):
                logging.warning(f"combined_results.txt not found in {dir_path}")
                continue

            logging.info(f"Processing file: {filepath}")
            
            parsed_outputs = parse_benchmark_output(filepath)
            
            if not parsed_outputs:
                logging.warning(f"No data extracted from {filepath}")
                continue

            iops_list = [output.get('IOPS', 0) for output in parsed_outputs]
            bw_list = [output.get('bandwidth', 0) for output in parsed_outputs]
            latency_list = [output.get('avg_latency', 0) for output in parsed_outputs]

            avg_iops = sum(iops_list) / len(iops_list) if iops_list else 0
            avg_bw = sum(bw_list) / len(bw_list) if bw_list else 0
            avg_latency = sum(latency_list) / len(latency_list) if latency_list else 0

            # Parse directory name for parameters
            params_match = re.match(r'(\w+)_(\d+)_(\w+)_(\w+)_(\d+)_(\d+)_(.+)', dir_name)
            
            if not params_match:
                logging.error(f"Unexpected directory name format: {dir_name}")
                continue

            block_size, numProc, size, runtime, direct, iodepth, io_engine = params_match.groups()

            result = {
                'test_lst': 'storage',  # Assuming 'storage' is the top-level directory
                'test_type': test_type,
                'block_sizes': block_size,
                'numProc': numProc,
                'size': size,
                'runtime': runtime,
                'direct': direct,
                'iodepth': iodepth,
                'io_engine': io_engine,
                'avg_latency': avg_latency,
            }

            if "bandwidth" in metrics:
                result['bandwidth'] = avg_bw
            if "IOPS" in metrics:
                result['IOPS'] = avg_iops

            if latency_list and percentiles_to_calculate:
                latency_distribution = np.array(latency_list)
                for percentile in percentiles_to_calculate:
                    percentile_value = np.percentile(latency_distribution, percentile)
                    result[f'{percentile}th_percentile_latency'] = percentile_value

            results.append(result)
            logging.info(f"Processed test: {test_type}, block size: {block_size}, io_engine: {io_engine}")

    return results

def save_to_csv(results, output_folder, metrics):
    base_fields = ['test_lst', 'test_type', 'block_sizes', 'numProc', 'size', 'runtime', 'direct', 'iodepth', 'io_engine']
    
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
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=required_fields)
        writer.writeheader()
        for result in results:
            row = {field: result.get(field, '') for field in required_fields}
            writer.writerow(row)
    
    logging.info(f"Results saved to {output_file}")

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        args = parse_arguments()
        metrics = json.loads(args.metrics)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing metrics: {e}")
        return
    except Exception as e:
        logging.error(f"Error parsing arguments: {e}")
        return

    output_folder = os.path.join(os.path.dirname(__file__), 'output')
    logging.info(f"Output folder: {output_folder}")

    try:
        results = process_files(output_folder, metrics)
    except Exception as e:
        logging.error(f"Error processing files: {e}", exc_info=True)
        return

    try:
        save_to_csv(results, output_folder, metrics)
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}", exc_info=True)

    print("Storage report.py successfully completed.")

if __name__ == '__main__':
    main()
