from .. import Globals as G

import sys
import os
import signal
import subprocess
import click

def planner(problem_name, plan_mode=G.PlanMode.DEFAULT, hide_plan=False, timeout=None):
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
    if timeout!=None and timeout<=0:
        result = 'failed'
        plan = ''
        fail_reason = 'No time budget'
        planlength = -1
        metric = -1
        return result, plan, planlength, metric, fail_reason
    
    if problem_name==G.PlanFiles.COMPILED:
        DOMAIN_PATH, PROBLEM_PATH = G.COMPILED_DOMAIN_PATH, G.COMPILED_PROBLEM_PATH
    else:
        DOMAIN_PATH, PROBLEM_PATH = G.PROBLEMS.get_paths(problem_name)
        
    if G.PlanMode.OPTIMAL==plan_mode:
        mode = [f'-planner', f'{G.PlanMode.OPTIMAL}']
    elif G.PlanMode.SATISFICING==plan_mode:
        mode = ['-planner', f'{G.PlanMode.SATISFICING}']
    elif G.PlanMode.ANYTIME==plan_mode:
        mode = ['-anytime']
    elif G.PlanMode.ANYTIMEAUTO==plan_mode:
        mode = ['-anytime', '-autoanytime']
    elif G.PlanMode.DEFAULT==plan_mode:
        mode = []
    else:
        mode = ['-planner', plan_mode]
        # raise Exception("planner: plan_mode unknown")
    
    if timeout!=None and timeout!='None':
        timeout = float(timeout)
    else:
        timeout = None
    timeout_str = '' if timeout==None else f', TO={timeout}s'
    
    # mprint(f"\nPlanning ({plan_mode}{timeout_str}) ... ", end="" )
    
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
    
    # Get Info
    result = plan = fail_reason = ''
    planlength = 0
    metric = 0.0
    if stdout.find('Problem Solved')!=-1:
        result = 'success'
        try:
            find_txt = 'Found Plan:\n'
            i1_plan = stdout.rfind(find_txt) + len(find_txt)
            i2_plan = stdout.find('\n\n', i1_plan)
            plan = stdout[i1_plan:i2_plan]
            
            find_txt = 'Plan-Length:'
            i1_length = stdout.find(find_txt, i1_plan)+len(find_txt)
            i2_length = stdout.find('\n', i1_length)
            planlength = int(stdout[i1_length:i2_length])
            
            find_txt = 'Metric (Search):'
            i1_metric = stdout.find(find_txt, i1_plan)+len(find_txt)
            i2_metric = stdout.find('\n', i1_metric)
            metric = float(stdout[i1_metric:i2_metric])
        except:
            print('\n[ERROR]')
            print(f'<stdout>\n{stdout}\n</stdout>')
            print('i1_plan=', i1_plan)
            print('i2_plan=', i2_plan)
            print('i1_length=', i1_length)
            print('i2_length=', i2_length)
            print('i1_metric=', i1_metric)
            print('i2_metric=', i2_metric)
            raise Exception('Data extraction from planner stdout')
    elif stdout.find('Unsolvable Problem')!=-1 or stdout.find('Problem unsolvable')!=-1:
        result = 'failed'
        fail_reason = 'Unsolvable Problem'
    else:
        result = 'failed'
        fail_reason = 'Timeout'
                
    return result, plan, planlength, metric, fail_reason

@click.command(help=f"{G.PROBLEMS.get_known_problems()}")
@click.argument('problem_name')
@click.option('--original', 'files', flag_value=G.PlanFiles.ORIGINAL, default=True, help="Use the original problem files (default)")
@click.option('-c', '--compiled', 'files', flag_value=G.PlanFiles.COMPILED, help="Use the last compiled problem files. PROBLEM_NAME not used")
@click.option('-p', '--path', 'files', flag_value=G.PlanFiles.PATH, help="Use the domain and problem paths given. PROBLEM_NAME not used")
@click.option('-a', '--anytime', 'planning_mode', flag_value=G.PlanMode.ANYTIME, default=True, help="Set the planning mode to 'Anytime' (default)")
@click.option('-aa', '--anytimeauto', 'planning_mode', flag_value=G.PlanMode.ANYTIMEAUTO, help="Set the planning mode to 'AnytimeAuto'")
@click.option('-d', '--default', 'planning_mode', flag_value=G.PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
@click.option('-o', '--optimal', 'planning_mode', flag_value=G.PlanMode.OPTIMAL, help="Set the planning mode to 'Optimal'")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=G.PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('--custommode', 'custom_planning_mode', default="", help="Custom planning mode")
@click.option('--domain', 'domain_path', help="Path of domain")
@click.option('--problem', 'problem_path', help="Path of problem")
@click.option('--hide-plan', 'hide_plan', is_flag=True, default=False, help="Hide plan")
@click.option('-t', '--timeout', 'timeout', default=None, help="Timeout for planning")
def main(problem_name, files, planning_mode, custom_planning_mode, domain_path, problem_path, hide_plan, timeout):    
    if files==G.PlanFiles.COMPILED:
        d, p = G.COMPILED_DOMAIN_PATH, G.COMPILED_PROBLEM_PATH
        problem_name = G.PlanFiles.COMPILED
    elif files==G.PlanFiles.ORIGINAL:
        if not G.PROBLEMS.exists(problem_name):
            click.echo("Unknown problem.\n" + G.PROBLEMS.get_known_problems())
            exit()
        d, p = G.PROBLEMS.get_paths(problem_name)
    if files==G.PlanFiles.PATH:
        d, p = domain_path, problem_path
        G.PROBLEMS.add_problem(G.PlanFiles.PATH, d, p)
        problem_name = G.PlanFiles.PATH
        
    if custom_planning_mode!="":
        planning_mode = custom_planning_mode
    
    print(f"{planning_mode}\nProblem ({problem_name}):\n\t- {d}\n\t- {p}\n")
    planner(problem_name, plan_mode=planning_mode, hide_plan=hide_plan, timeout=timeout)

if __name__ == '__main__':
    main()