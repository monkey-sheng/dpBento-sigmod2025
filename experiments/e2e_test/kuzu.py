import json
import os
import query

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

def run_benchmark(scale_factor, query_numbers, execution_mode):
    # Connect to the appropriate database based on the scale factor and execution mode
    db_path = f'sf{scale_factor}_{execution_mode}.db'
    conn = KuzudbConnection(db_path)
    
    query_runtimes = []
    for query_number in query_numbers:
        query_name = f"Q{query_number}"
        run_times = [query.run_query(conn, query_number) for _ in range(3)]
        avg_run_time = sum(run_times) / len(run_times)
        query_runtimes.append({'Query': query_name, 'Run Time (s)': avg_run_time})
    
    conn.close()
    return query_runtimes

def main():
    config_file = 'E:/Paper/DPU-bench/configs_user/e2e_testcustomize_test.json'
    config = load_config(config_file)
    
    benchmark_name = config['benchmark_name']
    test_parameters = config['test_parameters']
    output_folder = config['output_folder']
    
    scale_factors = test_parameters['scale_factors']
    query_numbers = test_parameters['query_numbers']
    execution_modes = test_parameters['executionMode']
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for sf in scale_factors:
        for mode in execution_modes:
            results = run_benchmark(sf, query_numbers, mode)
            df = pd.DataFrame(results)
            df.to_csv(os.path.join(output_folder, f'{sf}sf_{mode}.csv'), index=False)

if __name__ == "__main__":
    main()
