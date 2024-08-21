import glob
import json
import os
from run import VALID_BENCHMARK_ITEMS

import argparse
import pandas as pd

# report.py shall aggregate all the intermediate results generated by the benchmark items
# (which may have been run multiple times each) and generate an aggregate (csv) file

def parse_arguments():
    parser = argparse.ArgumentParser(description='compute benchmark')
    parser.add_argument('--metrics', type=str, default='', help='metrics to collect in the generated file')
    
    args, _ = parser.parse_known_args()
    print(args)
    return args

def gather_results() -> pd.DataFrame:
    # Get the directory path of the current file
    dir = os.path.dirname(os.path.realpath(__file__))
    
    all_dfs = []
    for item in VALID_BENCHMARK_ITEMS:
        # Use glob to find all .csv files in the directory
        result_paths = glob.glob(os.path.join(dir, item, '*.csv'))
        
        for result_csv in result_paths:
            df = pd.read_csv(result_csv)
            df['benchmark_item'] = item
            print(df)
            all_dfs.append(df)

        # merge all the dataframes
    return pd.concat(all_dfs)

if __name__ == '__main__':
    args = parse_arguments()
    concat_df = gather_results()
    print(concat_df)
    if args.metrics:
        # keep columns of dfs that are in the metrics list
        # TODO: need to keep the other useful columns, i.e. benchmark_item, too
        metrics = json.loads(args.metrics)
        assert(isinstance(metrics, list))
        metrics.append('benchmark_item')
        print('metrics to keep:', metrics)
        concat_df = concat_df[metrics]

    print('after keeping only the specified metrics:')
    print(concat_df)

    # write the aggregated results to a csv file
    concat_df.to_csv(os.path.join(os.path.dirname(__file__), 'output.csv'), index=False)
    