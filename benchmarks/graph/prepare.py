import subprocess
import os
import logging

def run_command(command, check=True, shell=False):
    """Run a shell command."""
    logging.info(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=check, shell=shell)


#if __name__ == '__main__':
def main():
    logging.basicConfig(level=logging.INFO)

    # Get the directory of the prepare.py script
    benchmark_dir = os.path.dirname(os.path.abspath(__file__))
    #print(benchmark_dir)
    logging.info(f"benchmark directory: {benchmark_dir}")

    run_command(['pip', 'install', "--user", "kuzu"]) # feels sus, but Chihan said to do this for now
    run_command(['sudo', 'apt', 'update'])
    run_command(['sudo', 'apt', 'install', '-y', 'zstd', 'wget', 'unzip'])
    
    logging.info("Setup complete")

if __name__ == "__main__":
    main()
