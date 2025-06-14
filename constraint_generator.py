from unified_planning.io import PDDLReader, PDDLWriter
import unified_planning 
from unified_planning.shortcuts import *
from defs import *
import random
from NumericTCORE.bin.ntcore import main as ntcore
from planner import planner

import typing
from unified_planning.model.problem import Problem as upProblem
from unified_planning.model.fluent import Fluent as upFluent
from unified_planning.model.parameter import Parameter as upParameter
from unified_planning.model.types import _RealType as upReal
from unified_planning.model.types import _BoolType as upBool

dp = '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl' # type: str
pp = '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile13.pddl'

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

reader = PDDLReader()
original_problem: upProblem = reader.parse_problem(dp, pp) 

# Generates NB_CONSTRAINT constraints, each forcing random grounded fluents to always keep their initial value
# Generates NB_CONSTRAINT_AND2 constraints by combining pairs of random previous constraints with And
# Generates NB_CONSTRAINT_AND3 constraints by combining three random previous constraints with And
# Generates NB_CONSTRAINT_OR2 constraints by combining pairs of random previous constraints with Or
# Generates NB_CONSTRAINT_OR3 constraints by combining three random previous constraints with Or

# SEED
seed = random.randrange(sys.maxsize)
random.seed(seed)
random.seed(0)

from datetime import datetime
date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
filename = f'expe_constraints_{date}.txt'
with open(filename, 'w') as f:
    f.write(f"domain:\n{dp}\nproblem:\n{pp}\n")
    f.write(f"seed:\n{seed}\n\n")


changing_fluents = []
for f in original_problem.fluents:
    if not f.name in ['distance', 'slow-burn', 'fast-burn', 'capacity', 'zoom-limit']:
        changing_fluents.append(f)

expressions = []

NB_CONSTRAINT = 20
constraints = []
for i in range(NB_CONSTRAINT):
    fluent:upFluent = pickRandom(changing_fluents)
    
    objects = []
    for p in fluent.signature:
        p:upParameter
        valid_objects = list(original_problem.objects(p.type))
        objects.append(pickRandom(valid_objects))
        
    print(fluent(*objects))

    if isinstance(fluent.type, upReal):
        initial_value = original_problem.initial_values[fluent(*objects)]
        exp = Equals(fluent(*objects), initial_value)
    elif isinstance(fluent.type, upBool):
        initial_value = original_problem.initial_values[fluent(*objects)]
        if initial_value:
            exp = fluent(*objects)
        else:
            exp = Not(fluent(*objects))
    
    expressions.append(exp)
    constraint = Always(exp)
    constraints.append(constraint)
print('\nConstraints:')
for c in constraints:
    print('\t', c)
    
NB_CONSTRAINT_AND2 = 20
constraints_AND2 = []
for i in range(NB_CONSTRAINT_AND2):
    e1, e2 = pick2Random(expressions)
    constraint = Always(And(e1, e2))
    constraints_AND2.append(constraint)
print('\nAND2 Constraints:')
for c in constraints_AND2:
    print('\t', c)
    
NB_CONSTRAINT_AND3 = 20
constraints_AND3 = []
for i in range(NB_CONSTRAINT_AND3):
    e1, e2, e3 = pick3Random(expressions)
    constraint = Always(And(e1, e2, e3))
    constraints_AND3.append(constraint)
print('\nAND3 Constraints:')
for c in constraints_AND3:
    print('\t', c)
    
NB_CONSTRAINT_OR2 = 20
constraints_OR2 = []
for i in range(NB_CONSTRAINT_OR2):
    e1, e2 = pick2Random(expressions)
    constraint = Always(Or(e1, e2))
    constraints_OR2.append(constraint)
print('\nOR2 Constraints:')
for c in constraints_OR2:
    print('\t', c)
        
NB_CONSTRAINT_OR3 = 20
constraints_OR3 = []
for i in range(NB_CONSTRAINT_OR3):
    e1, e2, e3 = pick3Random(expressions)
    constraint = Always(Or(e1, e2, e3))
    constraints_OR3.append(constraint)
print('\nOR2 Constraints:')
for c in constraints_OR3:
    print('\t', c)


with open(filename, 'a') as f:
    f.write(f"Generated constraints:\n")
    f.write( f"\nSIMPLE:\n" )
    f.write( '\n'.join( [str(c) for c in constraints] )+'\n' )
    f.write( f"\nAND2:\n" )
    f.write( '\n'.join( [str(c) for c in constraints_AND2] )+'\n' )
    f.write( f"\nAND3:\n" )
    f.write( '\n'.join( [str(c) for c in constraints_AND3] )+'\n' )
    f.write( f"\nOR2:\n" )
    f.write( '\n'.join( [str(c) for c in constraints_OR2] )+'\n' )
    f.write( f"\nOR3:\n" )
    f.write( '\n'.join( [str(c) for c in constraints_OR3] )+'\n' )
    
N_TEST = 2
for i in range(N_TEST):
    # Pick a constraint from all set and create updated problem
    c = pickRandom(constraints + constraints_AND2 + constraints_AND3 + constraints_OR2 + constraints_OR3)
    print("\nConstraint: ", c)
    new_problem = original_problem.clone()
    new_problem.add_trajectory_constraint(c)
    with open(filename, 'a') as f:
        f.write(f"\nConstraint={c}\n")

    # Write new problem with up
    w = PDDLWriter(new_problem)
    w.write_domain('tmp/updated_domain.pddl')
    w.write_problem('tmp/updated_problem.pddl')

    # Compile
    print("Compiling:")
    ntcore('tmp/updated_domain.pddl', 'tmp/updated_problem.pddl', "tmp/", achiever_strategy=NtcoreStrategy.DELTA, verbose=False)
    print("Compiled")

    # Plan
    print("Planning:")
    feedback, plan, stdout = planner(PlanFiles.COMPILED, plan_mode=PlanMode.DEFAULT, hide_plan=False, timeout=3)
    print("Planned")

    # Get Metric
    if feedback=='success':
        i1_metric = plan.find('Metric (Search):')+len('Metric (Search):')
        i2_metric = plan.find('\n', i1_metric)
        metric = float(plan[i1_metric:i2_metric])
        print(metric)
        with open(filename, 'a') as f:
            f.write(f"\nPlan:\n")
            f.write(f"{feedback}\n")
            f.write(f"{plan}\n")
            f.write(f"metric={metric}\n")
            
    else:
        print("failed")
        with open(filename, 'a') as f:
            f.write(f"\nPlan:\n")
            f.write(f"{feedback}:\n")
