from unified_planning.io import PDDLReader, PDDLWriter
import unified_planning 
from unified_planning.shortcuts import *
from defs import *
import random
from NumericTCORE.bin.ntcore import main as ntcore
from planner import planner
import json
from progress.bar import IncrementalBar
import psutil

import typing
from unified_planning.model.problem import Problem as upProblem
from unified_planning.model.fluent import Fluent as upFluent
from unified_planning.model.parameter import Parameter as upParameter
from unified_planning.model.types import _RealType as upReal
from unified_planning.model.types import _BoolType as upBool

    
dp = '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl' # type: str
pp = '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile13.pddl'

###################################

NB_CONSTRAINT =         50
NB_CONSTRAINT_AND2 =    50
NB_CONSTRAINT_AND3 =    50
NB_CONSTRAINT_OR2 =     50
NB_CONSTRAINT_OR3 =     50
NB_TEST = 200
TIMEOUT = 10

run_name = f"{NB_CONSTRAINT}-{NB_TEST}-TO{TIMEOUT}"
print(run_name)

###################################

def pickRandomNotAlready(l, already):
    if set(l)==set(already):
        raise Exception("pickRandomNotAlready: already picked all elements...")
    x = pickRandom(l)
    while x in already:
        x = pickRandom(l)
    return x

def pickRandom(l):
    return l[random.randint(0, len(l)-1)]

def pick2Random(l):
    i1 = random.randint(0, len(l)-1)
    i2 = random.randint(0, len(l)-1)
    while i2==i1: i2 = random.randint(0, len(l)-1)
    return l[i1], l[i2]

def pick3Random(l):
    i1 = random.randint(0, len(l)-1)
    i2 = random.randint(0, len(l)-1)
    while i2==i1: i2 = random.randint(0, len(l)-1)
    i3 = random.randint(0, len(l)-1)
    while i3==i1 or i3==i2: i3 = random.randint(0, len(l)-1)
    return l[i1], l[i2], l[i3]

##########
## MAIN ##
##########

