import LLM
import tools
from NumericTCORE.bin.ntcore import main as ntcore
import click
from planner import planner
from defs import *
from updatePDSimPlan import main as updatePDSimPlan
import Constraints
from helpers.UserOption import UserOption
import time
        
CM = Constraints.ConstraintManager()

# ABLATION_FLAGS #
WITH_VERIFIER = True
WITH_DECOMP = True
ASK_DECOMP_FEEDBACK = True
WITH_CHECK_DOMAIN_MODIFICATION = False

DUMP_CM = True
MAX_ENCODING_TRY = 3

def addConstraints(nl_constraints):
    for nl_constraint in nl_constraints:
        addConstraint(nl_constraint)
        
def addConstraint(nl_constraint):
    t1 = time.time()
    
    # Decomposition
    new_c, abort = decomposeConstraint(nl_constraint)
    if abort: return None
    
    # Encoding
    abort = encodeConstraint(new_c)
    if abort: return None
        
    t2 = time.time()
    mprint(f"\nTranslation time: {t2-t1:.2f} s")
    
    CM.dump()
    
def decomposeConstraint(nl_constraint):
    if WITH_DECOMP:
        # Regular decomposition
        mprint("\n== Decomposition ==")
        
        decompOK = False
        first_attempt = True
        while not decompOK:
            
            r = CM.createRaw(nl_constraint)
            
            if first_attempt:
                mprint("\nDecomposing: " + str(r) + " ... ")
                constraints, explanation = LLM.decompose(nl_constraint)
            else:
                mprint("\nRe-Decomposing: " + str(r) + " ... ")
                constraints, explanation = LLM.redecompose("Decompose again the constraint while considering the following: " + feedback)
                
            # for c in constraints:
            for c in constraints.splitlines():
                CM.createDecomposed(r, c)
            
            mprint(f'Explanation: "{explanation}"')
            mprint(r.strChildren())
            
            if WITH_CHECK_DOMAIN_MODIFICATION:
                mprint("Checking if worth to do modifications...")
                result = LLM.needModifications()
                mprint(result)
            
            if ASK_DECOMP_FEEDBACK:
                answer = minput("Press Enter or give feedback: ")
                if answer=='':
                    mprint("OK")
                elif 'abort'==answer:
                    LLM.clear_message_history()
                    CM.deleteConstraints( [r.symbol] )
                    return None, True
                else:
                    mprint("\n> " + answer)
                    
                decompOK = answer==''
                if not decompOK:
                    ## Re-decompose with user feedback
                    # reset Constraint ID
                    id = r.symbol[1:]
                    Constraints.Constraint._ID = int(id)
                    # delete created constraint
                    CM.deleteConstraints([r.symbol])
                    del r
                    feedback = answer
                    
            first_attempt = False
            
        LLM.clear_message_history
            
    elif not WITH_DECOMP:
        # create only decomposed constraint similar to raw constraint
        r = CM.createRaw(nl_constraint)
        CM.createDecomposed(r, nl_constraint)
        
    # created constraint (RawConstraint), process aborted (bool)
    return r, False

