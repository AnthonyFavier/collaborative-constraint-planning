# Installation Instructions

## LLM APIs

Create a `.env` file in root folder to store API keys in the form:
```
ANTHROPIC_API_KEY = 'REPLACE_WITH_YOUR_KEY'
OPENAI_API_KEY = 'REPLACE_WITH_YOUR_KEY'
API-NINJA_API_KEY = 'REPLACE_WITH_YOUR_KEY'
```

Replace `REPLACE_WITH_YOUR_KEY` with your respective API keys.

API-NINJA is free [link](https://api-ninjas.com/)

## PDSim Simulator [*Optional*]

The framework can simulate plans with PDSim. 
This is optinal. If the simulator is not installed or linked, the framework will still work and plan, only a warning will be shown when starting.

### Follow the PDSim instructions

Clone this repo and follow instructions

https://github.com/AnthonyFavier/PDSim_Scenes_zenotravel

### Link with framework

Set the path of the PDInstance file `PDSIM_INSTANCE_PATH` line 3 in [UpdatePDSimPlan.py](collab_planning/UpdatePDSimPlan.py)

*REPO_LOCATION*/PDSim_Scenes_zenotravel/Assets/Scenes/ZenoR/Data/PdSimProblem.asset

By default, it assumes the repo has been cloned in home/UNAME/ws/

## Docker Approach [*Recommended*]

Move to the `docker` folder and run the building script: 
```
$ cd docker/
$ ./build_docker.sh
```

See [README.md](README.md#run) for running instructions.

## Manual Detailed Approach

Tested on Ubuntu 24.04

### Install dependencies and Python3.10

Rely on **Python3.10** so it might be required to install this specific version through: `apt` or `deadsnake`
```
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt-get install -y python3.10 python3.10-tk
```

```
$ sudo apt-get -y install openjdk-17-jdk unifont
```

### Create a python3.10 virtual environment 

**IMPORTANT**: Currently only supporting **Venv** (<u>not</u> **Conda**) due to later manual patching of the packages `unified-planning` and `customtkinter`.

```
$ python3.10 -m venv env_cai
$ source env_cai/bin/activate
```
**Note**: to deactivate the python environment simply run: `deactivate`

#### Install python requirements
```
$ pip install --upgrade pip -r requirements.txt --no-cache-dir
```

#### Manual patch

Run a small patch for unified_planning and customtkinter. Respectivelly allow to handle default _real_ and _int_ values and use ScrollableFrame with both bars.
```
$ python patches.py 
```

#### NTCORE: Numeric constraints compilation

**Note**: Conflicting command line management in `NumericTCORE/bin/ntcore.py`, already solved by commenting `@click.command()`.

Install the package:
```
$ cd NumericTCORE/
$ pip install .
```

#### ENHSP: Compile planner 

Compile the planner by running:
```
$ cd ENHSP-Public
$ ./compile
```

Ignore the two _Note:_ lines.