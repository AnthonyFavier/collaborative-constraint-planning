#!/usr/bin/env python3.10
import sys
import llm_claude
import tools
from NumericTCORE.bin.ntcore import main as ntcore
import click
from planner import planner
from defs import *

def CAI(problem_name, planning_mode):
    
    DOMAIN_PATH, PROBLEM_PATH = PROBLEMS[problem_name]
    
    # Show selected problem
    print(f"{planning_mode}\nProblem ({problem_name}):\n\t- {DOMAIN_PATH}\n\t- {PROBLEM_PATH}\n")
    
    # Try parsing the initial problem
    try:
        parsed = tools.parse_pddl3(DOMAIN_PATH, PROBLEM_PATH)
    except Exception as e:
        print("ERROR", e)
        raise Exception(f"Unable to parse the initial problem.")

    # Set extracted fluent names (used during verification)
    tools.set_fluent_names([f.name for f in parsed.problem.fluents])
    
    # Open initial problem
    with open(DOMAIN_PATH, "r") as f:
        domain = f.read()
    with open(PROBLEM_PATH, "r") as f:
        problem = f.read()
    
    while True:
        
        #  Input of user Strategy to test
        print(color.BOLD + "Enter your preferences:\n" + color.END)
        pref = input()
        if pref=="exit":
            exit()
        
        success = False
        MAX_ENCODING_TRY = 5
        for i in range(MAX_ENCODING_TRY):
            
            # 1 # Encode the preferences
            if i==0: # first time
                print(color.BOLD + "\nEncoding..." + color.END)
                encodedPref = llm_claude.encodePrefs(domain, problem, pref)
            else: # re-encoding 
                # input()
                print(color.BOLD + "\nRe-Encoding..." + color.END)
                encodedPref = llm_claude.reencodePrefs(feedback)
                
            # 2 # Update the problem and verify the encoding
                # If error, re-encode with feedback
            filteredEncoding = tools.filterEncoding(encodedPref)
            filteredEncoding = tools.initialFixes(filteredEncoding)
            print(filteredEncoding)
            updatedProblem = tools.updateProblem(problem, filteredEncoding)
            encodingOK, feedback = tools.verifyEncoding(updatedProblem, domain, filteredEncoding)
            if not encodingOK:
                print("Verifier: Encoding not OK")
                print(feedback)
                continue
            
            # 3 # Save updated problem in a file
            with open(UPDATED_PROBLEM_PATH, "w") as f:
                f.write(updatedProblem)

            # 4 # Compile the updated problem
                # If error, re-encode
            try:
                print(color.BOLD + "\nCompiling..." + color.END)
                ntcore(DOMAIN_PATH, UPDATED_PROBLEM_PATH, "tmp/", achiever_strategy=NtcoreStrategy.DELTA, verbose=False)
            except Exception as error:
                print(error)
                print("NTCORE: Failed to compile updated problem...")
                feedback = f"There is the following error in the encoding: {error}. Fix it."
                continue
            
            # 5 # Plan using the compiled problem
            feedback, plan = planner(PlanFiles.COMPILED, plan_mode=planning_mode)
            success = feedback=='success'
            if success:
                print(plan)
                # print initial input and encoding
                print('\n"' + pref + '"' + filteredEncoding)
                break
            
        
        if not success:
            print("Failure: Maximum attempts reached unsuccessfully...")
            print('\n"' + pref + '"')
            
        
        llm_claude.clear_message_history()
        print('\n=======================')
        print('=======================\n')


@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name')
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, default=True, help="Set the planning mode to 'Optimal' (default)")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
def main(problem_name, planning_mode):
    
    if not problem_name in PROBLEMS:
        click.echo("Unknown problem.\n" + KNOWN_PROBLEMS_STR)
        exit()
    
    CAI(problem_name, planning_mode)

if __name__ == '__main__':
    main()