# CAI: Collaborative AI Agent

Human in the Loop constraint planning 
CAI 

## OVERVIEW

<img src="./misc/rsc/overview.jpg" width="600">

## INSTALLATION

See [INSTALL.md](INSTALL.md).



## RUN


**When using docker**: Allow display, and run the image:
```
$ xhost +local:docker
$ cd docker/
$ ./run_docker.sh
```

Activate virtual environment: `source env_cai/bin/activate`

Run the system:
```
python main.py [OPTIONS] PROBLEM_NAME
```

Problems and options can be listed using `python main.py --help`.

---
---

## Additional information

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

---

### Run Planner Only

You can also directly run the planner, only.
```
source env_cai/bin/activate
python planner.py [OPTIONS] PROBLEM_NAME
```

Problems and options can be listed using `python planner.py --help`

You can either use the original files corresponding to the given problem name or plan using the last compiled files using `-c`.

The planning mode used (i.e. optimal, satisficing, default) can be used using the respective options `-o`, `-s`, `-d`.

---

### [Alternative] Detailed install

#### Install python requirements
```
pip install --upgrade pip -r requirements.txt --no-cache-dir
```

#### Manual patch

Run a small patch for unified_planning and customtkinter. Respectivelly allow to handle default _real_ and _int_ values and use ScrollableFrame with both bars.
```
python patches.py 
```

#### NTCORE: Numeric constraints compilation

**Note**: Conflicting command line management in `NumericTCORE/bin/ntcore.py`, already solved by commenting `@click.command()`.

Install the package:
```
cd NumericTCORE/
pip install .
```

#### ENHSP: Compile planner 

Compile the planner by running:
```
cd ENHSP-Public
./compile
```

Ignore the two _Note:_ lines.
