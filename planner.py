import sys
import os
import signal
import subprocess
import click
from defs import *

def planner(problem_name, plan_mode=PlanMode.DEFAULT, hide_plan=False, timeout=None):
    """
    Inputs:
    - problem_name: one of the names provided in defs.py
    - [OPTIONAL] plan_mode: defines if using default, satisfacing, optimal or anytime planning mode
    - [OPTIONAL] hide_plan: if False will print the computed plan
    - [OPTIONAL] timeout: time after which the planning process is shutdown
    Return:
    - feedback: either 'success' if planning is successful, otherwise an error message
    - plan: plan computed, if successful, otherwise empty string
    """
    if problem_name==PlanFiles.COMPILED:
        DOMAIN_PATH, PROBLEM_PATH = COMPILED_DOMAIN_PATH, COMPILED_PROBLEM_PATH
    else:
        DOMAIN_PATH, PROBLEM_PATH = PROBLEMS[problem_name]
        
    if PlanMode.OPTIMAL==plan_mode:
        mode = [f'-planner', f'{PlanMode.OPTIMAL}']
    elif PlanMode.SATISFICING==plan_mode:
        mode = ['-planner', f'{PlanMode.SATISFICING}']
    elif PlanMode.ANYTIME==plan_mode:
        mode = ['-anytime']
    elif PlanMode.ANYTIMEAUTO==plan_mode:
        mode = ['-anytime', '-autoanytime']
    elif PlanMode.DEFAULT==plan_mode:
        mode = []
    else:
        mode = ['-planner', plan_mode]
        # raise Exception("planner: plan_mode unknown")
    
    if timeout!=None and timeout!='None':
        timeout = float(timeout)
    else:
        timeout = None
    timeout_str = '' if timeout==None else f', TO={timeout}s'
    
    mprint(color.BOLD + f"\nPlanning ({plan_mode}{timeout_str}) ..." + color.END)
    
    proc = subprocess.Popen(
            ["java", "-jar", "ENHSP-Public/enhsp.jar", "-o", f"{DOMAIN_PATH}", "-f", f"{PROBLEM_PATH}"] + mode, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            preexec_fn=os.setsid, 
            text=True
        )
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        
    stdout, stderr = proc.communicate()
    
    last_found_plan_i = stdout.rfind("Found Plan:")
    last_found_plan_end_i = stdout.rfind("NEW COST") # minus previous '\n'

    if last_found_plan_i==-1:
        feedback = "Failed planning " + stderr
        plan = ""
    else:
        feedback = "success"
        plan = stdout[last_found_plan_i:last_found_plan_end_i]
        if not hide_plan:
            print(plan)
                
    return feedback, plan, stdout

@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name')
@click.option('--original', 'files', flag_value=PlanFiles.ORIGINAL, default=True, help="Use the original problem files (default)")
@click.option('-c', '--compiled', 'files', flag_value=PlanFiles.COMPILED, help="Use the last compiled problem files. PROBLEM_NAME not used")
@click.option('-p', '--path', 'files', flag_value=PlanFiles.PATH, help="Use the domain and problem paths given. PROBLEM_NAME not used")
@click.option('-a', '--anytime', 'planning_mode', flag_value=PlanMode.ANYTIME, default=True, help="Set the planning mode to 'Anytime' (default)")
@click.option('-aa', '--anytimeauto', 'planning_mode', flag_value=PlanMode.ANYTIMEAUTO, help="Set the planning mode to 'AnytimeAuto'")
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, help="Set the planning mode to 'Optimal'")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('--custommode', 'custom_planning_mode', default="", help="Custom planning mode")
@click.option('--domain', 'domain_path', help="Path of domain")
@click.option('--problem', 'problem_path', help="Path of problem")
@click.option('--hide-plan', 'hide_plan', is_flag=True, default=False, help="Hide plan")
@click.option('-t', '--timeout', 'timeout', default=None, help="Timeout for planning")
def main(problem_name, files, planning_mode, custom_planning_mode, domain_path, problem_path, hide_plan, timeout):    
    if files==PlanFiles.COMPILED:
        d, p = COMPILED_DOMAIN_PATH, COMPILED_PROBLEM_PATH
        problem_name = PlanFiles.COMPILED
    elif files==PlanFiles.ORIGINAL:
        if not problem_name in PROBLEMS:
            click.echo("Unknown problem.\n" + KNOWN_PROBLEMS_STR)
            exit()
        d, p = PROBLEMS[problem_name]
    if files==PlanFiles.PATH:
        d, p = domain_path, problem_path
        PROBLEMS[PlanFiles.PATH] = (d, p)
        problem_name = PlanFiles.PATH
        
    if custom_planning_mode!="":
        planning_mode = custom_planning_mode
    
    print(f"{planning_mode}\nProblem ({problem_name}):\n\t- {d}\n\t- {p}\n")
    planner(problem_name, plan_mode=planning_mode, hide_plan=hide_plan, timeout=timeout)

if __name__ == '__main__':
    main()