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
from datetime import datetime

import typing
from unified_planning.model.problem import Problem as upProblem
from unified_planning.model.fluent import Fluent as upFluent
from unified_planning.model.parameter import Parameter as upParameter
from unified_planning.model.types import _RealType as upReal
from unified_planning.model.types import _BoolType as upBool

    
dp = '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl' # type: str
pp = '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile13.pddl'

###################################

NB_EXPRESSION =         50
NB_CONSTRAINT_SIMPLE =  NB_EXPRESSION
NB_CONSTRAINT_AND2 =    NB_EXPRESSION
NB_CONSTRAINT_AND3 =    NB_EXPRESSION
NB_CONSTRAINT_OR2 =     NB_EXPRESSION
NB_CONSTRAINT_OR3 =     NB_EXPRESSION
NB_TEST = 200
TIMEOUT = 5

run_name = f"{NB_EXPRESSION}-{NB_TEST}-TO{TIMEOUT}"
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

##########################
## GENERATE CONSTRAINTS ##
##########################
def generate_constraints(original_problem):
    # Select only changing fluents (not constants)
    changing_fluents = []
    for f in original_problem.fluents:
        if not f.name in ['distance', 'slow-burn', 'fast-burn', 'capacity', 'zoom-limit']:
            changing_fluents.append(f)
            
    # EXPRESSIONS
    expressions = []
    for i in range(NB_EXPRESSION):
        keep_picking = True
        n_retry = 0
        while keep_picking:
            # pick random changing fluent
            fluent:upFluent = pickRandom(changing_fluents)
            
            # randomly ground fluent
            objects = []
            for p in fluent.signature:
                p:upParameter
                valid_objects = list(original_problem.objects(p.type))
                objects.append(pickRandom(valid_objects))
            grounded_fluent = fluent(*objects)
            
            # make expression with initial value
            if isinstance(grounded_fluent.type, upReal):
                initial_value = original_problem.initial_values[grounded_fluent]
                exp = Equals(grounded_fluent, initial_value)
            elif isinstance(grounded_fluent.type, upBool):
                initial_value = original_problem.initial_values[grounded_fluent]
                if initial_value.constant_value():
                    exp = grounded_fluent
                else:
                    exp = Not(grounded_fluent)
                    
            # check if already present, if so retry until new 
            if not exp in expressions:
                keep_picking = False
                expressions.append(exp)
            
            # If too many retry, stop to avoid infite loop in case already picked all possibilities
            else:
                n_retry+=1
                if n_retry==100:
                    raise Exception("EXPRESSION: Too many retry to pick expression: Probably already picked all...")
    
    constraints_dict = {}
    
    # SIMPLE
    constraints_SIMPLE = []
    for i in range(NB_CONSTRAINT_SIMPLE):
        keep_picking = True
        n_retry = 0
        while keep_picking:
            exp = pickRandom(expressions)
            constraint = Always(exp)
            if not constraint in constraints_SIMPLE:
                keep_picking = False
                constraints_SIMPLE.append(constraint)
            else:
                n_retry+=1
                if n_retry==100:
                    raise Exception("SIMPLE: Too many retry to pick expression: Probably already picked all...")
    constraints_dict['SIMPLE'] = constraints_SIMPLE
         
    # AND2   
    constraints_AND2 = []
    for i in range(NB_CONSTRAINT_AND2):
        keep_picking = True
        n_retry = 0
        while keep_picking:
            e1, e2 = pick2Random(expressions)
            constraint = Always(And(e1, e2))
            if not constraint in constraints_AND2:
                keep_picking = False
                constraints_AND2.append(constraint)
            else:
                n_retry+=1
                if n_retry==100:
                    raise Exception("AND2: Too many retry to pick expression: Probably already picked all...")
    constraints_dict['AND2'] = constraints_AND2
             
    # AND3
    constraints_AND3 = []
    for i in range(NB_CONSTRAINT_AND3):
        keep_picking = True
        n_retry = 0
        while keep_picking:
            e1, e2, e3 = pick3Random(expressions)
            constraint = Always(And(e1, e2, e3))
            if not constraint in constraints_AND3:
                keep_picking = False
                constraints_AND3.append(constraint)
            else:
                n_retry+=1
                if n_retry==100:
                    raise Exception("AND3: Too many retry to pick expression: Probably already picked all...")
    constraints_dict['AND3'] = constraints_AND3
    
    # OR2    
    constraints_OR2 = []
    for i in range(NB_CONSTRAINT_OR2):
        keep_picking = True
        n_retry = 0
        while keep_picking:
            e1, e2 = pick2Random(expressions)
            constraint = Always(Or(e1, e2))
            if not constraint in constraints_OR2:
                keep_picking = False
                constraints_OR2.append(constraint)
            else:
                n_retry+=1
                if n_retry==100:
                    raise Exception("OR2: Too many retry to pick expression: Probably already picked all...")
    constraints_dict['OR2'] = constraints_OR2
    
    # OR3                
    constraints_OR3 = []
    for i in range(NB_CONSTRAINT_OR3):
        keep_picking = True
        n_retry = 0
        while keep_picking:
            e1, e2, e3 = pick3Random(expressions)
            constraint = Always(Or(e1, e2, e3))
            if not constraint in constraints_OR3:
                keep_picking = False
                constraints_OR3.append(constraint)
            else:
                n_retry+=1
                if n_retry==100:
                    raise Exception("OR3: Too many retry to pick expression: Probably already picked all...")
    constraints_dict['OR3'] = constraints_OR3
    
    return expressions, constraints_dict

