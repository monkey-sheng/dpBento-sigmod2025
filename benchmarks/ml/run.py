import argparse
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.components import processors
from mediapipe.tasks.python import vision
from time import perf_counter_ns


N_ITERATIONS = 50

ALL_METRICS = ['data_type', 'avg_inference_time(ms)']

def parse_arguments():
    parser = argparse.ArgumentParser(description='ML benchmark')
    parser.add_argument('--benchmark_items', type=str, default='img_classification', help='Benchmark items to run')
    parser.add_argument('--data_type', type=str, default='int8', help='Data type of model to run')

    # parser.add_argument('--n_workers', type=int, default=1, help='Number of workers')
    # parser.add_argument('--data_size', type=int, default=32, help='Size of the data type, i.e. 32 for int32')
    # parser.add_argument('--matrix_size', type=int, default=128, help='Size N of the matrix, i.e. NxN')
    # parser.add_argument('--running_time', type=int, default=5, help='Run N seconds for each')
    
    args, _ = parser.parse_known_args()
    # print(args)
    return args
args = parse_arguments()
base_options = python.BaseOptions(model_asset_path=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                f'classifier{args.data_type}.tflite'))
options = vision.ImageClassifierOptions(
    base_options=base_options)
classifier = vision.ImageClassifier.create_from_options(options)

images = []
predictions = []

# for all images in the sub current file's directory
IMAGE_FILENAMES = [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'burger.jpg')]

start_time = perf_counter_ns()
for i in range(N_ITERATIONS):
    for image_name in IMAGE_FILENAMES:
        image = mp.Image.create_from_file(image_name)

        classification_result = classifier.classify(image)

end_time = perf_counter_ns()

running_time_ms = (end_time - start_time) / 1000000
print(f"running time for {N_ITERATIONS}: {running_time_ms} ms")

results_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../output/ML')
os.makedirs(results_dir, exist_ok=True)

# write the results to a file
result_file = os.path.join(results_dir, "result.csv")
# print("result_file path: ", result_file)
if not os.path.exists(result_file):
    # write the columns header
    fp = open(result_file, 'w')
    fp.write(','.join(ALL_METRICS) + '\n')
else:
    fp = open(result_file, 'a')

fp.write(f"{args.data_type},{running_time_ms / N_ITERATIONS}\n")
fp.close()
   