#!/usr/bin/env python3.10
import sys
import subprocess
import click
from defs import *

def planner(problem_name, plan_mode=PlanMode.DEFAULT):
    if problem_name==PlanFiles.COMPILED:
        DOMAIN_PATH, PROBLEM_PATH = COMPILED_DOMAIN_PATH, COMPILED_PROBLEM_PATH
    else:
        DOMAIN_PATH, PROBLEM_PATH = PROBLEMS[problem_name]
    
    print(color.BOLD + f"\nPlanning ({plan_mode}) ..." + color.END)
    planner = f'-planner {plan_mode}' if plan_mode!=PlanMode.DEFAULT else ''
    result = subprocess.run(
        [f"java -jar ENHSP-Public/enhsp.jar -o {DOMAIN_PATH} -f {PROBLEM_PATH} {planner}"], shell=True, capture_output=True, text=True
    )
    result = result.stdout.splitlines()
    
    try: # if successful
        # print plan
        for l in result[result.index('Found Plan:'):]:
            print(l)
        feedback = "success"
    
    except:
        print('Unsolvable Problem')
        feedback = f"The encoding made the problem unsolvable. Fix it."
        
    return feedback

@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name')
@click.option('--original', 'files', flag_value=PlanFiles.ORIGINAL, default=True, help="Use the original problem files (default)")
@click.option('-c', '--compiled', 'files', flag_value=PlanFiles.COMPILED, help="Use the last compiled problem files. PROBLEM_NAME not used")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, default=True, help="Set the planning mode to 'Optimal' (default)")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
def main(problem_name, files, planning_mode):    
    if files==PlanFiles.COMPILED:
        d, p = COMPILED_DOMAIN_PATH, COMPILED_PROBLEM_PATH
        problem_name = PlanFiles.COMPILED
    elif files==PlanFiles.ORIGINAL:
        if not problem_name in PROBLEMS:
            click.echo("Unknown problem.\n" + KNOWN_PROBLEMS_STR)
            exit()
        d, p = PROBLEMS[problem_name]
    
    print(f"{planning_mode}\nProblem ({problem_name}):\n\t- {d}\n\t- {p}\n")
    planner(problem_name, plan_mode=planning_mode)

if __name__ == '__main__':
    main()