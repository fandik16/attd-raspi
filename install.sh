#!/bin/bash

# Membuat virtual environment dengan akses system site-packages
python3 -m venv venv --system-site-packages

# Aktivasi virtual environment
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

echo "Install Complete."
