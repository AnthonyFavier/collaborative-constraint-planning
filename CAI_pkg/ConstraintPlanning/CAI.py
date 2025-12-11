from . import Constraints
from .Planner import planner
from .. import LLM
from .. import Tools
from ..Verifier import Verifier
from ..defs import *
from ..Agentic_constraint import setup_agentic

from NumericTCORE.bin.ntcore import main as ntcore

import time
import click
        
# ABLATION_FLAGS #
WITH_E2NL = True
WITH_VERIFIER = True
WITH_DECOMP = True
WITH_DECOMP_CONFIRM = True
SETTING_NAME = 'DEFAULT'

global g_problem_name, g_domain, g_problem
global g_planning_mode, g_timeout
global g_plan
global g_suggestions
global DOMAIN_PATH, PROBLEM_PATH
global CM # Constraint Manager
global verifier

## ADD CONSTRAINT ##
def createConstraint(nl_constraint, input_time=0):
    r = CM.createRaw(nl_constraint)
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
    for k,c in CM.decomposed_constraints.items():
        if c.isActivated():
            activated_encodings.append(c.encoding)
        
    if not len(activated_encodings):
        mprint("\nNo active constraints: Planning without constraints")
        problem_name = g_problem_name
        time_compilation = 0
    else:
        problem_name = PlanFiles.COMPILED
        
        updatedProblem = Tools.updateProblem(g_problem, activated_encodings)
        
        # Save updated problem in a file
        with open(UPDATED_PROBLEM_PATH, "w") as f:
            f.write(updatedProblem)
        
        # Compile the updated problem
        mprint("\nCompiling ... ", end="")
        time_compilation = time.time()
        ntcore(DOMAIN_PATH, UPDATED_PROBLEM_PATH, "tmp/pddl_files/", achiever_strategy=NtcoreStrategy.DELTA, verbose=False)
        time_compilation = time.time() - time_compilation
        mprint(f"OK [{time_compilation:.2f}s]")
        
    # Plan
    mprint(f"Planning ({g_planning_mode}{'' if g_timeout==None else f', TO={g_timeout}s'}) ... ", end="" )
    time_planning = time.time()
    result, plan, planlength, metric, fail_reason = planner(problem_name, plan_mode=g_planning_mode, hide_plan=True, timeout=g_timeout)
    time_planning = time.time()-time_planning
    
    if result=='success':
        mprint(f"OK [{time_planning:.2f}s]")
    else:
        mprint(f"Failed {fail_reason} [{time_planning:.2f}s]")
    return result, plan, planlength, metric, fail_reason, time_compilation, time_planning

## SUGGESTIONS ##
g_suggestions = "* No suggestions *"
def suggestions(show=True):
    global g_suggestions
    d = time.time()
    startTimer()
    mprint("\nElaborating strategies suggestions ... ", end="")
    suggestions = LLM.suggestions()
    # remove empty lines
    suggestions = suggestions.splitlines()
    while True:
        try: suggestions.remove('')
        except ValueError: break
    suggestions = '\n'.join(suggestions)
    # save
    g_suggestions = suggestions
    stopTimer()
    d = time.time() - d
    mprint(f"OK [{d:.1f}s]")
    if show:
        mprint(g_suggestions)

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

    global g_problem_name, g_domain, g_problem
    global g_plan
    global g_planning_mode, g_timeout
    global DOMAIN_PATH, PROBLEM_PATH
    global CM
    global verifier
    
    if not PROBLEMS.exists(problem_name):
        click.echo("Unknown problem.\n" + PROBLEMS.get_known_problems())
        exit()
        
    g_problem_name = problem_name
    DOMAIN_PATH, PROBLEM_PATH = PROBLEMS.get_paths(g_problem_name)


    g_planning_mode = planning_mode
    
    g_timeout = float(timeout) if timeout!=None else None
    if g_timeout==0.0:
        g_timeout=None
        
    try:
        t = float(timeout)
        assert t>0
        g_timeout = t
    except:
        g_timeout = None
        if g_planning_mode in [PlanMode.ANYTIME, PlanMode.ANYTIMEAUTO]:
            print('WARNING: Timeout disabled with Anytime planning mode!')
    timeout_str = f', TO={g_timeout}' if g_timeout!=None else ''
    
    CM = Constraints.ConstraintManager(g_problem_name)
    
    # Show selected problem
    print(f"Planning mode: {planning_mode}{timeout_str}\nProblem ({problem_name}):\n\t- {DOMAIN_PATH}\n\t- {PROBLEM_PATH}")
    
    # Try parsing the initial problem
    try:
        parsed = Tools.parse_pddl3(DOMAIN_PATH, PROBLEM_PATH)
    except Exception as e:
        print("ERROR", e)
        raise Exception(f"Unable to parse the initial problem.")
    
    # Check if no initial constraints
    if parsed.problem.trajectory_constraints!=[]:
        raise Exception(f"There are already constraints in the initial problem.\n{parsed.problem.trajectory_constraints}")

    # Create Verifier
    verifier = Verifier(parsed.problem)
    
    # Open initial problem
    with open(DOMAIN_PATH, "r") as f:
        g_domain = f.read()
    with open(PROBLEM_PATH, "r") as f:
        g_problem = f.read()
    g_plan = "No plan"

    # Init LLM system message with domain and problem
    LLM.setSystemMessage(g_domain, g_problem)
        
    # Set up agentic part:
    setup_agentic()

from unified_planning.io import PDDLReader
def checkIfUpdatedProblemIsParsable():
    # Get activated constraints
    activated_encodings = [c.encoding for k,c in CM.decomposed_constraints.items() if c.isActivated()]
    encodingsStr = "\n".join(activated_encodings)
    updatedProblem = Tools.updateProblem(g_problem, activated_encodings)
    with open(UPDATED_PROBLEM_PATH, "w") as f:
        f.write(updatedProblem)
    reader = PDDLReader()
    try:
        pb = reader.parse_problem(DOMAIN_PATH, UPDATED_PROBLEM_PATH)
        return True, encodingsStr, None
    except Exception as err:
        return False, encodingsStr, err
        
def showSettings():
    timeout_str = f', TO={g_timeout}' if g_timeout!=None else ''
    DOMAIN_PATH, PROBLEM_PATH = PROBLEMS.get_paths(g_problem_name)
    mprint(f"Setting: {SETTING_NAME}")
    mprint(f"Planning mode: {g_planning_mode}{timeout_str}\nProblem ({g_problem_name}):\n\t- {DOMAIN_PATH}\n\t- {PROBLEM_PATH}")
