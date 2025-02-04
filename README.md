# CAI: Collaborative AI Agent

Human in the Loop constraint planning 
CAI 

## Overview

<!-- ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true) -->


Preliminary version for ONR CAI
Mix of Phase 2 and 3

## Installation

### NTCORE: Numeric constraints compilation

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

Note: to deactivate the python environment simply run:
```
deactivate
```

### ENHSP: Planner 

Install the java dependencies
```
sudo apt-get install openjdk-17-jdk
```

Then compile the planner by running:
```
cd ENHSP-Public
./compile
```

### LLM API: Set up Claude API key

Replace _**KEY**_ with the correct API key in `set_claude_api_key.sh`:  _export ANTHROPIC_API_KEY='**KEY**'_

Then set up the key by running:
```
source set_claude_api_key.sh
```

## Run main

Activate virtual environment:
```
source env_NTCORE/bin/activate
```

Run the main process:
```
python main.py
```

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