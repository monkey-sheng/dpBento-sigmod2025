import argparse
import os
import subprocess


def install_dependencies():
    subprocess.run("sudo apt install ffmpeg libsm6 libxext6  -y; pip3 install mediapipe", shell=True, check=True)

if __name__ == '__main__':
    install_dependencies()
    print(f"Installed deps for ML benchmarks")