import os
import argparse
import subprocess
import json
import time
import pandas as pd
import duckdb
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run E2E benchmark tests.')
    
    # Add command-line arguments
    parser.add_argument('--benchmark_config', type=str, required=True, help='Path to the JSON benchmark configuration file')
    parser.add_argument('--scale_factor', type=int, help='Scale factor for the benchmark')
    parser.add_argument('--query', type=str, help='Query name or number to execute')
    parser.add_argument('--execution_mode', type=str, choices=['cold', 'hot'], help='Execution mode: cold or hot')
    
    return parser.parse_args()

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def run_setup_script(benchmark_name):
    setup_script_path = os.path.join(os.path.dirname(__file__), 'setup.sh')
    subprocess.run(['bash', setup_script_path, benchmark_name], check=True)

def run_clean_script():
    clean_script_path = os.path.join(os.path.dirname(__file__), 'clean.sh')
    subprocess.run(['bash', clean_script_path], check=True)

#  for every query(they can choose what to include)
def run_benchmark_test(scale_factors, query_numbers, execution_modes, output_folder, log_file):
    results = []
    parquet_base_dir = Path('/tmp/e2e_test')

    for sf in scale_factors:
        duckdb_file_path = f'sf{sf}'  

        with duckdb.connect(database=duckdb_file_path, read_only=True) as conn:
            conn.execute("LOAD tpch")
            conn.execute(f"CALL dbgen(sf={sf})")
            print(f"Data generated for SF={sf} in DuckDB database at {duckdb_file_path}", file=log_file)

            for query_num in query_numbers:
                query_name = f"Q{query_num}"
                cmd = f"PRAGMA tpch({query_num});"

                for execution_mode in execution_modes:
                    if execution_mode == "cold":
                        
                        start_time = time.time()
                        conn.execute(cmd)
                        end_time = time.time()

                        run_time = end_time - start_time
                        results.append({
                            'Scale Factor': sf,
                            'Query': query_name,
                            'Execution Mode': execution_mode,
                            'Run Time (s)': run_time
                        })
                    elif execution_mode == "hot":
                        run_times = []
                        for i in range(4):
                            start_time = time.time()
                            conn.execute(cmd)
                            end_time = time.time()
                            if i > 0:  # Ignore the first run
                                run_times.append(end_time - start_time)
                        
                        run_time = sum(run_times) / len(run_times)
                        results.append({
                            'Scale Factor': sf,
                            'Query': query_name,
                            'Execution Mode': execution_mode,
                            'Run Time (s)': run_time
                        })

    # Calculate average run time for all queries
    results_df = pd.DataFrame(results)
    avg_runtime_all_queries = results_df['Run Time (s)'].mean() if 'Run Time (s)' in results_df.columns else results_df['Average Run Time (s)'].mean()
    results_df.loc[len(results_df)] = [None, 'avg', execution_mode, avg_runtime_all_queries]

    for sf in scale_factors:
        sf_results = results_df[results_df['Scale Factor'] == sf]
        if 'Run Time (s)' in sf_results.columns:
            avg_runtime_sf = sf_results['Run Time (s)'].mean()
        else:
            avg_runtime_sf = sf_results['Average Run Time (s)'].mean()
        results_df.loc[len(results_df)] = [sf, 'avg', execution_mode, avg_runtime_sf]

    results_csv_path = os.path.join(output_folder, 'e2e_test_results.csv')
    results_df.to_csv(results_csv_path, index=False)
    return results_df

def main():
    args = parse_arguments()
    
    with open(args.benchmark_config, 'r') as f:
        config = json.load(f)
    
    scale_factors = [args.scale_factor] if args.scale_factor else config["test_parameters"]["scale_factors"]
    query_numbers = [args.query] if args.query else config["test_parameters"]["query_numbers"]
    execution_modes = [args.execution_mode] if args.execution_mode else config["test_parameters"]["executionMode"]
    
    output_folder = config["output_folder"]
    benchmark_name = config["benchmark_name"]
    
    log_file_path = os.path.join(output_folder, "e2e_test_log.txt")

    # Run setup script
    run_setup_script(benchmark_name)
    
    with open(log_file_path, 'a') as log_file:
        create_directory(output_folder)
        
        run_benchmark_test(scale_factors, query_numbers, execution_modes, output_folder, log_file)
        run_clean_script()

if __name__ == '__main__':
    main()
