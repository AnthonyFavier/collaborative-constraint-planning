#!/usr/bin/env python3.10
import subprocess
import claude as llm
import tools
from NumericTCORE.bin.ntcore import main as ntcore
import sys
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

PROBLEMS = {
    "Zeno_5":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile5.pddl"),
    "Zeno_5_bis":   ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile5_bis.pddl"),
    "Zeno_8":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile8.pddl"),
    "Zeno_15":      ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile15.pddl"),
    "Zeno_23":      ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile23.pddl"),
    "sailing_1":    ("ENHSP-Public/ijcai18_benchmarks/sailing_ln/domain.pddl",              "ENHSP-Public/ijcai18_benchmarks/sailing_ln/instance_1_1_1229.pddl"),
    "satellite_1":  ("ENHSP-Public/ijcai16_benchmarks/Satellite/Numeric/metricSat.pddl",    "ENHSP-Public/ijcai16_benchmarks/Satellite/Numeric/pfile1"),
    "satellite_3":  ("ENHSP-Public/ijcai16_benchmarks/Satellite/Numeric/metricSat.pddl",    "ENHSP-Public/ijcai16_benchmarks/Satellite/Numeric/pfile3"),
    "satellite_4":  ("ENHSP-Public/ijcai16_benchmarks/Satellite/Numeric/metricSat.pddl",    "ENHSP-Public/ijcai16_benchmarks/Satellite/Numeric/pfile4"),
    "satellite_5":  ("ENHSP-Public/ijcai16_benchmarks/Satellite/Numeric/metricSat.pddl",    "ENHSP-Public/ijcai16_benchmarks/Satellite/Numeric/pfile5"),
    "satellite_15": ("ENHSP-Public/ijcai16_benchmarks/Satellite/Numeric/metricSat.pddl",    "ENHSP-Public/ijcai16_benchmarks/Satellite/Numeric/pfile15"),
    "rover1":       ("ENHSP-Public/ijcai16_benchmarks/Rover-Numeric/NumRover.pddl",         "ENHSP-Public/ijcai16_benchmarks/Rover-Numeric/pfile1"),
    "rover3":       ("ENHSP-Public/ijcai16_benchmarks/Rover-Numeric/NumRover.pddl",         "ENHSP-Public/ijcai16_benchmarks/Rover-Numeric/pfile3"),
    "rover3_bis":   ("ENHSP-Public/ijcai16_benchmarks/Rover-Numeric/NumRover.pddl",         "ENHSP-Public/ijcai16_benchmarks/Rover-Numeric/pfile3_bis"),
    "rover4":       ("ENHSP-Public/ijcai16_benchmarks/Rover-Numeric/NumRover.pddl",         "ENHSP-Public/ijcai16_benchmarks/Rover-Numeric/pfile4"),
    "rover10":      ("ENHSP-Public/ijcai16_benchmarks/Rover-Numeric/NumRover.pddl",         "ENHSP-Public/ijcai16_benchmarks/Rover-Numeric/pfile10"),
    "sar1":         ("ENHSP-Public/handcraft/domain.pddl",                                  "ENHSP-Public/handcraft/pfile1.pddl"),
}

DOMAIN_PATH, PROBLEM_PATH, PLAN_MODE = (*PROBLEMS["Zeno_5_bis"], 'opt')
# DOMAIN_PATH, PROBLEM_PATH, PLAN_MODE = (*PROBLEMS["Zeno_5_bis"], 'def')

COMPILED_DOMAIN_PATH = "tmp/compiled_dom.pddl"
COMPILED_PROBLEM_PATH = "tmp/compiled_prob.pddl"
UPDATED_PROBLEM_PATH = "tmp/updatedProblem.pddl"

NTCORE_STRATEGY = {"naive":"naive", "regression":"regression", "delta":"delta"}
PLAN_MODES = {'sat':'sat-hmrp', 'opt':'opt-hrmax', 'def':'def'}

###
with open(DOMAIN_PATH, "r") as f:
    domain = f.read()
    
with open(PROBLEM_PATH, "r") as f:
    problem = f.read()
###

def plan(domain=COMPILED_DOMAIN_PATH, problem=COMPILED_PROBLEM_PATH, plan_mode=PLAN_MODES['opt']):
    mode = [key for key, val in PLAN_MODES.items() if val == plan_mode][0]
    print(color.BOLD + f"\nPlanning ({mode}) ..." + color.END)
    planner = f'-planner {plan_mode}' if plan_mode!='def' else ''
    result = subprocess.run(
        [f"java -jar ENHSP-Public/enhsp.jar -o {domain} -f {problem} {planner}"], shell=True, capture_output=True, text=True
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
    
    # Show selected problem
    print(f"Problem:\n\t- {DOMAIN_PATH}\n\t- {PROBLEM_PATH}\n")
    
    # Try parsing the initial problem
    try:
        parsed = tools.parse_pddl3(DOMAIN_PATH, PROBLEM_PATH)
    except Exception as e:
        print("ERROR", e)
        raise Exception(f"Unable to parse the initial problem.")

    # Set extracted fluent names (used during verification)
    tools.set_fluent_names([f.name for f in parsed.problem.fluents])
    
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
                encodedPref = llm.encodePrefs(domain, problem, pref)
            else: # re-encoding 
                # input()
                print(color.BOLD + "\nRe-Encoding..." + color.END)
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
                print(color.BOLD + "\nCompiling..." + color.END)
                ntcore(DOMAIN_PATH, UPDATED_PROBLEM_PATH, "tmp/", achiever_strategy=NTCORE_STRATEGY["delta"], verbose=False)
            except Exception as error:
                print(error)
                print("NTCORE: Failed to compile updated problem...")
                feedback = f"There is the following error in the encoding: {error}. Fix it."
                continue
            
            # 5 # Plan using the compiled problem
            feedback = plan(plan_mode=PLAN_MODES[PLAN_MODE])
            # print initial input and encoding
            print('\n"' + pref + '"' + filteredEncoding)
            success = feedback=='success'
            if success:
                break
            
        
        if not success:
            print("Failure: Maximum attempts reached unsuccessfully...")
            print('\n"' + pref + '"')
            
        
        llm.clear_message_history()
        print('\n=======================')
        print('=======================\n')



if __name__ == '__main__':

    # Main interactive loop (w/o arguments)
    if len(sys.argv)==1:
        main()
        
    # Only planning (w/ arguments)
    else:
        try:
            files_arg = {'ori': (DOMAIN_PATH, PROBLEM_PATH), 'comp': (COMPILED_DOMAIN_PATH, COMPILED_PROBLEM_PATH)}
            d = files_arg[sys.argv[1]][0]
            p = files_arg[sys.argv[1]][1]
            pm = PLAN_MODES[sys.argv[2]]
        except:
            print('Usage:\n  - python main.py: run interactive loop\n  - python main.py [ori, comp] [opt, sat, def]\n\tori: plan using original files\n\tcomp: plan using the compiled files\n\topti: plan in optimal mode\n\tsat: plan in satisficing mode\n\tdef: plan in default satisficing mode')
            exit()
            
        # Show selected problem
        print(f"Problem:\n\t- {DOMAIN_PATH}\n\t- {PROBLEM_PATH}\n")
        plan(domain=d, problem=p, plan_mode=pm)
        