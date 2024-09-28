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

class RDBRunner(Runner):
    def run_benchmark_test(self, scale_factors, query, execution_mode, output_dir):
        for benchmark_item in self.args.benchmark_items.split(','):
            results = []
        sf = scale_factors
        duckdb_file_path = f'sf{sf}'  
        if not os.path.exists(duckdb_file_path):
            duckdb_file_path = f'sf{sf}'
            with duckdb.connect(database=duckdb_file_path, read_only=False) as conn:
                conn.execute("LOAD tpch")
                conn.execute(f"CALL dbgen(sf={sf})")
                print(f"Data generated for SF={sf} in DuckDB database at {duckdb_file_path}", file=log_file)

        with duckdb.connect(database=duckdb_file_path, read_only=True) as conn:
            
            query_name = f"Q{int(query)}"
            cmd = f"PRAGMA tpch({query});"
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

        results_csv_path = os.path.join(output_dir, 'trivial.csv')
        # Check if the file already exists and append if it does
        if os.path.exists(results_csv_path):
            existing_df = pd.read_csv(results_csv_path)
            results_df = pd.concat([existing_df, results_df], ignore_index=True)
        results_df.to_csv(results_csv_path, index=False)
        print(f"Running RDB benchmark for {benchmark_item} with scale factors {scale_factors}, query {query}, execution mode {execution_mode}")