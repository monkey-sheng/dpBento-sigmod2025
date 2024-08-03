import subprocess
import os

def clean():
    # call the external clean.sh bash script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.call(['bash', os.path.join(current_dir, 'clean.sh')])

if __name__ == '__main__':
    clean()