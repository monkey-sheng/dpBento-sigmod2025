import os
import csv
import re
import sys

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

if base_dir not in sys.path:
    sys.path.append(base_dir)
    
from benchmarks.packages.kvs_parser import KVSParser

class ReportGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        parser = KVSParser()
        args = parser.parse_arguments()
        self.metrics = args.metric

    def extract_metrics(self, output_content):
        """Extract metrics from output content."""
        metrics_data = {}
        
        # Find the overall runtime and throughput
        overall_match = re.findall(r'\[OVERALL\], (.+?), ([\d.]+)', output_content)
        for metric, value in overall_match:
            if metric in self.metrics:
                metrics_data[metric] = float(value)
        
        # Extracting configuration parameters
        operation_count_match = re.search(r'operationcount=(\d+)', output_content)
        read_proportion_match = re.search(r'readproportion=(\d+\.?\d*)', output_content)
        update_proportion_match = re.search(r'updateproportion=(\d+\.?\d*)', output_content)
        insert_proportion_match = re.search(r'insertproportion=(\d+\.?\d*)', output_content)
        scan_proportion_match = re.search(r'scanproportion=(\d+\.?\d*)', output_content)
        request_distribution_match = re.search(r'requestdistribution=(\w+)', output_content)

        if operation_count_match:
            metrics_data['operationcount'] = int(operation_count_match.group(1))
        if read_proportion_match:
            metrics_data['readproportion'] = float(read_proportion_match.group(1))
        if update_proportion_match:
            metrics_data['updateproportion'] = float(update_proportion_match.group(1))
        if insert_proportion_match:
            metrics_data['insertproportion'] = float(insert_proportion_match.group(1))
        if scan_proportion_match:
            metrics_data['scanproportion'] = float(scan_proportion_match.group(1))
        if request_distribution_match:
            metrics_data['requestdistribution'] = request_distribution_match.group(1)

        return metrics_data

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
            fieldnames = ['operationcount', 'readproportion', 'updateproportion', 'insertproportion', 
                          'scanproportion', 'requestdistribution'] + self.metrics
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for data in report_data:
                writer.writerow(data)

        print(f"Report generated: {report_file}")


if __name__ == "__main__":
    output_directory = 'output'  # Adjust as necessary
    report_generator = ReportGenerator(output_directory)
    report_generator.generate_report()
