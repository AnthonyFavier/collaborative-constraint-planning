# CAI: Collaborative AI Agent

Human in the Loop constraint planning 
CAI 

## Overview

![plot](./rsc/overview.jpg "Overview")

Preliminary version for ONR CAI
Mix of Phase 2 and 3

## Installation

Tested on Ubuntu 20.04

#### > NTCORE: Numeric constraints compilation

Create a python3.10 environment for NTCORE before activating it and installing the relevant dependencies:
```
python3.10 -m venv ./env_NTCORE
source env_NTCORE/bin/activate
pip install anthropic wheel click sympy unified_planning==1.0.0.29.dev1 --no-cache-dir
```

[Only if using NTCORE source] Remove conflicting command line management in NTCORE, comment `@click.command()`:
```
nano NumericTCORE/bin/ntcore.py
```

Then, install the package:
```
cd NumericTCORE/
pip install .
```

#### > ENHSP: Planner 

Install the java dependencies
```
sudo apt-get install openjdk-17-jdk
```

Then compile the planner by running:
```
cd ENHSP-Public
./compile
```

#### > LLM API: Set up Claude API key

Replace `REPLACE_WITH_YOUR_KEY` in `script_generate_set_key.py`.  
Then run the python script to initialize your setup script:
```
python script_generate_set_key.py
```
You can now remove you API key from `script_generate_set_key.py`

**IMPORTANT: Never share an API key publicly, e.g., pushed on git!**

#### > GUI 

Install the gui dependencies
```
sudo apt-source env_NTCORE/bin/activate
sudo apt-get install python3.10-tk
pip install customtkinter
```

## Run CAI

Set the LLM API key by running (once per shell):
```
source set_claude_api_key.sh
```

Activate virtual environment:
```
source env_NTCORE/bin/activate
```

Run the main process:
```
python cai.py [OPTIONS] PROBLEM_NAME
```

Problems and options can be listed using `python cai.py --help`.

To add new problems, see `defs.py`.

The planning mode used (i.e. optimal, satisficing, default) can be used using the respective options `-o`, `-s`, `-d`.


*Note: to deactivate the python environment simply run: `deactivate`*

---


### Run Planner Only

You can also directly run the planner, only.
```
python planner.py [OPTIONS] PROBLEM_NAME
```

Problems and options can be listed using `python planner.py --help`

You can either use the original files corresponding to the given problem name or plan using the last compiled files using `-c`.

The planning mode used (i.e. optimal, satisficing, default) can be used using the respective options `-o`, `-s`, `-d`.

---
---

### How to use directly NTCORE 

Use `--delta_mode` (NTCORE+)? 

```
source env_NTCORE/bin/activate
python3.10 NumericTCORE/bin/ntcore.py domain.pddl problem.pddl NumericTCORE/.
deactivate
```

A mode can be specified: `--delta_mode`, `--naive_mode`, `--regression_mode`

### How to use directly ENHSP 
```
java -jar ENHSP-Public/enhsp.jar -o NumericTCORE/compiled_dom.pddl -f NumericTCORE/compiled_prob.pddl 
```