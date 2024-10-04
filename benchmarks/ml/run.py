import argparse
import os
# import mediapipe as mp
# from mediapipe.tasks import python
# from mediapipe.tasks.python.components import processors
# from mediapipe.tasks.python import vision

import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
from time import perf_counter_ns


N_ITERATIONS = 50

ALL_METRICS = ['data_type', 'num_threads', 'img_size', 'avg_inference_time(ms)']

def parse_arguments():
    parser = argparse.ArgumentParser(description='ML benchmark')
    parser.add_argument('--num_threads', type=int, default=1, help='Number of threads')
    parser.add_argument('--benchmark_items', type=str, default='img_classification', help='Benchmark items to run')
    parser.add_argument('--data_type', type=str, default='int8', help='Data type of model to run')
    parser.add_argument('--img_size', type=str, default='480x640', help='Image size')
    parser.add_argument('--metrics', type=str, help='Metrics to run')

    # parser.add_argument('--n_workers', type=int, default=1, help='Number of workers')
    # parser.add_argument('--data_size', type=int, default=32, help='Size of the data type, i.e. 32 for int32')
    # parser.add_argument('--matrix_size', type=int, default=128, help='Size N of the matrix, i.e. NxN')
    # parser.add_argument('--running_time', type=int, default=5, help='Run N seconds for each')
    
    args, _ = parser.parse_known_args()
    # print(args)
    return args

args = parse_arguments()

model_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), f'classifier{args.data_type}.tflite')

# Initialize the image classification model
base_options = core.BaseOptions(
    file_name=model_path, num_threads=args.num_threads)

classification_options = processor.ClassificationOptions()
options = vision.ImageClassifierOptions(
    base_options=base_options, classification_options=classification_options)

classifier = vision.ImageClassifier.create_from_options(options)

# for all images
IMAGE_FILENAMES = [os.path.join(os.path.dirname(os.path.realpath(__file__)), 'burger.jpg')]
IMAGE_NAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'burger.jpg')
image = cv2.imread(IMAGE_NAME)
# resize the image to the expected size
image = cv2.resize(image, tuple(map(int, args.img_size.split('x'))))
img_size = image.shape
tensor_image = vision.TensorImage.create_from_array(image)

start_time = perf_counter_ns()
for i in range(N_ITERATIONS):
    categories = classifier.classify(tensor_image)

end_time = perf_counter_ns()

running_time_ms = (end_time - start_time) / 1000000
print(f"running time for {N_ITERATIONS}: {running_time_ms} ms")

results_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../output/ML/img_classification')
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

fp.write(f"{args.data_type},{args.num_threads},{img_size[1]}x{img_size[0]},{running_time_ms / N_ITERATIONS}\n")
fp.close()
   