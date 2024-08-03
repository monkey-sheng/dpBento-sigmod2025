import subprocess
import os

def prepare():
    # call the external clean.sh bash script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.call(['bash', os.path.join(current_dir, 'setup.sh')])

if __name__ == '__main__':
    prepare()