def main():
    reader = PDDLReader()
    original_problem: upProblem = reader.parse_problem(dp, pp) 

    if original_problem.trajectory_constraints!=[]:
        raise Exception('Already some constraints in original problem')

    # Generates NB_CONSTRAINT constraints, each forcing random grounded fluents to always keep their initial value
    # Generates NB_CONSTRAINT_AND2 constraints by combining pairs of random previous constraints with And
    # Generates NB_CONSTRAINT_AND3 constraints by combining three random previous constraints with And
    # Generates NB_CONSTRAINT_OR2 constraints by combining pairs of random previous constraints with Or
    # Generates NB_CONSTRAINT_OR3 constraints by combining three random previous constraints with Or

    result = {}

    # SEED
    seed = random.randrange(sys.maxsize)
    seed = 0
    random.seed(seed)
    result['seed'] = seed

    result['timeout'] = TIMEOUT

    from datetime import datetime
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'{run_name}_{date}.json'
    result['domain'] = dp
    result['problem'] = pp
    with open(filename, 'w') as f:
        f.write(json.dumps(result, indent=4))

    changing_fluents = []
    for f in original_problem.fluents:
        if not f.name in ['distance', 'slow-burn', 'fast-burn', 'capacity', 'zoom-limit']:
            changing_fluents.append(f)
            
    expressions = []

    constraints_SIMPLE = []
    picked = []
    for i in range(NB_CONSTRAINT):
        fluent:upFluent = pickRandomNotAlready(changing_fluents, picked)
        picked.append(fluent)
        
        objects = []
        for p in fluent.signature:
            p:upParameter
            valid_objects = list(original_problem.objects(p.type))
            objects.append(pickRandom(valid_objects))
            
        # print(fluent(*objects))

        if isinstance(fluent.type, upReal):
            initial_value = original_problem.initial_values[fluent(*objects)]
            exp = Equals(fluent(*objects), initial_value)
        elif isinstance(fluent.type, upBool):
            initial_value = original_problem.initial_values[fluent(*objects)]
            if initial_value.constant_value():
                exp = fluent(*objects)
            else:
                exp = Not(fluent(*objects))
        
        expressions.append(exp)
        constraint = Always(exp)
        constraints_SIMPLE.append(constraint)
        
    constraints_AND2 = []
    for i in range(NB_CONSTRAINT_AND2):
        e1, e2 = pick2Random(expressions)
        constraint = Always(And(e1, e2))
        constraints_AND2.append(constraint)
        
    constraints_AND3 = []
    for i in range(NB_CONSTRAINT_AND3):
        e1, e2, e3 = pick3Random(expressions)
        constraint = Always(And(e1, e2, e3))
        constraints_AND3.append(constraint)
        
    constraints_OR2 = []
    for i in range(NB_CONSTRAINT_OR2):
        e1, e2 = pick2Random(expressions)
        constraint = Always(Or(e1, e2))
        constraints_OR2.append(constraint)
            
    constraints_OR3 = []
    for i in range(NB_CONSTRAINT_OR3):
        e1, e2, e3 = pick3Random(expressions)
        constraint = Always(Or(e1, e2, e3))
        constraints_OR3.append(constraint)


    result['generated_constraints'] = {
        'EXPRESSIONS': [str(e) for e in expressions],
        'SIMPLE': [str(c) for c in constraints_SIMPLE],
        'AND2': [str(c) for c in constraints_AND2],
        'AND3': [str(c) for c in constraints_AND3],
        'OR2': [str(c) for c in constraints_OR2],
        'OR3': [str(c) for c in constraints_OR3],
    }
    
    all_constraints = constraints_SIMPLE+constraints_AND2+constraints_AND3+constraints_OR2+constraints_OR3
    my_dict = {x:all_constraints.count(x) for x in all_constraints}
    print("repeated constraints:")
    repeated = 0
    for k,n in my_dict.items():
        if n>1:
            print(f'\t{n}: {k}')
            repeated+=1

    with open(filename, 'w') as f:
        f.write(json.dumps(result, indent=4))

    result['tests'] = []
    with IncrementalBar('Processsing', max=NB_TEST, suffix = '%(percent).1f%% - ETA %(eta_td)s') as bar:
        for i in range(NB_TEST):
            # print(f'\nTEST {i+1}/{NB_TEST}')
            bar.start()
            test = {}
            
            # Pick a constraint from all set
            picked_constrait = pickRandomNotAlready(constraints_SIMPLE+constraints_AND2+constraints_AND3+constraints_OR2+constraints_OR3, [t['constraint'] for t in result['tests']])
            test['constraint'] = str(picked_constrait)
            if picked_constrait in constraints_SIMPLE:
                test['constraint_type'] = 'SIMPLE'
            elif picked_constrait in constraints_AND2:
                test['constraint_type'] = 'AND2'
            elif picked_constrait in constraints_AND3:
                test['constraint_type'] = 'AND3'
            elif picked_constrait in constraints_OR2:
                test['constraint_type'] = 'OR2'
            elif picked_constrait in constraints_OR3:
                test['constraint_type'] = 'O3'
                
            
            
            result['tests'].append(test)
            with open(filename, 'w') as f:
                f.write(json.dumps(result, indent=4))
            
            # Update problem with constraint
            new_problem = original_problem.clone()
            new_problem.add_trajectory_constraint(c)

            # Write new problem with up
            w = PDDLWriter(new_problem)
            w.write_domain('tmp/updated_domain.pddl')
            w.write_problem('tmp/updated_problem.pddl')

            # Compile
            # print("Compiling ... ", end='', flush=True)
            ntcore('tmp/updated_domain.pddl', 'tmp/updated_problem.pddl', "tmp/", achiever_strategy=NtcoreStrategy.DELTA, verbose=False)
            # print("OK")

            # Plan
            # print("Planning ... ", end='', flush=True)
            feedback, plan, stdout = planner(PlanFiles.COMPILED, plan_mode=PlanMode.ANYTIME, hide_plan=True, timeout=TIMEOUT)

            # Get Metric
            if feedback=='success':
                # print('Success')
                i1_metric = plan.find('Metric (Search):')+len('Metric (Search):')
                i2_metric = plan.find('\n', i1_metric)
                metric = float(plan[i1_metric:i2_metric])
                # print('Metric: ', metric)
                
                test['result'] = 'success'
                test['plan'] = plan
                test['metric'] = metric
            else:
                # print('Failed')
                test['result'] = 'failed'
                if stdout.find('Unsolvable Problem'):
                    reason = 'Unsolvable Problem'
                else:
                    reason = 'Timeout'
                test['reason'] = reason
                # print('Reason: ', reason)
                
            with open(filename, 'w') as f:
                f.write(json.dumps(result, indent=4))
                
            bar.next()
    
if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C detected. Exiting...")
        # Kill ENHSP java process
        for proc in psutil.process_iter():
            if proc.name() == "java":
                proc.kill()
