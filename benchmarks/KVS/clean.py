import os
import shutil
import subprocess
import sys

def uninstall_maven():
    # Uninstall maven using apt
    
    try:
        subprocess.run(["sudo", "apt", "remove", "--purge", "-y", "maven"], check=True)
        print("Maven has been successfully uninstalled.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during Maven uninstallation: {e}")
        sys.exit(1)

def delete_output_directory(output_dir):
    # Check if the output directory exists and delete it
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir)
            print(f"Output directory '{output_dir}' and all its contents have been deleted.")
        except Exception as e:
            print(f"Error occurred while deleting the output directory: {e}")
            sys.exit(1)
    else:
        print(f"The output directory '{output_dir}' does not exist.")

def main():
    # Define the output directory path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'output')

    # Step 1: Uninstall Maven
    uninstall_maven()

    # Step 2: Delete the output directory and its contents
    delete_output_directory(output_dir)

if __name__ == "__main__":
    main()
