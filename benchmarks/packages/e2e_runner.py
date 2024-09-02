import os
import time
import pandas as pd
import duckdb
from pathlib import Path
from .runner import Runner
import subprocess

def drop_caches():
    try:
        # Sync the filesystem
        subprocess.run(['sudo', 'sync'], check=True)

        # Drop caches
        subprocess.run(['sudo', 'sh', '-c', 'echo 3 > /proc/sys/vm/drop_caches'], check=True)

        print("Caches dropped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

class E2ERunner(Runner):
    def run_benchmark_test(self, scale_factors, query, execution_mode, output_dir, log_file):
        for benchmark_item in self.args.benchmark_items.split(','):
            # 实现E2E测试的逻辑
            results = []

        for sf in scale_factors:
            duckdb_file_path = f'sf{sf}'  
            if not os.path.exists(duckdb_file_path):
                conn.execute("LOAD tpch")
                conn.execute(f"CALL dbgen(sf={sf})")
                print(f"Data generated for SF={sf} in DuckDB database at {duckdb_file_path}", file=log_file)

            with duckdb.connect(database=duckdb_file_path, read_only=True) as conn:
                
                for query_num in query:
                    query_name = f"Q{query_num}"
                    cmd = f"PRAGMA tpch({query_num});"

                    for execution_mode in execution_mode:
                        if execution_mode == "cold":
                            conn.close()
                            conn = duckdb.connect(database=duckdb_file_path, read_only=True)
                            # Simulate a cold start by reopening the connection
                            drop_caches()
                            
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

        results_csv_path = os.path.join(output_dir, 'results.csv')
        results_df.to_csv(results_csv_path, index=False)
        print(f"Running E2E benchmark for {benchmark_item} with scale factors {scale_factors}, query {query}, execution mode {execution_mode}")
        log_file.write(f"Running E2E benchmark for {benchmark_item}\n")