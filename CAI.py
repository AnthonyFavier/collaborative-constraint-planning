import sys
import LLM
import tools
from NumericTCORE.bin.ntcore import main as ntcore
import click
from planner import planner
from defs import *
from updatePDSimPlan import main as updatePDSimPlan
import Constraints
from UserOption import UserOption
        
CM = Constraints.ConstraintManager()


def addConstraintsAsk():
    nl_constraints = []
    while True:
        if not len(nl_constraints):
            mprint(color.BOLD + "\nEnter your first constraint:\n> " + color.END, end="")
        else:
            mprint(color.BOLD + "\nPress Enter to validate or type another constraint:\n> " + color.END, end="")
            
        t = input()
        if t=="":
            break
        else:
            nl_constraints.append(t)
            
    addConstraints(nl_constraints)
def addConstraints(nl_constraints):
    new_r = []
    for nl_constraint in nl_constraints:
        r = CM.createRaw(nl_constraint)
        new_r.append(r)
        
        mprint(color.BOLD + "\nDecomposing constraints..." + color.END)
        result = LLM.decompose(g_domain, g_problem, nl_constraint)
        result = LLM.removeFormating(result)
        
        # for c in constraints:
        for c in result.splitlines():
            CM.createDecomposed(r, c)
        
        mprint(r.strWithChildren())
        
        # input("is ok?")
        
        # TODO: Ask if decomposition ok?
        # otherwise retry
        # Different options: retry, with comment?, delete this constraint, replace this constraint
    
    # When all ok, encode the decomposed of all new r
    
    # Encoding
    mprint(color.BOLD + "\nEncoding..." + color.END)
    r_to_delete = []
    for r in new_r:
        for c in r.children:
            encodingOK = False
            MAX_ENCODING_TRY = 5
            i=0
            while not encodingOK and i<MAX_ENCODING_TRY:
                
                # 1 # Encode the preferences
                if i==0: # first time
                    mprint(f"\tencoding {c.symbol}...")
                    encodedPref = LLM.encodePrefs(g_domain, g_problem, c.nl_constraint)
                else: # Re-encoding
                    mprint(f"\tre-encoding {c.symbol}...")
                    encodedPref = LLM.reencodePrefs(feedback)
                filteredEncoding = tools.filterEncoding(encodedPref)
                filteredEncoding = tools.initialFixes(filteredEncoding)
                # mprint(filteredEncoding)
                    
                # 2 # Update the problem and verify the encoding
                    # If error, re-encode with feedback
                updatedProblem = tools.updateProblem(g_problem, [filteredEncoding])
                encodingOK, feedback = tools.verifyEncoding(updatedProblem, g_domain, filteredEncoding)
                if encodingOK:
                    c.encoding = filteredEncoding
                    LLM.clear_message_history()
                else:
                    mprint("\t\tVerifier: Encoding not OK.")
                    # mprint(feedback)
                i+=1
            
            if not encodingOK:
                mprint(f"Failure: Maximum attempts reached to encode {c.symbol} of {r.symbol}... {r.symbol} will be deleted")
                r_to_delete.append(r.symbol)
    
    if len(r_to_delete):
        deleteConstraints(r_to_delete)
                
            
def deleteConstraintsAsk():
    loop = True
    while loop:
        loop = False
        constraint_symbols = input("Which constraints you want to delete? (type symbol, separated by commas or space, leave empty to cancel)\n> ")
        if constraint_symbols=='':
            print("Deletion aborted.")
            return None
        
        constraint_symbols = " ".join(constraint_symbols.split(',')).upper()
        constraint_symbols = constraint_symbols.split()
        for c in constraint_symbols:
            if not c in CM.constraints:
                print("One or more constraints not recognized.\n")
                loop = True
                break
    
    print('\n' + ", ".join(constraint_symbols) + " will be deleted.")
    while True:
        answer = input("Confirm (y/n)? ")
        if answer in ['y', 'n']:
            if answer=='n':
                print("Deletion aborted.")
                return None
            break
        
    deleteConstraints(constraint_symbols)
def deleteConstraints(constraint_symbols):
    # if R# remove raw constraint and all decomposed associated
    # if D# remove only decompose from general list and from parent children
    
    # Deletion
    for symbol in constraint_symbols:
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
    # Constraints are activated by default
    # ask which constraints to activate
    # R# will activate all children D#
    # D# will activate the corresponding decomposed constraint
    
    loop = True
    while loop:
        loop = False
        x = input("Which constraints you want to activate? (type symbol, separated by commas or space, leave empty to cancel)\n> ")
        if x=='':
            print("Activation aborted.")
            return None
        
        x = " ".join(x.split(',')).upper()
        x = x.split()
        for c in x:
            if not c in CM.constraints:
                print("One or more constraints not recognized.\n")
                loop = True
                break
    
    # Activation
    for symbol in x:
        CM.constraints[symbol].activate()
        