def encodeConstraint(r):
    # Encoding
    mprint("\n== Encoding ==")
    
    mprint("\n" + str(r))
    
    for c in r.children:
        encodingOK = False
        i=0
        while not encodingOK and i<MAX_ENCODING_TRY:
            
            # 1 # Encode the preferences
            if i==0: # first time
                mprint(f"\tEncoding {c} ... ", end="")
                encodedPref = LLM.encodePrefs(c.nl_constraint)
            else: # Re-encoding
                mprint(f"\t\tRe-encoding (try {i+1}/{MAX_ENCODING_TRY}) ... ", end="")
                encodedPref = LLM.reencodePrefs(feedback)
            filteredEncoding = encodedPref
            filteredEncoding = tools.initialFixes(filteredEncoding)
                
            # 2 # Update the problem
            updatedProblem = tools.updateProblem(g_problem, [filteredEncoding])
            
            # VERIFIER
            if WITH_VERIFIER:
                encodingOK, feedback = tools.verifyEncoding(updatedProblem, g_domain, filteredEncoding)
                if encodingOK:
                    mprint(f"OK")
                    c.encoding = filteredEncoding
                    
                    if g_with_e2nl:
                        # Generate back translation
                        mprint("E2NL: ", end="")
                        c.e2nl = LLM.E2NL(c.encoding)
                        mprint(f'"{c.e2nl}"')
                        
                        # Asking for feedback
                        mprint("Does this back-translation match the constraint?")
                        answer = minput("Press Enter for yes or give feedback: ")
                        if answer=="":
                            mprint("OK")
                        elif 'abort'== answer:
                            LLM.clear_message_history()
                            CM.deleteConstraints(r)
                            return True
                        else:
                            mprint("\n\t> " + answer)
                        
                        e2nlOK = answer==''
                        if not e2nlOK:
                            # Re-encoding with human feedback
                            c.encoding = ''
                            feedback = "There is an issue with the encoding. Try again considering the following feedback: " + answer
                            i=-1
                    
                elif not encodingOK:
                    # Re-encoding with verifier's feedback
                    mprint("Verifier failed")
                    c.encoding = ''
                    
            elif not WITH_VERIFIER:
                mprint(f"OK")
                encodingOK = True
                c.encoding = filteredEncoding
                
            i+=1
            
        LLM.clear_message_history()
        
        if not encodingOK:
            mprint(f"\n\t\tFailure: Maximum attempts reached to encode {c.symbol}... {c.symbol} will be deleted")
    
    CM.clean()
    
    # process aborted (bool)
    return False

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
    
    else:
        problem_name = PlanFiles.COMPILED
        
        updatedProblem = tools.updateProblem(g_problem, activated_encodings)
        
        # Save updated problem in a file
        with open(UPDATED_PROBLEM_PATH, "w") as f:
            f.write(updatedProblem)
        
        # Compile the updated problem
        mprint("\nCompiling ... ", end="")
        ntcore(DOMAIN_PATH, UPDATED_PROBLEM_PATH, "tmp/", achiever_strategy=NtcoreStrategy.DELTA, verbose=False)
        mprint("OK")
        
    # Plan
    mprint(f"Planning ({g_planning_mode}{'' if g_timeout==None else f', TO={g_timeout}s'}) ... ", end="" )
    feedback, plan, stdout = planner(problem_name, plan_mode=g_planning_mode, hide_plan=True, timeout=g_timeout)
    success = feedback=='success'
    if success:
        mprint("OK")
        return plan
    else:
        mprint("Failed")
        return "Failed to plan:\n" + str(feedback)

def suggestions():
    mprint("\nElaborating strategies suggestions...")
    mprint(LLM.suggestions())

g_with_e2nl = False
def init(problem_name, planning_mode, timeout):
    global g_problem_name, g_domain, g_problem, g_planning_mode, g_timeout
    global DOMAIN_PATH, PROBLEM_PATH
    
    if not problem_name in PROBLEMS:
        click.echo("Unknown problem.\n" + KNOWN_PROBLEMS_STR)
        exit()
        
    g_problem_name = problem_name
    DOMAIN_PATH, PROBLEM_PATH = PROBLEMS[g_problem_name]
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
            mprint('WARNING: Timeout disabled with Anytime planning mode!')
    timeout_str = f', TO={g_timeout}' if g_timeout!=None else ''
    
    # Show selected problem
    mprint(f"Planning mode: {planning_mode}{timeout_str}\nProblem ({problem_name}):\n\t- {DOMAIN_PATH}\n\t- {PROBLEM_PATH}")
    
    # Try parsing the initial problem
    try:
        parsed = tools.parse_pddl3(DOMAIN_PATH, PROBLEM_PATH)
    except Exception as e:
        print("ERROR", e)
        raise Exception(f"Unable to parse the initial problem.")
    
    # Check if no initial constraints
    if parsed.problem.trajectory_constraints!=[]:
        raise Exception(f"There are already constraints in the initial problem.\n{parsed.problem.trajectory_constraints}")

    # Set extracted fluent names (used during verification)
    tools.set_fluent_names([f.name for f in parsed.problem.fluents])
    typed_objects = {}
    objects = []
    for o in parsed.problem.all_objects:
        objects.append(o.name)
        if o.type.name in objects:
            typed_objects[o.type.name].append(o.name)
        else:
            typed_objects[o.type.name] = [o.name]
    tools.set_all_objects(objects)
    tools.set_typed_objects(typed_objects)
    
    # Open initial problem
    with open(DOMAIN_PATH, "r") as f:
        g_domain = f.read()
    with open(PROBLEM_PATH, "r") as f:
        g_problem = f.read()
        
    # Init LLM system message with domain and problem
    LLM.setSystemMessage(g_domain, g_problem)



