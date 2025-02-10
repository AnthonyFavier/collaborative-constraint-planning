#!/usr/bin/env python3.10
import subprocess
from claude import encodePrefs, reencodePrefs, clear_message_history
from tools import verifyEncoding, updateProblem, filterEncoding, initialFixes
from NumericTCORE.bin.ntcore import main as ntcore

###
DOMAIN_FILE = "NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl"
PROBLEM_FILE = "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile5.pddl"
###

COMPILED_DOMAIN_FILE = "tmp/compiled_dom.pddl"
COMPILED_PROBLEM_FILE = "tmp/compiled_prob.pddl"
UPDATED_PROBLEM_FILE = "tmp/updatedProblem.pddl"

NTCORE_STRATEGY = {"naive":"naive", "regression":"regression", "delta":"delta"}
PLAN_MODE = {'sat':'sat-hmrp', 'opt':'opt-hrmax'}

###
with open(DOMAIN_FILE, "r") as f:
    domain = f.read()
    
with open(PROBLEM_FILE, "r") as f:
    problem = f.read()
###

while True:
    
    #  User Strategy to test
    print("Enter your preferences:\n")
    pref = input()
    if pref=="exit":
        exit()
    # pref="If plane1 visits city1 then it should visit city2 sometime after"
    # print(pref)
    # input("Press Return to validate...")
    
    # Preferences should be given incrementally if possible? 
    # Only one big sentence, LLM tends to forget parts of it.......
    
    success = False
    MAX_ENCODING_TRY = 5
    for i in range(MAX_ENCODING_TRY):
        
        # 1 # Encode the preferences
        if i==0: # first time
            print("\nEncoding...")
            encodedPref = encodePrefs(domain, problem, pref)
        else: # re-encoding 
            # input()
            print("\nRe-Encoding...")
            encodedPref = reencodePrefs(feedback)
            
        # 2 # Update the problem and verify the encoding
            # If error, re-encode with feedback
        filteredEncoding = filterEncoding(encodedPref)
        filteredEncoding = initialFixes(filteredEncoding)
        print(filteredEncoding)
        updatedProblem = updateProblem(problem, filteredEncoding)
        encodingOK, feedback = verifyEncoding(updatedProblem, filteredEncoding)
        if not encodingOK:
            print("Verifier: Encoding not OK")
            print(feedback)
            continue
        
        # 3 # Save updated problem in a file
        with open(UPDATED_PROBLEM_FILE, "w") as f:
            f.write(updatedProblem)

        # 4 # Compile the updated problem
            # If error, re-encode
        try:
            print("\nCompiling...")
            ntcore(DOMAIN_FILE, UPDATED_PROBLEM_FILE, "tmp/", achiever_strategy=NTCORE_STRATEGY["delta"], verbose=False)
        except Exception as error:
            print(error)
            print("NTCORE: Failed to compile updated problem...")
            feedback = f"There is the following error in the encoding: {error}. Fix it."
            continue
        
        # 5 # Plan using the compiled problem
            # add -planner option, opti (opt-hrmax) or satisficing (sat-hmrp) ?
        print("\nPlanning...")
        result = subprocess.run(
            [f"java -jar ENHSP-Public/enhsp.jar -o {COMPILED_DOMAIN_FILE} -f {COMPILED_PROBLEM_FILE} -planner {PLAN_MODE['opt']}"], shell=True, capture_output=True, text=True
        )
        result = result.stdout.splitlines()
        if result[-1] == 'Unsolvable Problem':
            print('Unsolvable Problem')
            feedback = f"The encoding made the problem unsolvable. Fix it."
            continue
        
        for l in result[result.index('Found Plan:'):]:
            print(l)
        
        success = True 
        print('\n"' + pref + '"' + filteredEncoding)
        break
    
    if not success:
        print("Failure: Maximum tries reached unsuccessfully...")
    
    clear_message_history()
    print('\n=======================')
    print('=======================\n')