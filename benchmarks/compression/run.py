import argparse
import subprocess
import sys
import json
import os
from datetime import datetime
import io
import subprocess
import re
import csv
import zlib_ng
from zlib_ng import gzip_ng_threaded, gzip_ng
import zlib
from time import perf_counter_ns

VALID_ITEMS = ['default', 'simd', 'threading', 'doca']

def write_results(type, bs, threads, throughput_mbps):
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'output', 'compression')
    os.makedirs(output_dir, exist_ok=True)
    output_filename = "results.csv"
    result_file = os.path.join(output_dir, output_filename)
    if not os.path.exists(result_file):
        # write the columns header
        fp = open(result_file, 'w')
        writer = csv.writer(fp)
        writer.writerow(["type", "block size", "threads", "throughput (MB/s)"])
    else:
        fp = open(result_file, 'a')
        writer = csv.writer(fp)
        

    # Write the results
    writer.writerow([type, str(bs / 1024) + 'K', threads, throughput_mbps])
    fp.close()

def default_compress(block_size, threads):
    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)), '128.txt')
    txt = open(fname, 'rb').read()
    start = perf_counter_ns()
    buf = zlib.compress(txt)
    end = perf_counter_ns()
    elapsed_ms = (end - start) / 1_000_000
    throughput = 128 * 1024*1024 / elapsed_ms
    print(f"Default throughput: {throughput} MB/s")
    write_results('default', block_size, threads, throughput)

def simd_compress(block_size, threads):
    start = perf_counter_ns()
    fp = gzip_ng_threaded.open('/home/jasonhu/128.gz', threads=0, block_size=block_size)
    r=fp.read()
    end = perf_counter_ns()
    elapsed_ms = (end - start) / 1_000_000
    throughput = 128 * 1024*1024 / elapsed_ms
    print(f"SIMD throughput: {throughput} MB/s")
    write_results('simd', block_size, threads, throughput)

def threading_compress(block_size, threads):
    buf = io.BytesIO()
    fname = os.path.join(os.path.dirname(os.path.realpath(__file__)), '128.txt')
    txt = open(fname, 'rb').read()
    fp2 = gzip_ng_threaded.open(buf, 'w', threads=threads, block_size=block_size)
    start = perf_counter_ns()
    fp2.write(txt)
    end = perf_counter_ns()
    elapsed_ms = (end - start) / 1_000_000
    throughput = 128 * 1024*1024 / elapsed_ms
    print(f"Threaded throughput: {throughput} MB/s")
    write_results('threading (max)', block_size, threads, throughput)

def doca_compress(data_size: str):
    root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
    this_dir = os.path.dirname(os.path.realpath(__file__))
    build_dir = os.path.join(this_dir, 'build')
    exec_name = os.path.join(build_dir, 'doca_compress')
    output_dir = os.path.join(root_dir, 'output', 'compress')
    result_file = os.path.join(output_dir, 'doca_result.csv')
    fname = os.path.join(this_dir, f'{data_size}.deflate')

    os.makedirs(output_dir, exist_ok=True)
    output = subprocess.run([exec_name, '-p', "03:00.0", '-m', 'compress', '-f', fname, '-o', 'rub.out'],
                            cwd=build_dir, capture_output=True, text=True).stdout
    # total = 0.05553569
    found = re.findall(r"total = (.+)", output)
    completion_time = float(found[0])
    throughput_mbps = float(data_size) / completion_time / 1024 / 1024
    print(f"Throughput: {throughput_mbps} MB/s")
    write_results('doca', data_size, 0, throughput_mbps)

def main():
    parser = argparse.ArgumentParser(description='Run compression benchmark')
    parser.add_argument('--benchmark_items', help='Comma-separated list of benchmark items')
    parser.add_argument('--block_size', type=int, default=1, help='Block size in KB')
    parser.add_argument('data_size', type=str, default=4, help='Data size')
    parser.add_argument('--threads', type=int, default=-1, help='Number of threads')
    args, _ = parser.parse_known_args()

    items = args.benchmark_items.split(',')
    block_size = args.block_size * 1024
    for item in items:
        if item == 'default':
            default_compress(block_size, args.threads)
        elif item == 'simd':
            simd_compress(block_size, args.threads)
        elif item == 'threading':
            threading_compress(block_size, args.threads)
        elif item == 'doca':
            doca_compress(args.data_size)
        else:
            print(f"Invalid item: {item}")

if __name__ == '__main__':  
    main()