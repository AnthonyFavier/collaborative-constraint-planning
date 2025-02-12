#!/usr/bin/env python3.10
import subprocess
import claude as llm
import tools
from NumericTCORE.bin.ntcore import main as ntcore
import sys


PROBLEMS = {
    "Zeno_5" : ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl", "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile5.pddl"),
    "Zeno_8" : ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl", "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile8.pddl"),
    "Zeno_23" : ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl", "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile23.pddl"),
}

DOMAIN_PATH, PROBLEM_PATH = PROBLEMS["Zeno_5"]

COMPILED_DOMAIN_PATH = "tmp/compiled_dom.pddl"
COMPILED_PROBLEM_PATH = "tmp/compiled_prob.pddl"
UPDATED_PROBLEM_PATH = "tmp/updatedProblem.pddl"

NTCORE_STRATEGY = {"naive":"naive", "regression":"regression", "delta":"delta"}
PLAN_MODE = {'sat':'sat-hmrp', 'opt':'opt-hrmax'}

###
with open(DOMAIN_PATH, "r") as f:
    domain = f.read()
    
with open(PROBLEM_PATH, "r") as f:
    problem = f.read()
###

def plan(domain=COMPILED_DOMAIN_PATH, problem=COMPILED_PROBLEM_PATH, plan_mode=PLAN_MODE['opt']):
    mode = [key for key, val in PLAN_MODE.items() if val == plan_mode][0]
    print(f"\nPlanning ({mode}) ...")
    result = subprocess.run(
        [f"java -jar ENHSP-Public/enhsp.jar -o {domain} -f {problem} -planner {plan_mode}"], shell=True, capture_output=True, text=True
    )
    result = result.stdout.splitlines()
    
    try: # if successful
        # print plan
        for l in result[result.index('Found Plan:'):]:
            print(l)
        # stop loop
        feedback = "success"
    
    except:
        print('Unsolvable Problem')
        feedback = f"The encoding made the problem unsolvable. Fix it."
        
    return feedback

def main():
    
    # Try parsing the initial problem
    try:
        tools.parse_pddl3(DOMAIN_PATH, PROBLEM_PATH)
    except:
        raise Exception(f"Unable to parse the initial problem described in:\n\t- {DOMAIN_PATH}\n\t- {PROBLEM_PATH}")
    
    while True:
        
        #  User Strategy to test
        print("Enter your preferences:\n")
        pref = input()
        if pref=="exit":
            exit()
        
        success = False
        MAX_ENCODING_TRY = 5
        for i in range(MAX_ENCODING_TRY):
            
            # 1 # Encode the preferences
            if i==0: # first time
                print("\nEncoding...")
                encodedPref = llm.encodePrefs(domain, problem, pref)
            else: # re-encoding 
                # input()
                print("\nRe-Encoding...")
                encodedPref = llm.reencodePrefs(feedback)
                
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
                print("\nCompiling...")
                ntcore(DOMAIN_PATH, UPDATED_PROBLEM_PATH, "tmp/", achiever_strategy=NTCORE_STRATEGY["delta"], verbose=False)
            except Exception as error:
                print(error)
                print("NTCORE: Failed to compile updated problem...")
                feedback = f"There is the following error in the encoding: {error}. Fix it."
                continue
            
            # 5 # Plan using the compiled problem
            feedback = plan()
            # print initial input and encoding
            print('\n"' + pref + '"' + filteredEncoding)
            success = feedback=='success'
            if success:
                break
            
        
        if not success:
            print("Failure: Maximum attempts reached unsuccessfully...")
        
        llm.clear_message_history()
        print('\n=======================')
        print('=======================\n')



if __name__ == '__main__':
    if len(sys.argv)>1:
        try:
            files_arg = {'ori': (DOMAIN_PATH, PROBLEM_PATH), 'comp': (COMPILED_DOMAIN_PATH, COMPILED_PROBLEM_PATH)}
            plan(domain=files_arg[sys.argv[1]][0], problem=files_arg[sys.argv[1]][1], plan_mode=PLAN_MODE[sys.argv[2]])
            exit()
        except:
            print('Usage:\n  - python main.py: run interactive loop\n  - python main.py [ori, comp] [opt, sat]\n\tori: plan using original files\n\tcomp: plan using the compiled files\n\topti: plan in optimal mode\n\tsat: plan in satisficing mode')
            exit()
        
    main()