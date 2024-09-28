#!/usr/bin/env python3
import subprocess
import argparse
import logging
import sys
import os

def uninstall_packages(packages):
    """Uninstall packages using pip."""
    pip_executable = 'pip3'
    for package in packages:
        try:
            subprocess.run(['sudo',pip_executable, 'uninstall', '-y', package])
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to uninstall {package}: {e}")

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Define the packages to uninstall
    packages_to_uninstall = ['pandas', 'matplotlib', 'numpy', 'duckdb']

    # Uninstall the packages
    uninstall_packages(packages_to_uninstall)

if __name__ == '__main__':
    main()