class MyIterator:
    def __init__(self, d):
        self.names = [n for n in d]
        self.lists = [d[n] for n in d]
    def __iter__(self):
        self.i = 0
        return self
    def __next__(self):
        n = self.names[self.i]
        l = self.lists[self.i]
        self.i+=1
        if self.i==len(self.names):
            self.i=0
        return n,l

##########
## MAIN ##
##########

def main():
    # Parse original problem
    reader = PDDLReader()
    original_problem: upProblem = reader.parse_problem(dp, pp) 

    # Check if original problem has no constraints
    if original_problem.trajectory_constraints!=[]:
        raise Exception('Already some constraints in original problem')

    # Initialize random seed
    seed = random.randrange(sys.maxsize)
    seed = 0 # for testing
    random.seed(seed)

    # Create result file
    result = {}
    result['seed'] = seed
    result['timeout'] = TIMEOUT
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'{run_name}_{date}.json'
    path = 'results_constraints/'
    result['domain'] = dp
    result['problem'] = pp
    with open(path+filename, 'w') as f:
        f.write(json.dumps(result, indent=4))

    # Generate constraints
    expressions, constraints_dict = generate_constraints(original_problem)
    result['generated_constraints'] = {'EXPRESSIONS': [str(e) for e in expressions]}
    for k,l in constraints_dict.items():
        result['generated_constraints'][k] = [str(c) for c in l]
    with open(path+filename, 'w') as f:
        f.write(json.dumps(result, indent=4))

    # Tests
    result['tests'] = []
    itType = iter(MyIterator(constraints_dict))
    with IncrementalBar('Processsing', max=NB_TEST, suffix = '%(percent).1f%% - ETA %(eta_td)s') as bar:
        for i in range(NB_TEST):
            
            bar.start()
            test = {}
            
            # Get current type and pickRandom of this type
            type_name, type_list = next(itType)
            picked_constraint = pickRandom(type_list)
            while str(picked_constraint) in [t['constraint'] for t in result['tests']]:
                picked_constraint = pickRandom(type_list)
            test['constraint'] = str(picked_constraint)
            test['constraint_type'] = type_name
                
            result['tests'].append(test)
            test['result'] = 'In progress...'
            with open(path+filename, 'w') as f:
                f.write(json.dumps(result, indent=4))
            
            # Update problem with constraint
            new_problem = original_problem.clone()
            new_problem.add_trajectory_constraint(picked_constraint)

            # Write new problem with up
            problem_name = filename.replace('.json', '')
            w = PDDLWriter(new_problem)
            w.write_domain(f'tmp/{problem_name}_updated_domain.pddl')
            w.write_problem(f'tmp/{problem_name}_updated_problem.pddl')

            # Compile
            ntcore(f'tmp/{problem_name}_updated_domain.pddl', f'tmp/{problem_name}_updated_problem.pddl', "tmp/", filename=problem_name, achiever_strategy=NtcoreStrategy.DELTA, verbose=False)

            # Plan
            PROBLEMS[problem_name] = (f"tmp/{problem_name}_compiled_dom.pddl", f"tmp/{problem_name}_compiled_prob.pddl")
            feedback, plan, stdout = planner(problem_name, plan_mode=PlanMode.ANYTIME, hide_plan=True, timeout=TIMEOUT)

            # Get Metric
            if feedback=='success':
                i1_metric = plan.find('Metric (Search):')+len('Metric (Search):')
                i2_metric = plan.find('\n', i1_metric)
                metric = float(plan[i1_metric:i2_metric])
                
                test['result'] = 'success'
                test['plan'] = plan
                test['metric'] = metric
            else:
                test['result'] = 'failed'
                if stdout.find('Unsolvable Problem')!=-1:
                    reason = 'Unsolvable Problem'
                else:
                    reason = 'Timeout'
                test['reason'] = reason
                
            with open(path+filename, 'w') as f:
                f.write(json.dumps(result, indent=4))
                
            bar.next()
    
        result['elapsed'] = str(bar.elapsed_td)
        with open(path+filename, 'w') as f:
            f.write(json.dumps(result, indent=4))
        
if __name__=="__main__":
    
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C detected. Exiting...")
        # Kill ENHSP java process
        for proc in psutil.process_iter():
            if proc.name() == "java":
                proc.kill()
