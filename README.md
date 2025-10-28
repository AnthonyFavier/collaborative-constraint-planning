# CAI: Collaborative AI Agent

Human in the Loop constraint planning 
CAI 

## OVERVIEW

![plot](./rsc/overview.jpg "Overview")

## INSTALLATION

Tested on Ubuntu 20.04

### 1. Create a python3.10 virtual environment 

**IMPORTANT**: Currently only supporting **Venv** (<u>not</u> Conda) due to later manual patching of the packages `unified-planning` and `customtkinter`.

```
python3.10 -m venv env_cai
source env_cai/bin/activate
```

### 2. Install dependencies

```
pip install --upgrade pip -r requirements.txt --no-cache-dir
sudo apt-get install openjdk-17-jdk python3.10-tk unifont
```

Run a small patch for unified_planning and customtkinter. Respectivelly allow to handle default _real_ and _int_ values and use ScrollableFrame with both bars.
```
python patches.py 
```


**Note**: to deactivate the python environment simply run: `deactivate`


### 3. NTCORE: Numeric constraints compilation


**Note**: Conflicting command line management in `NumericTCORE/bin/ntcore.py`, already solved by commenting `@click.command()`.

Install the package:
```
cd NumericTCORE/
pip install .
```

### 4. ENHSP: Compile planner 

Compile the planner by running:
```
cd ENHSP-Public
./compile
```

Ignore the two _Note:_ lines.

### 5. LLM APIs

Create a `.env` file in root folder to store API keys in the form:
```
ANTHROPIC_API_KEY = 'REPLACE_WITH_YOUR_KEY'
OPENAI_API_KEY = 'REPLACE_WITH_YOUR_KEY'
```

Replace `REPLACE_WITH_YOUR_KEY` with your respective API keys.

## RUN

Activate virtual environment: `source env_cai/bin/activate`

Run the system:
```
python main.py [OPTIONS] PROBLEM_NAME
```

Problems and options can be listed using `python main.py --help`.

---

### Adding new problems

To add to new problems open `defs.py` and add a new key to the `PROBLEMS` dictionary such as: 
```
PROBLEMS = {
    ...
    *existing_problems*
    ...
    'new_problem_name': ('Path/To/Domain.pddl', 'Path/To/Problem.pddl'),
}
```

### Run Planner Only

You can also directly run the planner, only.
```
source env_cai/bin/activate
python planner.py [OPTIONS] PROBLEM_NAME
```

Problems and options can be listed using `python planner.py --help`

You can either use the original files corresponding to the given problem name or plan using the last compiled files using `-c`.

The planning mode used (i.e. optimal, satisficing, default) can be used using the respective options `-o`, `-s`, `-d`.
