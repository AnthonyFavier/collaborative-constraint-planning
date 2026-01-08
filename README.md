# CAI: Collaborative AI Agent

Human in the Loop constraint planning 
CAI 

## OVERVIEW

<img src="./misc/rsc/overview.jpg" width="600">


## PAPER

- *Favier, A., La, N., Verma, P., & Shah, J.* (2025). **A Collaborative Numeric Task Planning Framework based on Constraint Translations using LLMs**. In: ICAPS 2025 Workshops on Human-Aware and Explainable Planning and LM4Plan. [PDF](https://openreview.net/pdf?id=rRjEMmavbR)
 <!-- ![DOI:10.1007/978-3-031-21438-7_60](https://zenodo.org/badge/DOI/10.1007/978-3-319-76207-4_15.svg)](https://doi.org/10.1007/978-3-031-21438-7_60) -->

- *Favier, A., La, N., Verma, P., & Shah, J. A.* (2025). **An LLM-powered Collaborative Task Planning Framework**. In: ICAPS 2025 Demo Track. [PDF](https://icaps25.icaps-conference.org/program/demos-pdfs/ICAPS25-Demo_paper_6.pdf)

## INSTALLATION

See [INSTALL.md](INSTALL.md).

## RUN


**When using docker**: Allow display, and run the image:
```
$ xhost +local:docker
$ cd docker/
$ ./run_docker.sh
```

Activate virtual environment and run the system with default problem (zenoreal):
```
$ source env_cai/bin/activate
$ python main.py
```

Problems and options can be listed using `python main.py --help`.

---
---

## Additional information

### Adding new problems

To add to new problems open [Globals.py](collab_planning/Globals.py) and add a new key to the `PROBLEMS` dictionary such as: 
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

## Acknowledgments

This work was in part supported by the Office of Naval Research (ONR) under grant N000142312883.
