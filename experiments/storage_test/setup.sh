#!/bin/bash

# Update package list
sudo apt update

# Install fio
sudo apt install -y fio

# Install python3-pip
sudo apt install -y python3-pip

# Create virtual environment
python3 -m venv myenv

# Activate the virtual environment
source myenv/bin/activate

# Upgrade pip in the virtual environment
pip install --upgrade pip

# Install packages from requirements.txt
pip install -r requirements.txt

# Deactivate the virtual environment
deactivate

echo "Setup complete. To activate the virtual environment, use: source myenv/bin/activate"
