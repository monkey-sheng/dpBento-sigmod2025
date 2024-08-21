import os
import subprocess
import logging
import venv

def run_command(command, check=True, shell=False):
    """Run a shell command."""
    logging.info(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=check, shell=shell)

def install_packages(env_path):
    """Install packages in the virtual environment."""
    pip_executable = os.path.join(env_path, 'bin', 'pip')
    run_command([pip_executable, 'install', '--upgrade', 'pip'])

    # Install required packages
    required_packages = ['matplotlib', 'numpy', 'pandas']
    for package in required_packages:
        run_command([pip_executable, 'install', package])

def main():
    logging.basicConfig(level=logging.INFO)

    run_command(['sudo', 'apt', 'install', "python3.10-venv"])
    
    # Get the directory of the prepare.py script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logging.info(f"Script directory: {script_dir}")

    # Set the benchmark directory to the script directory
    benchmark_dir = script_dir

    # Update package list
    run_command(['sudo', 'apt', 'update'])

    # Install fio
    run_command(['sudo', 'apt', 'install', '-y', 'fio'])

    # Install python3-pip
    run_command(['sudo', 'apt', 'install', '-y', 'python3-pip'])

    # Create virtual environment
    env_path = os.path.join(benchmark_dir, 'env')
    venv.create(env_path, with_pip=True)
    logging.info("Created virtual environment.")

    # Install packages directly in the virtual environment
    install_packages(env_path)

    logging.info("Setup complete.")
    activate_command = f"source {env_path}/bin/activate"
    logging.info(f"To activate the virtual environment, run: {activate_command}")

    # Block the script to allow the user to manually activate the environment
    input(f"Please run the following command in this terminal to activate the virtual environment and then press Enter here to continue:\n\n{activate_command}\n\n")

    # Continue with the rest of the tasks after virtual environment activation
    logging.info("Virtual environment should now be active. Continuing with the rest of the script...")


if __name__ == "__main__":
    main()
