import argparse
import os
import subprocess


def install_dependencies():
    subprocess.run(r"sudo apt install ffmpeg libsm6 libxext6  -y;\
                   pip3 install tflite-support==0.4.3 opencv-python", shell=True, check=True)

if __name__ == '__main__':
    install_dependencies()
    print(f"Installed deps for ML benchmarks")