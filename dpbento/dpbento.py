'''
This is the main runner for the benchmark framework, more or less the entry point.
It will automatically handle the loading and some boilerplate setup process for the bento boxes and benchmarks.
'''

import argparse as ap


def final_plot():
    '''
    This plots the final results of all benchmarks across all perf aspects
    should be called after all benchmarks have been run.
    // TODO: think about what goes into the plots
    '''
    pass

if __name__ == '__main__':
    parser = ap.ArgumentParser(prog='dpbento', description='Run the dpbento benchmarking framework', add_help=True)

    parser.add_argument('--extras_dir', type=str, help='The directory to load extra user benchmarks from,\
                        which should contain dpbento(s), where each contain module(s), which are the benchmarks.',
                        required=False)    

    args = parser.parse_args()

    # Load the user benchmarks
    if args.dir:
        # TODO: load the user supplied benchmarks as modules
        pass