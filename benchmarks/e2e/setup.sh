#!/bin/bash

# Check if benchmark name argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <benchmark_name>"
  exit 1
fi

benchmark_name=$1
benchmark_dir=$(pwd)/experiments/$benchmark_name

# Create benchmark directory if it does not exist
mkdir -p $benchmark_dir

# Navigate to benchmark directory
cd $benchmark_dir

# Update package list
sudo apt update

# Install python3-pip
sudo apt install -y python3-pip

# Create virtual environment
python3 -m venv env

# Activate the virtual environment
source env/bin/activate

# Upgrade pip in the virtual environment
pip install --upgrade pip

# Install packages from requirements.txt
pip install -r requirements.txt


echo "Setup complete. To activate the virtual environment, use: source env/bin/activate"