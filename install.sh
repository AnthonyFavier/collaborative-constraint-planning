#!/bin/bash

echo "[CAI installation Script]"

echo "[1/4] Installing pip requirements"
pip install --upgrade pip -r requirements.txt --no-cache-dir

echo "[2/4] Manual patching"
python3.10 patches.py

echo "[3/4] Installing NTCORE"
cd NumericTCORE/
pip install .
cd ..

echo "[4/4] Compiling ENHSP planner"
cd ENHSP-Public
./compile
cd ..

echo "[Done!]"
