#!/bin/bash
echo "Starting startup script..."

# Print current directory and contents for debugging
pwd
ls -la

# Create and activate virtual environment
echo "Creating virtual environment..."
python -m venv antenv
source antenv/bin/activate

# Install requirements
echo "Installing requirements..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Print installed packages for debugging
pip list

# Start Streamlit
echo "Starting Streamlit..."
python -m streamlit run Home.py --server.port 8000 --server.address 0.0.0.0