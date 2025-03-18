#!/usr/bin/env python3.10
import sys
import llm_claude
import llm_NL_decomposition
import tools
from NumericTCORE.bin.ntcore import main as ntcore
import click
from planner import planner
from defs import *
from updatePDSimPlan import main as updatePDSimPlan
import Constraints
from UserOption import UserOption
        
CM = Constraints.ConstraintManager()

def addConstraints(domain, problem):
    nl_constraints = []
    while True:
        if not len(nl_constraints):
            print(color.BOLD + "\nEnter your first constraint:\n> " + color.END, end="")
        else:
            print(color.BOLD + "\nPress Enter to validate or type another constraint:\n> " + color.END, end="")
            
        t = input()
        if t=="":
            break
        else:
            nl_constraints.append(t)
    
    new_r = []
    for nl_constraint in nl_constraints:
        r = CM.createRaw(nl_constraint)
        new_r.append(r)
        
        result = llm_NL_decomposition.decompose(domain, problem, nl_constraint)
        result = llm_NL_decomposition.removeFormating(result)
        
        # for c in constraints:
        for c in result.splitlines():
            CM.createDecomposed(r, c)
            
        r.showWithChildren()
        
        input("is ok?")
        
        # TODO: Ask if decomposition ok?
        # otherwise retry
        # Different options: retry, with comment?, delete this constraint, replace this constraint
    
    # When all ok, encode the decomposed of all new r
    
    # Encoding
    print(color.BOLD + "\nEncoding..." + color.END)
    for r in new_r:
        for c in r.children:
            encodedPref = llm_NL_decomposition.encodePrefs(domain, problem, c.nl_constraint)
            filteredEncoding = tools.newfilterEncoding(encodedPref)
            filteredEncoding = tools.initialFixes(filteredEncoding)
            # TODO: Verify encoding somehow ?
            c.encoding = filteredEncoding
        
def deleteConstraints():
    # ask which id to remove
    # if R# remove raw constraint and all decomposed associated
    # if D# remove only decompose from general list and from parent children
    
    loop = True
    while loop:
        loop = False
        x = input("Which constraints you want to delete? (type symbol, separated by commas or space, leave empty to cancel)\n> ")
        if x=='':
            print("Deletion aborted.")
            return None
        
        x = " ".join(x.split(',')).upper()
        x = x.split()
        for c in x:
            if not c in CM.constraints:
                print("One or more constraints not recognized.\n")
                loop = True
                break
    
    print('\n' + ", ".join(x) + " will be deleted.")
    while True:
        answer = input("Confirm (y/n)? ")
        if answer in ['y', 'n']:
            if answer=='n':
                print("Deletion aborted.")
                return None
            break
            
    # Deletion
    for symbol in x:
        if symbol not in CM.constraints:
            # already deleted
            continue
    
        if symbol in CM.raw_constraints:
            constraint = CM.constraints[symbol]
            CM.constraints.pop(constraint.symbol)
            CM.raw_constraints.pop(constraint.symbol)
            for child in constraint.children:
                CM.constraints.pop(child.symbol)
                CM.decomposed_constraints.pop(child.symbol)
                del child
            del constraint
            
        elif symbol in CM.decomposed_constraints:
            constraint = CM.constraints[symbol]
            # Warning if deleting only child of a constraint
            if len(constraint.parent.children)==1:
                print(f"Warning: deleting {constraint.symbol} will also delete {constraint.parent.symbol}.")
                while True:
                    answer = input("Continue (y/n)? ")
                    if answer in ['y', 'n']:
                        if answer=='n':
                            print("Deletion aborted.")
                            return None
                        break
                
            CM.constraints.pop(constraint.symbol)
            CM.decomposed_constraints.pop(constraint.symbol)
            constraint.parent.children.remove(constraint)
            
            if len(constraint.parent.children)==0:
                CM.constraints.pop(constraint.parent.symbol)
                CM.raw_constraints.pop(constraint.parent.symbol)
                del constraint.parent
            
            del constraint
            
def activateConstraints():
    print("activateConstraints: TODO")
    # Constraints are activated by default
    # ask which constraints to activate
    # R# will activate all children D#
    # D# will activate the corresponding decomposed constraint
        
def deactivateConstraints():
    print("deactivateConstraints: TODO")
    # ask which constraints to deactivate
    # R# will deactivate all children D#
    # D# will deactivate the corresponding decomposed constraint

def planWithConstraints():
    print("planWithConstraints: TODO")   
    # update problem with activated constraints
    # compile problem
    # Solve it

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
        
    # Testing initialized CM
    """
    R0 - never use plane1
        D1 - Person1, person2, person3, and person4 should never be in plane1.
                (always (and (not (in person1 plane1)) (not (in person2 plane1)) (not (in person3 plane1)) (not (in person4 plane1))))
        D2 - Plane1 should remain at its initial location (city1) throughout the plan.
                (always (located plane1 city1))
        D3 - The number of people onboard plane1 should always be zero.
                (always (= (onboard plane1) 0))
        D4 - The fuel level of plane1 should remain unchanged from its initial value.
                (always (= (fuel plane1) 174))
    R5 - plane2 should be in city2 at the end
            D6 - plane2 must be located in city2 in the final state
                (at-end (located plane2 city2))
    """
    r = CM.createRaw("never use plane1")
    d = CM.createDecomposed(r, "Person1, person2, person3, and person4 should never be in plane1.")
    d.encoding = "(always (and (not (in person1 plane1)) (not (in person2 plane1)) (not (in person3 plane1)) (not (in person4 plane1))))"
    d = CM.createDecomposed(r, "Plane1 should remain at its initial location (city1) throughout the plan.")
    d.encoding = "(always (located plane1 city1))"
    d = CM.createDecomposed(r, "The number of people onboard plane1 should always be zero.")
    d.encoding = "(always (= (onboard plane1) 0))"
    d = CM.createDecomposed(r, "The fuel level of plane1 should remain unchanged from its initial value.")
    d.encoding = "(always (= (fuel plane1) 174))"
    r = CM.createRaw("plane2 should be in city2 at the end")
    d = CM.createDecomposed(r, "plane2 must be located in city2 in the final state")
    d.encoding = "(at-end (located plane2 city2))"
    CM.show()
    
    # exit()
    
    while True:
        
        # Show current CM
        CM.show()
        
        # Options
        UO = UserOption()
        UO.addOption("ADD", "Add constraints")
        UO.addOption("DEL", "Delete constraints")
        UO.addOption("ACT", "Activate constraints")
        UO.addOption("DEA", "Deactivate constraints")
        UO.addOption("PLAN", "Plan with constraints")
        user_input = UO.ask()
        
        if "ADD"==user_input:
            addConstraints(domain, problem)
        elif "DEL"==user_input:
            deleteConstraints()
        elif "ACT"==user_input:
            activateConstraints()
        elif "DEA"==user_input:
            deactivateConstraints()
        elif "PLAN"==user_input:
            planWithConstraints()
        
        
    exit()
###########################################################################################################################
###########################################################################################################################
    
    while True:
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
                # update pdsim plan
                # updatePDSimPlan(plan)
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
    sys.argv += ["zeno5_bis"]
    main()