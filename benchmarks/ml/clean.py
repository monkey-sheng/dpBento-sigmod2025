import os


results_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../output/ML')
result_file = os.path.join(results_dir, "result.csv")

# remove the file if it exists
if os.path.exists(result_file):
    os.remove(result_file)