def deactivateConstraints():
    # ask which constraints to deactivate
    # R# will deactivate all children D#
    # D# will deactivate the corresponding decomposed constraint
    
    loop = True
    while loop:
        loop = False
        x = input("Which constraints you want to deactivate? (type symbol, separated by commas or space, leave empty to cancel)\n> ")
        if x=='':
            print("Deactivation aborted.")
            return None
        
        x = " ".join(x.split(',')).upper()
        x = x.split()
        for c in x:
            if not c in CM.constraints:
                print("One or more constraints not recognized.\n")
                loop = True
                break
    
    # Deactivation
    for symbol in x:
        CM.constraints[symbol].deactivate()

def planWithConstraints():
    # get activated constraints
    # update problem with activated constraints
    # compile problem
    # Solve it
    
    # Get activated constraints
    activated_encodings = []
    for k,c in CM.decomposed_constraints.items():
        if c.isActivated():
            activated_encodings.append(c.encoding)
        
    if not len(activated_encodings):
        mprint("\nNo active constraints: Planning without constraints")
        problem_name = g_problem_name
    
    else:
        problem_name = PlanFiles.COMPILED
        
        updatedProblem = tools.updateProblem(g_problem, activated_encodings)
        
        # Save updated problem in a file
        with open(UPDATED_PROBLEM_PATH, "w") as f:
            f.write(updatedProblem)
        
        # Compile the updated problem
        mprint(color.BOLD + "\nCompiling..." + color.END)
        ntcore(DOMAIN_PATH, UPDATED_PROBLEM_PATH, "tmp/", achiever_strategy=NtcoreStrategy.DELTA, verbose=False)
        
    # Plan
    feedback, plan = planner(problem_name, plan_mode=g_planning_mode)
    success = feedback=='success'
    if success:
        mprint("\nSuccessful planning")
        return plan
    else:
        mprint("\nFailed to plan")
        return "Failed to plan:\n" + str(feedback)
def askChangePlanMode():
    print(f"Current planning mode: {g_planning_mode}")
    print(f"Select a planning mode:\n\t1 - {PlanMode.DEFAULT}\n\t2 - {PlanMode.OPTIMAL}\n\t3 - {PlanMode.SATISFICING}")
    c = input("> ")
    if c!='':
        # Check if correct
        if c in ['1', '2', '3']:
            if c=='1':
                g_planning_mode=PlanMode.DEFAULT
            if c=='2':
                g_planning_mode=PlanMode.OPTIMAL
            if c=='3':
                g_planning_mode=PlanMode.SATISFICING
            
            print(f"\nPlanning mode set to: {g_planning_mode}")
        else:
            print("Incorrect input")
            print("Aborted\n")
    else:
        print("Aborted\n")
        
g_last_plan = None
def CAI():
    global g_last_plan
    
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
        UO.addOption("CHANGEPLANMODE", "Change planning mode")
        UO.addOption("UPDATESIM", "Update Sim")
        user_input = UO.ask()
        
        if "ADD"==user_input:
            addConstraintsAsk()
        elif "DEL"==user_input:
            deleteConstraintsAsk()
        elif "ACT"==user_input:
            activateConstraints()
        elif "DEA"==user_input:
            deactivateConstraints()
        elif "PLAN"==user_input:
            g_last_plan = planWithConstraints()
        elif "CHANGEPLANMODE"==user_input:
            askChangePlanMode()
        elif "UPDATESIM"==user_input:
            if g_last_plan!= None and g_last_plan.find("Failed to plan:")!=-1:
                updatePDSimPlan(g_last_plan)
            else:
                mprint("No current valid plan")

def init(problem_name, planning_mode):
    global g_problem_name, g_domain, g_problem, g_planning_mode
    global DOMAIN_PATH, PROBLEM_PATH
    
    if not problem_name in PROBLEMS:
        click.echo("Unknown problem.\n" + KNOWN_PROBLEMS_STR)
        exit()
    
    g_problem_name = problem_name
    DOMAIN_PATH, PROBLEM_PATH = PROBLEMS[g_problem_name]
    g_planning_mode = planning_mode
    
    # Show selected problem
    mprint(f"Planning mode: {planning_mode}\nProblem ({problem_name}):\n\t- {DOMAIN_PATH}\n\t- {PROBLEM_PATH}")
    
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
        g_domain = f.read()
    with open(PROBLEM_PATH, "r") as f:
        g_problem = f.read()

@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name')
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, default=True, help="Set the planning mode to 'Default' (default)")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, help="Set the planning mode to 'Optimal'")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
def main(problem_name, planning_mode):
    init(problem_name, planning_mode)
    CAI()
if __name__ == '__main__':
    main()