import duckdb
import pandas as pd
import time

# Define scale factors and corresponding DuckDB file paths
scale_factors = [1, 3, 10]
duckdb_file_paths = {
    1: 'sf1',
    3: 'sf3',
    10: 'sf10'
}

# Function to run queries and record runtimes
def run_queries_and_record_times(scale_factor, duckdb_file_path, output_file):
    # Create an empty list to store results
    results = []

    # Connect to the corresponding DuckDB database
    with duckdb.connect(database=duckdb_file_path, read_only=True) as conn:
        # Loop through each TPC-H query (Q1 to Q22)
        for query_number in range(1, 23):
            query_name = f"Q{query_number}"
            avg_query_runtime = 0.0
            # Execute the query three times and calculate average runtime
            for _ in range(3):
                # Timing query execution
                start_time = time.time()
                try:
                    # Execute the PRAGMA tpch command
                    conn.execute(f"PRAGMA tpch({query_number});")
                except Exception as e:
                    print(f"Error executing query {query_name} for SF={scale_factor}: {str(e)}")
                    continue
                end_time = time.time()
                run_time = end_time - start_time
                avg_query_runtime += run_time / 3.0  # Accumulate average runtime

            # Append the result for this query
            results.append({
                'Query': query_name,
                'Run Time (s)': avg_query_runtime
            })

    # Convert list of dictionaries to DataFrame
    results_df = pd.DataFrame(results)

    # Save results to a CSV file
    results_df.to_csv(output_file, index=False)

# Run queries for each scale factor and save results
for sf in scale_factors:
    duckdb_file_path = duckdb_file_paths[sf]
    output_file = f"{sf}sf.csv"
    run_queries_and_record_times(sf, duckdb_file_path, output_file)
    print(f"Results for SF={sf} saved to {output_file}")
