import os
import csv
import re
import sys
import json

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

if base_dir not in sys.path:
    sys.path.append(base_dir)

from benchmarks.packages.kvs_parser import KVSParser

class ReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        parser = KVSParser()
        args = parser.parse_arguments()
        self.metrics = json.loads(args.metrics)

    def extract_metrics(self, output_content):
        # Initialize a dictionary to hold the extracted values
        extracted_metrics = {
            "latency(us)": {"READ": None, "UPDATE": None, "INSERT": None, "SCAN": None},
            "95latency(us)": {"READ": None, "UPDATE": None, "INSERT": None, "SCAN": None},
            "99latency(us)": {"READ": None, "UPDATE": None, "INSERT": None, "SCAN": None},
            "runtime(ms)": None,
            "throughput(ops/sec)": None,
            "operationcount": None,
            "readproportion": None,
            "updateproportion": None,
            "insertproportion": None,
            "scanproportion": None,
            "requestdistribution": None
        }

        # Use regular expressions to extract values
        for line in output_content.splitlines():
            # Extract overall runtime and throughput
            if "[OVERALL], RunTime(ms)" in line:
                extracted_metrics["runtime(ms)"] = int(re.search(r"\[OVERALL\], RunTime\(ms\), (\d+)", line).group(1))
            if "[OVERALL], Throughput(ops/sec)" in line:
                extracted_metrics["throughput(ops/sec)"] = float(re.search(r"\[OVERALL\], Throughput\(ops/sec\), ([\d.]+)", line).group(1))

            # Extract operation metrics (READ, UPDATE, INSERT, SCAN)
            for operation in ["READ", "UPDATE", "INSERT", "SCAN"]:
                if f"[{operation}]" in line:
                    # Latency (AverageLatency)
                    match_latency = re.search(r"AverageLatency\(us\), ([\d.]+)", line)
                    if match_latency:
                        extracted_metrics["latency(us)"][operation] = float(match_latency.group(1))
                        
                    # 95th Percentile Latency
                    match_95th = re.search(r"95thPercentileLatency\(us\), ([\d.]+)", line)
                    if match_95th:
                        extracted_metrics["95latency(us)"][operation] = float(match_95th.group(1))
                        
                    # 99th Percentile Latency
                    match_99th = re.search(r"99thPercentileLatency\(us\), ([\d.]+)", line)
                    if match_99th:
                        extracted_metrics["99latency(us)"][operation] = float(match_99th.group(1))

            # Extract operation count
            if "operationcount" in line:
                match_operation_count = re.search(r"operationcount=(\d+)", line)
                if match_operation_count:
                    extracted_metrics["operationcount"] = int(match_operation_count.group(1))

            # Extract operation proportions
            match_readproportion = re.search(r"readproportion=(\d+.\d+)", line)
            if match_readproportion:
                extracted_metrics['readproportion'] = float(match_readproportion.group(1))

            match_updateproportion = re.search(r"updateproportion=(\d+.\d+)", line)
            if match_updateproportion:
                extracted_metrics['updateproportion'] = float(match_updateproportion.group(1))

            match_insertproportion = re.search(r"insertproportion=(\d+.\d+)", line)
            if match_insertproportion:
                extracted_metrics['insertproportion'] = float(match_insertproportion.group(1))

            match_scanproportion = re.search(r"scanproportion=(\d+.\d+)", line)
            if match_scanproportion:
                extracted_metrics['scanproportion'] = float(match_scanproportion.group(1))
            else:
                extracted_metrics['scanproportion'] = 0.0  # Set default to 0.0 if not found

            # Extract request distribution
            if "requestdistribution" in line:
                match_request_distribution = re.search(r"requestdistribution=(.+)", line)
                if match_request_distribution:
                    extracted_metrics["requestdistribution"] = match_request_distribution.group(1)

        return extracted_metrics

    def generate_report(self):
        """Generate a report from output files."""
        report_data = []

        # Process each output file in the specified directory
        for filename in os.listdir(self.output_dir):
            if filename.startswith('output'):
                file_path = os.path.join(self.output_dir, filename)

                with open(file_path, 'r') as file:
                    content = file.read()
                    metrics_data = self.extract_metrics(content)

                    if metrics_data:
                        report_data.append(metrics_data)

        # Write the report data to CSV
        report_file = os.path.join(self.output_dir, 'report.csv')
        with open(report_file, 'w', newline='') as csvfile:
            fieldnames = ['operationcount', 'readproportion', 'updateproportion', 
                          'insertproportion', 'scanproportion', 'requestdistribution'] + self.metrics
            
            # Add units to latency, runtime, and throughput
            fieldnames = [name if name not in self.metrics else f"{name}(us)" if "latency" in name else f"{name}(ms)" if name == "runtime" else f"{name}(ops/sec)" for name in fieldnames]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data in report_data:
                # Convert None to empty strings for CSV
                data = {k: (v if v is not None else '') for k, v in data.items()}
                writer.writerow(data)

        print(f"Report generated: {report_file}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'output')

    report_generator = ReportGenerator(output_dir)
    report_generator.generate_report()
