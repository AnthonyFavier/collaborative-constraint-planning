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
import threading
        
CM = Constraints.ConstraintManager()

# ABLATION_FLAGS #
WITH_VERIFIER = True
WITH_DECOMP = True
ASK_DECOMP_FEEDBACK = True
WITH_CHECK_DOMAIN_MODIFICATION = False

DUMP_CM = True
MAX_ENCODING_TRY = 3

## ADD CONSTRAINT ##
def createConstraint(nl_constraint, input_time=0):
    r = CM.createRaw(nl_constraint)
    r.time_input = input_time
    return r

def decompose(r):
    mprint("\n== Decomposition ==")
    initialDecomposition(r)
    feedback = decompInteraction(r)
    if 'abort'==feedback: raise Exception('abort')
    while 'OK'!=feedback:
        r = reDecomposition(r, feedback)
        feedback = decompInteraction(r)

def encode(r):
    initialEncoding(r)
    for d in r.children:
        feedback = encodingInteraction(d)
        if 'abort'==feedback: raise Exception('abort')
        while 'OK'!=feedback:
            encodeDecomposed(d, feedback, reencode_e2nl=True)
            feedback = encodingInteraction(d)
    
## DECOMPOSE ##
def initialDecomposition(r):
    if WITH_DECOMP:
        r.decomp_conv = LLM.ConversationHistory()
        
        t1 = time.time()
        startTimer()
        mprint("\nDecomposing: " + str(r) + " ... ", end="")
        constraints, explanation = LLM.decompose(r.nl_constraint, r.decomp_conv)
        t2 = time.time()
        stopTimer()
        r.time_decomp = t2-t1
        mprint(f"OK [{r.time_decomp:.2f}s]")
            
        for c in constraints.splitlines():
            CM.createDecomposed(r, c)
        mprint(f'Explanation: "{explanation}"')
        mprint(r.strChildren())
            
        if WITH_CHECK_DOMAIN_MODIFICATION:
            mprint("Checking if worth to do modifications...")
            result = LLM.needModifications()
            mprint(result)
            
    elif not WITH_DECOMP:
        # create only decomposed constraint similar to raw constraint
        CM.createDecomposed(r, r.nl_constraint)
        r.time_decomp = 0
        
def decompInteraction(r):
    if ASK_DECOMP_FEEDBACK:
        time_validation = time.time()
        answer = minput("Press Enter or give feedback: ")
        if answer=='':
            mprint("OK")
        elif 'abort'==answer:
            CM.deleteConstraints( [r.symbol] )
            return 'abort'
        else:
            mprint("\n> " + answer)
        
        r.time_validation += time.time() - time_validation
        decompOK = answer==''
        if not decompOK:
            ## Re-decompose with user feedback
            return answer
    return 'OK'

def reDecomposition(r, feedback):
    # Re-decompose constraint according to user feedback
    
    time_redecomp = time.time()
    startTimer()
    
    # delete previous children
    CM.deleteChildren(r)
    
    # reset global constraint ID constraint
    Constraints.Constraint._ID = int(r.symbol[1:])+1
    
    mprint("\nRe-Decomposing: " + str(r) + " ... ", end="")
    constraints, explanation = LLM.redecompose("Decompose again the constraint while considering the following: " + feedback, r.decomp_conv)
    stopTimer()
    r.time_redecomp += time.time()-time_redecomp
    mprint(f"OK [{r.time_redecomp:.2f}s]")
                
    for c in constraints.splitlines():
        CM.createDecomposed(r, c)
    mprint(f'Explanation: "{explanation}"')
    mprint(r.strChildren())
            
    # created constraint (RawConstraint)
    return r

## ENCODING ##

def initialEncoding(r):
    
    # Encoding
    mprint("\n== Encoding ==")
    
    mprint("\n" + str(r))
    
    reset_counters(len(r.children))
    showEncodingStatus(newline=True)
    
    # THREADING ENCODING
    startTimer()
    t_encoding = time.time()
    threads = []
    for d in r.children:
        t = threading.Thread(target=encodeDecomposed, args=[d])
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    t2 = time.time()
    stopTimer()
    
    t_encoding = time.time() - t_encoding
    r.time_initial_encoding = t_encoding
    mprint(f"\nEncoding done [{r.time_initial_encoding:.2f}s]")

