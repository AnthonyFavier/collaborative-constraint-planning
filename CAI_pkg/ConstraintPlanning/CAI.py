"""
Docstring for CAI_pkg.ConstraintPlanning.CAI
"""

import time
import click

from NumericTCORE.bin.ntcore import main as ntcore

from .Constraints import ConstraintManager
from .Planner import planner
from .. import LLM
from .. import Tools
from .. import Globals as G
from ..Helpers import mprint, startTimer, stopTimer
from ..Verifier import Verifier

## ADD CONSTRAINT ##
def createConstraint(nl_constraint, input_time=0):
    r = G.CM.createRaw(nl_constraint)
    r.time_input += input_time
    return r

## PLAN ##
def planWithConstraints():
    # get activated constraints
    # update problem with activated constraints
    # compile problem
    # Solve it
    
    mprint("\n=== PLANNING ===")
    
    # Get activated constraints
    activated_encodings = []
    for k,c in G.CM.decomposed_constraints.items():
        if c.isActivated():
            activated_encodings.append(c.encoding)
        
    if not len(activated_encodings):
        mprint("\nNo active constraints: Planning without constraints")
        problem_name = G.PROBLEM_NAME
        time_compilation = 0
    else:
        problem_name = G.PlanFiles.COMPILED
        
        updatedProblem = Tools.updateProblem(G.PROBLEM_PDDL, activated_encodings)
        
        # Save updated problem in a file
        with open(G.UPDATED_PROBLEM_PATH, "w") as f:
            f.write(updatedProblem)
        
        # Compile the updated problem
        mprint("\nCompiling ... ", end="")
        time_compilation = time.time()
        ntcore(G.DOMAIN_PATH, G.UPDATED_PROBLEM_PATH, "tmp/pddl_files/", achiever_strategy=G.NtcoreStrategy.DELTA, verbose=False)
        time_compilation = time.time() - time_compilation
        mprint(f"OK [{time_compilation:.2f}s]")
        
    # Plan
    mprint(f"Planning ({G.planning_mode}{'' if G.timeout==None else f', TO={G.timeout}s'}) ... ", end="" )
    time_planning = time.time()
    result, plan, planlength, metric, fail_reason = planner(problem_name, plan_mode=G.planning_mode, hide_plan=True, timeout=G.timeout)
    time_planning = time.time()-time_planning
    
    if result=='success':
        mprint(f"OK [{time_planning:.2f}s]")
    else:
        mprint(f"Failed {fail_reason} [{time_planning:.2f}s]")
    return result, plan, planlength, metric, fail_reason, time_compilation, time_planning

## SUGGESTIONS ##
def generate_suggestions(show=True):
    d = time.time()
    startTimer()
    mprint("\nElaborating strategies suggestions ... ", end="")
    G.suggestions = LLM.suggestions()
    # remove empty lines
    G.suggestions = G.suggestions.splitlines()
    while True:
        try: G.suggestions.remove('')
        except ValueError: break
    G.suggestions = '\n'.join(G.suggestions)
    stopTimer()
    d = time.time() - d
    mprint(f"OK [{d:.1f}s]")
    if show:
        mprint(G.suggestions)

## INIT ##
def init(problem_name, planning_mode, timeout):
    """
    Docstring for init
    
    :param problem_name: name of the problem being solved, 
        matching a pair of PDDL domain+problem file path defined in module 'defs.py'
    :param planning_mode: sets the initial planning mode, based on PlanMode from 'defs.py'
    :param timeout: time budget for planning (Mandatory for anytime planning)

    Retrieve the domain and problem paths based on given problem name.
    Sets global planning mode and time budget/timeout.
    Creates the global ConstraintManager (CM).
    Performs a few initial checks:
    - Parse initial problem
    - Look for presence of constraints in initial problem
    Creates the symbolic Verifier
    Sets content of global domain/problem/plan variables.
    Initialize LLM module (Only used for 'suggestions')
    Setup agentic part (Setup RAG and build Langgraph graph)
    """
    
    if not G.PROBLEMS.exists(problem_name):
        click.echo("Unknown problem.\n" + G.PROBLEMS.get_known_problems())
        exit()
        
    G.PROBLEM_NAME = problem_name
    G.DOMAIN_PATH, G.PROBLEM_PATH = G.PROBLEMS.get_paths(G.PROBLEM_NAME)


    G.planning_mode = planning_mode
    
    G.timeout = float(timeout) if timeout!=None else None
    if G.timeout==0.0:
        G.timeout=None
        
    try:
        t = float(timeout)
        assert t>0
        G.timeout = t
    except AssertionError:
        G.timeout = None
        if G.planning_mode in [G.PlanMode.ANYTIME, G.PlanMode.ANYTIMEAUTO]:
            print('WARNING: Timeout disabled with Anytime planning mode!')
    timeout_str = f', TO={G.timeout}' if G.timeout is not None else ''
    
    G.CM = ConstraintManager(G.PROBLEM_NAME)
    
    # Show selected problem
    print(f"Planning mode: {planning_mode}{timeout_str}\nProblem ({problem_name}):\n\t- {G.DOMAIN_PATH}\n\t- {G.PROBLEM_PATH}")
    
    # Try parsing the initial problem
    try:
        parsed = Tools.parse_pddl3(G.DOMAIN_PATH, G.PROBLEM_PATH)
    except Exception as e:
        print("ERROR", e)
        raise Exception(f"Unable to parse the initial problem.")
    
    # Check if no initial constraints
    if parsed.problem.trajectory_constraints!=[]:
        raise Exception(f"There are already constraints in the initial problem.\n{parsed.problem.trajectory_constraints}")

    # Create Verifier
    G.verifier = Verifier(parsed.problem)
    
    # Open initial problem
    with open(G.DOMAIN_PATH, "r") as f:
        DOMAIN_PDDL = f.read()
    with open(G.PROBLEM_PATH, "r") as f:
        G.PROBLEM_PDDL = f.read()
    G.current_plan = "No plan"
    G.suggestions = "* No suggestions *"

    # Init LLM system message with domain and problem
    LLM.setSystemMessage(DOMAIN_PDDL, G.PROBLEM_PDDL)
        
from unified_planning.io import PDDLReader
def checkIfUpdatedProblemIsParsable():
    # Get activated constraints
    activated_encodings = [c.encoding for k,c in G.CM.decomposed_constraints.items() if c.isActivated()]
    encodingsStr = "\n".join(activated_encodings)
    updatedProblem = Tools.updateProblem(G.PROBLEM_PDDL, activated_encodings)
    with open(G.UPDATED_PROBLEM_PATH, "w") as f:
        f.write(updatedProblem)
    reader = PDDLReader()
    try:
        pb = reader.parse_problem(G.DOMAIN_PATH, G.UPDATED_PROBLEM_PATH)
        return True, encodingsStr, None
    except Exception as err:
        return False, encodingsStr, err
        
def showSettings():
    timeout_str = f', TO={G.timeout}' if G.timeout!=None else ''
    mprint(f"Setting: {G.SETTING_NAME}")
    mprint(f"Planning mode: {G.planning_mode}{timeout_str}\nProblem ({G.PROBLEM_NAME}):\n\t- {G.DOMAIN_PATH}\n\t- {G.PROBLEM_PATH}")
