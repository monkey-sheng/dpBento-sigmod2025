import os
import shutil
import subprocess

def run_command(command, check=True, shell=False):
    """Run a shell command."""
    print(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=check, shell=shell)

def remove_directory(path):
    """Remove the specified directory if it exists."""
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Removed directory: {path}")

def remove_package(package_name):
    """Remove the specified package using apt."""
    run_command(['sudo', 'apt', 'remove', '-y', package_name])
    
def purge_package(package_name):
    """Purge the specified package using apt."""
    run_command(['sudo', 'apt', 'purge', '-y', package_name])
    
def clean_package_cache():
    """Clean up package cache."""
    run_command(['sudo', 'apt', 'clean'])

def main():
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(curr_dir, 'output')
    remove_directory(output_path)
    remove_package('paramiko')
    purge_package('paramiko')
    clean_package_cache()
    print("Output directory deleted and package removed.")
    
if __name__ == "__main__":
    main()
