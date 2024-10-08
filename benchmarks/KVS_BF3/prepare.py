import os
import subprocess
import sys

def install_packages():
    # Install maven and openjdk-8-jdk
    try:
        subprocess.run(["sudo", "apt", "install", "-y", "maven", "git-lfs"], check=True)
        print("Maven and Git LFS successfully installed.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during installation: {e}")
        sys.exit(1)

def git_lfs_setup():
    # Initialize Git LFS and pull LFS files
    try:
        subprocess.run(["git", "lfs", "install"], check=True)
        print("Git LFS installed.")
        subprocess.run(["git", "lfs", "pull"], check=True)
        print("Git LFS files pulled.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred with Git LFS: {e}")
        sys.exit(1)

def define_paths():
    # Get the directory where the current script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the relative paths for the .jar file and YCSB directory
    jar_path = os.path.join(script_dir, 'rocksdbjni-7.0.1-linux64.jar')
    ycsb_path = os.path.join(script_dir, 'YCSB')

    return jar_path, ycsb_path

def package_ycsb(ycsb_path):
    # Change to the YCSB directory and run the mvn command to package
    try:
        os.chdir(ycsb_path)
        subprocess.run(["mvn", "-pl", "site.ycsb:rocksdb-binding", "-am", "clean", "package"], check=True)
        print("YCSB package built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during YCSB package build: {e}")
        sys.exit(1)

def main():
    # Step 1: Install necessary packages
    install_packages()

    # Step 2: Setup Git LFS and pull large files
    git_lfs_setup()

    # Step 3: Define paths for the jar file and YCSB directory
    jar_path, ycsb_path = define_paths()

    # Step 4: Build YCSB rocksdb-binding
    package_ycsb(ycsb_path)

if __name__ == "__main__":
    main()
