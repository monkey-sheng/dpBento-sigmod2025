import os
# import time
# import pandas as pd
# import duckdb
# from pathlib import Path
import sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if base_dir not in sys.path:
    sys.path.append(base_dir)

from packages.e2e_parser import E2EParser
from packages.e2e_runner import E2ERunner

# def parse_arguments():
#     parser = argparse.ArgumentParser(description='Run E2E benchmark tests.')
    
#     # Dynamically add arguments based on the parameters passed from run_dpdbento.py
#     parser.add_argument('--benchmark_items', type=str, required=True, help='Comma-separated list of benchmark items')

#     # Add command-line arguments
#     parser.add_argument('--scale_factor', type=int, help='Scale factor for the benchmark')
#     parser.add_argument('--query', type=str, help='Query name or number to execute')
#     parser.add_argument('--execution_mode', type=str, choices=['cold', 'hot'], help='Execution mode: cold or hot')
    
#     return parser.parse_args()

# def create_directory(directory):
#     if not os.path.exists(directory):
#         os.makedirs(directory)

#  for every query(they can choose what to include)
# def run_benchmark_test(scale_factors, query_numbers, execution_modes, output_folder, log_file):
#     results = []

#     for sf in scale_factors:
#         duckdb_file_path = f'sf{sf}'  

#         with duckdb.connect(database=duckdb_file_path, read_only=True) as conn:
#             conn.execute("LOAD tpch")
#             conn.execute(f"CALL dbgen(sf={sf})")
#             print(f"Data generated for SF={sf} in DuckDB database at {duckdb_file_path}", file=log_file)

#             for query_num in query_numbers:
#                 query_name = f"Q{query_num}"
#                 cmd = f"PRAGMA tpch({query_num});"

#                 for execution_mode in execution_modes:
#                     if execution_mode == "cold":
                        
#                         start_time = time.time()
#                         conn.execute(cmd)
#                         end_time = time.time()

#                         run_time = end_time - start_time
#                         results.append({
#                             'Scale Factor': sf,
#                             'Query': query_name,
#                             'Execution Mode': execution_mode,
#                             'Run Time (s)': run_time
#                         })
#                     elif execution_mode == "hot":
#                         run_times = []
#                         for i in range(4):
#                             start_time = time.time()
#                             conn.execute(cmd)
#                             end_time = time.time()
#                             if i > 0:  # Ignore the first run
#                                 run_times.append(end_time - start_time)
                        
#                         run_time = sum(run_times) / len(run_times)
#                         results.append({
#                             'Scale Factor': sf,
#                             'Query': query_name,
#                             'Execution Mode': execution_mode,
#                             'Run Time (s)': run_time
#                         })

#     # Calculate average run time for all queries
#     results_df = pd.DataFrame(results)
#     avg_runtime_all_queries = results_df['Run Time (s)'].mean() if 'Run Time (s)' in results_df.columns else results_df['Average Run Time (s)'].mean()
#     results_df.loc[len(results_df)] = [None, 'avg', execution_mode, avg_runtime_all_queries]

#     for sf in scale_factors:
#         sf_results = results_df[results_df['Scale Factor'] == sf]
#         if 'Run Time (s)' in sf_results.columns:
#             avg_runtime_sf = sf_results['Run Time (s)'].mean()
#         else:
#             avg_runtime_sf = sf_results['Average Run Time (s)'].mean()
#         results_df.loc[len(results_df)] = [sf, 'avg', execution_mode, avg_runtime_sf]

#     results_csv_path = os.path.join(output_folder, 'results.csv')
#     results_df.to_csv(results_csv_path, index=False)
#     return results_df

if __name__ == '__main__':
    e2e_parser = E2EParser()
    args = e2e_parser.parse_arguments()
    
    e2e_runner = E2ERunner(args)
    e2e_runner.run_benchmark_test(args.scale_factors, args.query, args.execution_mode, e2e_runner.output_dir, e2e_runner.log_file)
    e2e_runner.close_log_file()
