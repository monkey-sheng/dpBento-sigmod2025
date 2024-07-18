import json
import subprocess
import time
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

class BenchmarkItem:
    def __init__(self, benchmark_name, test_parameters, dpdento_root, output_folder):
        self.benchmark_name = benchmark_name
        self.test_parameters = test_parameters
        self.dpdento_root = dpdento_root
        self.output_folder = output_folder

    def initialize(self):
        # Initialization logic, if any
        pass

    def run(self):
        results = []
        for sf in self.test_parameters['scale_factors']:
            for query_num in self.test_parameters['query_numbers']:
                query_name = f"Q{query_num}"
                cmd = f"PRAGMA tpch({query_num});"
                
                # Timing query execution
                start_time = time.time()
                try:
                    # Execute the PRAGMA tpch command
                    subprocess.run(cmd, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error executing query {query_name} for SF={sf}: {str(e)}")
                    continue
                end_time = time.time()
                
                run_time = end_time - start_time
                results.append({
                    'Scale Factor': sf,
                    'Query': query_name,
                    'Run Time (s)': run_time
                })

        results_df = pd.DataFrame(results)
        results_csv_path = os.path.join(self.output_folder, f'{self.benchmark_name}_results.csv')
        results_df.to_csv(results_csv_path, index=False)
        return results_df

    def plot(self, results_df, visualization_option):
        if visualization_option == 'average':
            avg_df = results_df.groupby('Scale Factor')['Run Time (s)'].mean().reset_index()
            plt.bar(avg_df['Scale Factor'], avg_df['Run Time (s)'])
            plt.xlabel('Scale Factor')
            plt.ylabel('Average Run Time (s)')
            plt.title('Average Run Time per Scale Factor')
        elif visualization_option == 'individual':
            for query in results_df['Query'].unique():
                query_df = results_df[results_df['Query'] == query]
                plt.plot(query_df['Scale Factor'], query_df['Run Time (s)'], label=query)
            plt.xlabel('Scale Factor')
            plt.ylabel('Run Time (s)')
            plt.title('Run Time for Each Query')
            plt.legend()
        else:
            raise ValueError("Invalid visualization option")
        
        plot_path = os.path.join(self.output_folder, f'{self.benchmark_name}_plot.png')
        plt.savefig(plot_path)
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="Run and visualize TPC-H benchmark.")
    parser.add_argument('--config', type=str, required=True, help="Path to the JSON config file.")
    parser.add_argument('--visualize', type=str, required=False, default='average', help="Visualization option: 'average' or 'individual'.")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)

    benchmark = BenchmarkItem(
        benchmark_name=config['benchmark_name'],
        test_parameters=config['test_parameters'],
        dpdento_root=config['dpdento_root'],
        output_folder=config['output_folder']
    )

    benchmark.initialize()
    results_df = benchmark.run()
    benchmark.plot(results_df, args.visualize)

if __name__ == "__main__":
    main()
