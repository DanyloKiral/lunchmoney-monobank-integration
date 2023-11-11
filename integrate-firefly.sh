#!/bin/sh
echo "$(date) - Start integration monobank->firefly."
cd "${0%/*}"
export PYTHONDONTWRITEBYTECODE=1
apk add --no-cache python3 py3-pip
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "$(date) - Installed python, configured venv. Running script."
python firefly-integrator.py --config $1 --credentials $2
deactivate
echo "$(date) - Monobank->firefly finished"