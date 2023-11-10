#!/bin/bash
export PYTHONDONTWRITEBYTECODE=1
sudo apt-get update
sudo apt-get install python3 python3-pip python-is-python3 python3.10-venv -y
alias python=python3
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt