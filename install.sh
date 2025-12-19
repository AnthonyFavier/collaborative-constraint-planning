#!/bin/bash

echo "[CAI installation Script]"

echo "[1/5 Virtual Env setup]"
python3.10 -m venv env_cai
source env_cai/bin/activate

echo "[2/5] Installing pip requirements"
pip install --upgrade pip -r requirements.txt --no-cache-dir

echo "[3/5] Manual patching"
python3.10 patches.py 

echo "[4/5] Installing NTCORE"
cd NumericTCORE/
pip install .
cd ..

echo "[5/5] Compiling ENHSP planner"
cd ENHSP-Public
./compile
cd ..

echo "[Done!]"
