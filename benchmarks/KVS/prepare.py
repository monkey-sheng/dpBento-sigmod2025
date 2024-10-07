import os
import subprocess
import sys

def install_packages():
    # Install maven and openjdk-8-jdk
    try:
        subprocess.run(["sudo", "apt", "install", "-y", "maven", "openjdk-8-jdk","git-lfs"], check=True)
        print("Maven successfully installed.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during installation: {e}")
        sys.exit(1)

def define_paths():
    # Get the directory where the current script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Define the relative paths for the .jar file and YCSB directory
    jar_path = os.path.join(script_dir, 'rocksdbjni-7.0.1-linux64.jar')
    ycsb_path = os.path.join(script_dir, 'YCSB')
    return jar_path, ycsb_path

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

def install_rocksdb_jar(jar_path):
    # Run the maven install:install-file command to install the rocksdbjni jar
    try:
        subprocess.run([
            "mvn", "install:install-file", 
            f"-Dfile={jar_path}",
            "-DgroupId=org.rocksdb",
            "-DartifactId=rocksdbjni",
            "-Dversion=7.0.1",
            "-Dpackaging=jar"
        ], check=True)
        print("rocksdbjni JAR file installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during jar installation: {e}")
        sys.exit(1)

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
    git_lfs_setup()
    # Step 2: Define paths for the jar file and YCSB directory
    jar_path, ycsb_path = define_paths()

    # Step 3: Install rocksdbjni JAR file using Maven
    install_rocksdb_jar(jar_path)
    # Step 4: Build YCSB rocksdb-binding
    package_ycsb(ycsb_path)
if __name__ == "__main__":
    main()
