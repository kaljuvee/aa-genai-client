#!/bin/bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run Home.py --server.port 8000 --server.address 0.0.0.0