def encodeDecomposed(d, feedback=None, reencode_e2nl=False):
    print('start encoding of ', d)
    
    if feedback==None:
        d.encoding_conv = LLM.ConversationHistory()
    
    encodingOK = False
    i=0
    while not encodingOK and i<MAX_ENCODING_TRY:
        if i==0 and feedback==None:
            time_encoding = time.time()
            encoding = LLM.encodePrefs(d.nl_constraint, d.encoding_conv)
            d.time_encoding = time.time()-time_encoding
        else:
            time_reencoding = time.time()
            encoding = LLM.reencodePrefs(feedback, d.encoding_conv)
            if not reencode_e2nl:
                d.time_reencoding = time.time()-time_reencoding
            else:
                d.time_e2nl_reencoding = time.time()-time_reencoding
        encoding = tools.initialFixes(encoding)
        
        # VERIFIER
        if WITH_VERIFIER:
            time_verifier = time.time()
            updatedProblem = tools.updateProblem(g_problem, [encoding])
            result = tools.verifyEncoding(updatedProblem, g_domain, encoding)
            d.time_verifier = time.time()-time_verifier
            encodingOK = result=='OK'
            if encodingOK:
                d.encoding = encoding
                if g_with_e2nl:
                    time_e2nl = time.time()
                    d.e2nl = LLM.E2NL(d.encoding)
                    d.time_e2nl = time.time()-time_e2nl
                    increase_e2nl_done()
                
            elif not encodingOK:
                d.encoding = ''
                increase_encoding_retry()
                feedback = result
                d.nb_retries += 1
                
        elif not WITH_VERIFIER:
            encodingOK = True
            d.encoding = encoding
            
    
    if encodingOK:
        increase_encoding_done()
    if not encodingOK:
        increase_encoding_failed()
    
    print('end encoding of ', d)

def encodingInteraction(d):
    # show decomposed nl + succes or failed + nb retry 
    mprint(f"\n{d}")
    status = "Encoded" if d.encoding!='' else "Failed"
    retries = f"Retries:{d.nb_retries}/{MAX_ENCODING_TRY-1}"
    mprint(f"\t{status} - {retries}")

    # E2NL
    if g_with_e2nl:
        time_validation = time.time()
        mprint(f'E2NL: "{d.e2nl}"')
        mprint("\nDoes this back-translation sounds correct?")
        answer = minput("Press Enter for yes or give feedback: ")
        if answer=="":
            mprint('OK')
        elif 'abort'==answer:
            CM.deleteConstraints(d.parent)
            return 'abort'
        else:
            mprint("\n> " + answer + '\n')
        
        d.time_validation = time.time()-time_validation
        e2nlOK = answer==''
        if not e2nlOK:
            return answer
    
    return 'OK'
    

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
        
        updatedProblem = tools.updateProblem(g_problem, activated_encodings)
        
        # Save updated problem in a file
        with open(UPDATED_PROBLEM_PATH, "w") as f:
            f.write(updatedProblem)
        
        # Compile the updated problem
        mprint("\nCompiling ... ", end="")
        time_compilation = time.time()
        ntcore(DOMAIN_PATH, UPDATED_PROBLEM_PATH, "tmp/", achiever_strategy=NtcoreStrategy.DELTA, verbose=False)
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
def suggestions():
    mprint("\nElaborating strategies suggestions...")
    mprint(LLM.suggestions())

## INIT ##
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

########################
### HELPERS ENCODING ###
########################

def reset_counters(n):
    global nb_to_encode
    nb_to_encode = n
    reset_encoding_done()
    reset_encoding_failed()
    reset_encoding_retry()
    reset_nb_e2nl_done()
    
nb_to_encode = 0
nb_encoding_done = 0
nb_encoding_done_lock = threading.Lock()
def increase_encoding_done():
    global nb_encoding_done
    nb_encoding_done_lock.acquire()
    nb_encoding_done += 1
    showEncodingStatus()
    nb_encoding_done_lock.release()
def reset_encoding_done():
    global nb_encoding_done
    nb_encoding_done_lock.acquire()
    nb_encoding_done = 0 
    nb_encoding_done_lock.release()
    
nb_encoding_failed = 0
nb_encoding_failed_lock = threading.Lock()
def increase_encoding_failed():
    global nb_encoding_failed
    nb_encoding_failed_lock.acquire()
    nb_encoding_failed += 1
    showEncodingStatus()
    nb_encoding_failed_lock.release()
def reset_encoding_failed():
    global nb_encoding_failed
    nb_encoding_failed_lock.acquire()
    nb_encoding_failed = 0 
    nb_encoding_failed_lock.release()
    
nb_encoding_retry = 0
nb_encoding_retry_lock = threading.Lock()
def increase_encoding_retry():
    global nb_encoding_retry
    nb_encoding_retry_lock.acquire()
    nb_encoding_retry += 1
    showEncodingStatus()
    nb_encoding_retry_lock.release()
def reset_encoding_retry():
    global nb_encoding_retry
    nb_encoding_retry_lock.acquire()
    nb_encoding_retry = 0 
    nb_encoding_retry_lock.release()    
    
nb_e2nl_done = 0
nb_e2nl_done_lock = threading.Lock()
def increase_e2nl_done():
    global nb_e2nl_done
    nb_e2nl_done_lock.acquire()
    nb_e2nl_done += 1
    showEncodingStatus()
    nb_e2nl_done_lock.release()
def reset_nb_e2nl_done():
    global nb_e2nl_done
    nb_e2nl_done_lock.acquire()
    nb_e2nl_done = 0 
    nb_e2nl_done_lock.release()

def showEncodingStatus(newline=False):
    f = mprint if newline else mrprint
    e2nl_txt = f" - E2NL:{nb_e2nl_done}/{nb_to_encode}" if g_with_e2nl else ""
    f(f"In progress... done:{nb_encoding_done}/{nb_to_encode} - retries:{nb_encoding_retry} - failed:{nb_encoding_failed}{e2nl_txt}", end="")

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