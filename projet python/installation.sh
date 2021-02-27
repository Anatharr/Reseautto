#!/bin/bash

# Create virtual environment in .venv folder
echo "Creating virtual environment in .venv folder"
python3 -m venv .venv 

# Activate the venv
echo "Sourcing virtual environment"
source .venv/bin/activate 2> /dev/null

# Install all required packages for the project
echo "Installation of requirements.txt"
pip install -r requirements.txt 2> /dev/null

# Set-up pre-commit hooks
if [ "$1" = "--production" ]; 
then
    echo "Finished production building"
else
    echo "Pre-commit installation..."
    pre-commit install
fi
