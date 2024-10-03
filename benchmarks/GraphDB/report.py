import os
import csv
def main():
    benchmark_dir = os.path.dirname(os.path.abspath(__file__))
    with open(benchmark_dir + "/results/results.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=chr(9))
        with open(benchmark_dir + "/output.csv", "w") as output:
            output.write("num_threads,SF,query,time(seconds)\n")
            for row in reader:
                output.write(row["num_threads"]+","+row["SF"] +"," + row["query"] + "," + row["time(seconds)"] + "\n") 

if __name__ == "__main__":
    main()
