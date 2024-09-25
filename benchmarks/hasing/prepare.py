import subprocess
import sys

def update_openssl():
    try:
        print("Updating package list...")
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        
        print("Upgrading OpenSSL...")
        subprocess.run(['sudo', 'apt', 'upgrade', '-y', 'openssl'], check=True)
        
        print("OpenSSL update completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating OpenSSL: {e}")
        return False

def main():
    if update_openssl():
        print("Preparation completed successfully.")
    else:
        print("Preparation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()