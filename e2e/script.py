import duckdb
import pandas as pd
import time
import paramiko

# Define scale factors and corresponding DuckDB file paths
scale_factors = [1, 3, 10]
duckdb_file_paths = {
    1: 'sf1',
    3: 'sf3',
    10: 'sf10'
}

# Create an empty list to store results
results_bf3 = []
results_bf2 = []

# Function to run TPC-H queries and collect runtimes
def run_tpch_queries(conn, scale_factor):
    query_runtimes = []
    for query_number in range(1, 23):
        pragma_query = f"PRAGMA tpch({query_number});"
        start_time = time.time()
        try:
            conn.execute(pragma_query)
        except Exception as e:
            print(f"Error executing query Q{query_number} for SF={scale_factor}: {str(e)}")
            continue
        end_time = time.time()
        run_time = end_time - start_time
        query_runtimes.append(run_time)
    return query_runtimes

# Run benchmarks on host
for sf in scale_factors:
    duckdb_file_path = duckdb_file_paths[sf]
    with duckdb.connect(database=duckdb_file_path, read_only=True) as conn:
        runtimes = run_tpch_queries(conn, sf)
        results_host.extend([{'Scale Factor': sf, 'Query': f'Q{q+1}', 'Run Time (s)': rt} for q, rt in enumerate(runtimes)])

# Save host results to CSV
host_results_df = pd.DataFrame(results_host)
host_results_df.to_csv('host_results.csv', index=False)

# Run benchmarks on BF2
bf2_hostname = 'bf2_hostname'
bf2_username = 'bf2_username'
bf2_password = 'bf2_password'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(bf2_hostname, username=bf2_username, password=bf2_password)

for sf in scale_factors:
    duckdb_file_path = duckdb_file_paths[sf]
    sftp = ssh.open_sftp()
    sftp.put(duckdb_file_path, f'/tmp/{duckdb_file_path}')
    sftp.close()
    
    stdin, stdout, stderr = ssh.exec_command(f'python3 -c "\
import duckdb;\
import pandas as pd;\
import time;\
with duckdb.connect(database=\'/tmp/{duckdb_file_path}\', read_only=True) as conn:\
    query_runtimes = [];\
    for query_number in range(1, 23):\
        pragma_query = f\'PRAGMA tpch({query_number});\';\
        start_time = time.time();\
        try:\
            conn.execute(pragma_query);\
        except Exception as e:\
            print(f\'Error executing query Q{{query_number}} for SF={{sf}}: {{str(e)}}\');\
            continue;\
        end_time = time.time();\
        run_time = end_time - start_time;\
        query_runtimes.append(run_time);\
    df = pd.DataFrame([{{\'Query\': f\'Q{{q+1}}\', \'Run Time (s)\': rt}} for q, rt in enumerate(query_runtimes)]);\
    df.to_csv(\'/tmp/bf2_results_sf{sf}.csv\', index=False);\
    "')
    
    stdout.channel.recv_exit_status()
    sftp = ssh.open_sftp()
    sftp.get(f'/tmp/bf2_results_sf{sf}.csv', f'bf2_results_sf{sf}.csv')
    sftp.close()

ssh.close()

# Load BF2 results from CSV files
for sf in scale_factors:
    bf2_results_df = pd.read_csv(f'dpu_results_sf{sf}.csv')
    bf2_results_df['Scale Factor'] = sf
    results_bf2.append(bf2_results_df)

dpu_results_df = pd.concat(results_bf2, ignore_index=True)
dpu_results_df.to_csv('dpu_results.csv', index=False)

print("Benchmarking completed and results saved.")

# Plotting function
def plot_results(host_file, dpu_file):
    host_data = pd.read_csv(host_file)
    bf2_data = pd.read_csv(bf2_file)

    # Merge dataframes on Query
    merged_data = host_data.merge(bf2_data, on=['Scale Factor', 'Query'], suffixes=('_host', '_dpu'))

    # Create plot
    fig, ax = plt.subplots(figsize=(14, 7))
    
    for sf in scale_factors:
        sf_data = merged_data[merged_data['Scale Factor'] == sf]
        index = range(len(sf_data))
        
        bar_width = 0.35
        r1 = index
        r2 = [x + bar_width for x in r1]
        
        ax.bar(r1, sf_data['Run Time (s)_host'], color='b', width=bar_width, edgecolor='grey', label=f'BF3 SF={sf}')
        ax.bar(r2, sf_data['Run Time (s)_bf2'], color='r', width=bar_width, edgecolor='grey', label=f'BF2 SF={sf}')

    ax.set_xlabel('Query')
    ax.set_ylabel('Run Time (s)')
    ax.set_title('TPC-H Query Run Time Comparison: BF3 vs BF2')
    ax.set_xticks([r + bar_width/2 for r in range(len(merged_data['Query']))])
    ax.set_xticklabels(merged_data['Query'], rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.savefig('comparison_plot.png')
    plt.show()

# Plot results
plot_results('host_results.csv', 'bf2_results.csv')

