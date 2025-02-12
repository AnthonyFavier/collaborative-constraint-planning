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

## Run main

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
python main.py
```

*Note: to deactivate the python environment simply run:*
```
deactivate
```

---
---

## Run independently


### 1. Encode User strategy into PDDL3 constraints with LLM

### 2. Compile the updated problem with NTCORE

Use `--delta_mode` (NTCORE+)? 

```
source env_NTCORE/bin/activate
python3.10 NumericTCORE/bin/ntcore.py domain.pddl problem.pddl NumericTCORE/.
deactivate
```

### 3. Plan using ENHSP
```
java -jar ENHSP-Public/enhsp.jar -o NumericTCORE/compiled_dom.pddl -f NumericTCORE/compiled_prob.pddl 
```