#################################################################
########### TEXT ONLY BELOW, WITHOUT GUI [DEPRECATED] ###########
#################################################################

def askAddConstraints():
    nl_constraints = []
    while True:
        if not len(nl_constraints):
            mprint("\nEnter your first constraint:\n> ", end="")
        else:
            mprint("\nPress Enter to validate or type another constraint:\n> ", end="")
            
        t = input()
        if t=="":
            break
        else:
            nl_constraints.append(t)
            
    return nl_constraints

def askDeleteConstraints():
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
        
    CM.deleteConstraints(constraint_symbols)

def askChangePlanMode():
    print(f"Current planning mode: {g_planning_mode}")
    mprint(f"Select a planning mode:\n\t1 - {PlanMode.ANYTIME}\n\t2 - {PlanMode.ANYTIMEAUTO}\n\t3 - {PlanMode.DEFAULT}\n\t4 - {PlanMode.OPTIMAL}\n\t5 - {PlanMode.SATISFICING}")
    c = input("> ")
    if c!='':
        # Check if correct
        if c in ['1', '2', '3', '4', '5']:
            if c=='1':
                CAI.g_planning_mode=PlanMode.ANYTIME
            if c=='2':
                CAI.g_planning_mode=PlanMode.ANYTIMEAUTO
            if c=='3':
                CAI.g_planning_mode=PlanMode.DEFAULT
            if c=='4':
                CAI.g_planning_mode=PlanMode.OPTIMAL
            if c=='5':
                CAI.g_planning_mode=PlanMode.SATISFICING
            
            print(f"\nPlanning mode set to: {g_planning_mode}")
        else:
            print("Incorrect input")
            print("Aborted\n")
    else:
        print("Aborted\n")

def askActivateConstraints():
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
        
def askDeactivateConstraints():
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
            constraints = askAddConstraints()
            addConstraints(constraints)
        elif "DEL"==user_input:
            CM.askDeleteConstraints()
        elif "ACT"==user_input:
            askActivateConstraints()
        elif "DEA"==user_input:
            askDeactivateConstraints()
        elif "PLAN"==user_input:
            g_last_plan = planWithConstraints()
        elif "CHANGEPLANMODE"==user_input:
            askChangePlanMode()
        elif "UPDATESIM"==user_input:
            if g_last_plan!= None and g_last_plan.find("Failed to plan:")!=-1:
                updatePDSimPlan(g_last_plan)
            else:
                mprint("No current valid plan")

@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name')
@click.option('-a', '--anytime', 'planning_mode', flag_value=PlanMode.ANYTIME, default=True, help="Set the planning mode to 'Anytime' (default)")
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, help="Set the planning mode to 'Optimal'")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('-t', '--timeout', 'timeout', default=10.0, help="Timeout for planning")
def main(problem_name, planning_mode, timeout):
    init(problem_name, planning_mode, timeout)
    CAI()
if __name__ == '__main__':
    main()