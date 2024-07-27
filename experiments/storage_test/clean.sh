#!/bin/bash

# Deactivate the virtual environment if it is active
deactivate 2>/dev/null

# Remove the virtual environment directory within the storage_test folder
rm -rf $(dirname $0)/env

# Uninstall fio
sudo apt remove -y fio

# Uninstall python3-pip
sudo apt remove -y python3-pip

# Clean up residual configuration files
sudo apt purge -y fio python3-pip

# Remove any unused dependencies
sudo apt autoremove -y

# Clean up package cache
sudo apt clean

echo "Cleanup complete. All installed packages and virtual environment have been removed."
