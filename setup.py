import subprocess
import sys

def install_requirements(requirements_file='requirements.txt'):
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print(f"Successfully installed packages from {requirements_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages from {requirements_file}")
        print(e)

if __name__ == '__main__':
    install_requirements()
