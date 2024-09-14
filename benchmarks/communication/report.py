import argparse
import os
import csv

def parse_arguments():
    parser = argparse.ArgumentParser(description='Communication benchmark')
    parser.add_argument('--metrics', type=str, default='', help='Metrics to collect in the generated file')
    args = parser.parse_args()
    return args

def parse_rdma_output():
    output_file = os.path.join(os.path.dirname(__file__), 'output', 'RDMA', 'output.txt')
    
    if not os.path.exists(output_file):
        print(f"No such file or directory: '{output_file}'")
        return

    with open(output_file, 'r') as f:
        contents = f.read()

    # Split the content into sections separated by the separator line
    sections = contents.split('---------------------------------------------------------------------------------------')

    # Find the section that contains the table
    table_section = None
    for section in sections:
        if '#bytes' in section:
            table_section = section
            break

    if table_section is None:
        print('Table section not found in output.')
        return

    # Clean and split the table section into lines
    lines = [line.strip() for line in table_section.strip().split('\n') if line.strip()]

    if len(lines) < 2:
        print('Not enough lines in table section.')
        return

    header_line = lines[0]
    data_line = lines[1]

    # Correctly handling '99%' and '99.9%' percentile headers
    header_line = header_line.replace('99% percentile[usec]', '99_percentile[usec]').replace('99.9% percentile[usec]', '99.9_percentile[usec]')
    header_fields = header_line.split()
    data_values = data_line.split()

    if len(header_fields) != len(data_values):
        print('Number of data values does not match number of header fields.')
        return

    # Write the headers and data into a CSV file
    output_csv = os.path.join(os.path.dirname(__file__), 'output', 'RDMA', 'output.csv')
    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header_fields)
        csvwriter.writerow(data_values)

    print(f'Data successfully written to {output_csv}')

if __name__ == '__main__':
    args = parse_arguments()
    parse_rdma_output()
