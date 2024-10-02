# import os
# import subprocess
# import sys

# def run_command(command, env=None):
#     """Run a shell command and handle errors."""
#     try:
#         result = subprocess.run(command, shell=True, check=True, env=env, stdout=sys.stdout, stderr=sys.stderr)
#         print(result.stdout.decode())
#     except subprocess.CalledProcessError as e:
#         print(f"Error occurred while running command: {command}")
#         print(e.stderr.decode())
#         sys.exit(1)
#     print(f"Successfully running command {command}")

# def install_dependencies():
#     """Install required dependencies: Maven and OpenJDK 8."""
#     print("Installing Maven and OpenJDK 8...")
#     run_command("sudo apt update")
#     run_command("sudo apt install -y maven openjdk-8-jdk")

# def set_java_home():
#     """Set the JAVA_HOME environment variable to OpenJDK 8."""
#     java_home = "/usr/lib/jvm/java-8-openjdk-arm64"
#     print(f"Setting JAVA_HOME environment variable to {java_home}...")
#     os.environ['JAVA_HOME'] = java_home
#     print(f"JAVA_HOME set to {os.environ['JAVA_HOME']}")

# def clone_rocksdb():
#     """Clone the RocksDB repository and checkout version 7.0.1."""
#     if not os.path.exists('rocksdb'):
#         print("Cloning RocksDB repository...")
#         run_command("git clone https://github.com/facebook/rocksdb.git")
#     else:
#         print("RocksDB repository already exists, skipping clone step.")
    
#     os.chdir('rocksdb')
    
#     print("Checking out RocksDB version 7.0.1...")
#     run_command("git checkout v7.0.1")

# def build_rocksdb():
#     """Build RocksDB with Java bindings."""
#     print("Make clean all the prvious target and file")
#     run_command("make clean")
#     print("Building RocksDB with Java bindings...")
#     run_command("PORTABLE=1 DEBUG_LEVEL=0 make -j8 rocksdbjava")
#     print("RocksDB Java bindings build completed!")

# def main():
#     """Main function to run all steps."""
#     install_dependencies()
#     set_java_home()
#     clone_rocksdb()
#     build_rocksdb()

# if __name__ == '__main__':
#     main()
