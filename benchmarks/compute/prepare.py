import argparse
import os
import subprocess


def install_dependencies():
    print('installing stress-ng...')
    subprocess.run("sudo apt install stress-ng python3-venv -y", shell=True, check=True)
    
    # get dir of current file
    # env_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'compute_env')
    # print(env_dir)
    # # create and use a virtual environment
    # print('creating virtual environment...')
    # subprocess.run(f"python3 -m venv {env_dir}", shell=True, check=True)
    # subprocess.run(f"source {env_dir}/bin/activate;\
    #                pip install pandas", shell=True, check=True, executable='/bin/bash')

if __name__ == '__main__':
    install_dependencies()
    print(f"Installed deps for compute benchmarks")