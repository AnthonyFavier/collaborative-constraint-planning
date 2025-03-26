#!/usr/bin/env python3.10
import sys
import subprocess
import click
from defs import *

def planner(problem_name, plan_mode=PlanMode.DEFAULT, show_plan=False):
    if problem_name==PlanFiles.COMPILED:
        DOMAIN_PATH, PROBLEM_PATH = COMPILED_DOMAIN_PATH, COMPILED_PROBLEM_PATH
    else:
        DOMAIN_PATH, PROBLEM_PATH = PROBLEMS[problem_name]
    
    mprint(color.BOLD + f"\nPlanning ({plan_mode}) ..." + color.END)
    planner = f'-planner {plan_mode}' if plan_mode!=PlanMode.DEFAULT else ''
    result = subprocess.run(
        [f"java -jar ENHSP-Public/enhsp.jar -o {DOMAIN_PATH} -f {PROBLEM_PATH} {planner}"], shell=True, capture_output=True, text=True
    )
    result = result.stdout.splitlines()
    plan = ""
    
    try: # if successful
        # print plan
        for l in result[result.index('Found Plan:'):]:
            plan += l + '\n'
        feedback = "success"
        if show_plan:
            print(plan)
    
    except:
        feedback = result
        
    return feedback, plan

@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name')
@click.option('--original', 'files', flag_value=PlanFiles.ORIGINAL, default=True, help="Use the original problem files (default)")
@click.option('-c', '--compiled', 'files', flag_value=PlanFiles.COMPILED, help="Use the last compiled problem files. PROBLEM_NAME not used")
@click.option('-p', '--path', 'files', flag_value=PlanFiles.PATH, help="Use the domain and problem paths given. PROBLEM_NAME not used")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, default=True, help="Set the planning mode to 'Optimal' (default)")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
@click.option('--domain', 'domain_path', help="Path of domain")
@click.option('--problem', 'problem_path', help="Path of problem")
@click.option('--show', 'show_plan', is_flag=True, default=False, help="Show plan")
def main(problem_name, files, planning_mode, domain_path, problem_path, show_plan):    
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
    
    print(f"{planning_mode}\nProblem ({problem_name}):\n\t- {d}\n\t- {p}\n")
    planner(problem_name, plan_mode=planning_mode, show_plan=show_plan)

if __name__ == '__main__':
    main()