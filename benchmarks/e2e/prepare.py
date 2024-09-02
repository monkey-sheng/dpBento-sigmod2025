# import os
# import subprocess
# import logging
# import venv
import sys
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if base_dir not in sys.path:
    sys.path.append(base_dir)

from packages.e2e_parser import E2EParser
from packages.e2e_runner import E2ERunner

# def run_command(command, check=True, shell=False):
#     """Run a shell command."""
#     logging.info(f"Running command: {' '.join(command)}")
#     subprocess.run(command, check=check, shell=shell)

# def install_packages(env_path, requirements_path):
#     """Install packages in the virtual environment."""
#     pip_executable = os.path.join(env_path, 'bin', 'pip')
#     run_command([pip_executable, 'install', '--upgrade', 'pip'])
#     if os.path.exists(requirements_path):
#         run_command([pip_executable, 'install', '-r', requirements_path])
#     else:
#         logging.warning(f"requirements.txt not found at {requirements_path}")

# def main():
#     logging.basicConfig(level=logging.INFO)

#     # Get the directory of the prepare.py script
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     logging.info(f"Script directory: {script_dir}")

#     # Set the benchmark directory to the script directory
#     benchmark_dir = script_dir

#     # Update package list
#     run_command(['sudo', 'apt', 'update'])

#     # Install python3-pip
#     run_command(['sudo', 'apt', 'install', '-y', 'python3-pip'])

#     # Create virtual environment
#     env_path = os.path.join(benchmark_dir, 'env')
#     venv.create(env_path, with_pip=True)
#     logging.info("Created virtual environment.")

#     # Install packages from requirements.txt in the virtual environment
#     requirements_path = os.path.join(benchmark_dir, 'requirements.txt')
#     install_packages(env_path, requirements_path)

#     logging.info("Setup complete. To activate the virtual environment, use: source env/bin/activate")

# if __name__ == "__main__":
#     main()
