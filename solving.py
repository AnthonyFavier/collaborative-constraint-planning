import click
from unified_planning.io import PDDLReader, PDDLWriter
import unified_planning 
from unified_planning.shortcuts import *
from defs import *
import random
from NumericTCORE.bin.ntcore import main as ntcore
from planner import planner
import json
from progress.bar import IncrementalBar
from datetime import datetime

import typing
from unified_planning.model.problem import Problem as upProblem
from unified_planning.model.fluent import Fluent as upFluent
from unified_planning.model.parameter import Parameter as upParameter
from unified_planning.model.types import _RealType as upReal
from unified_planning.model.types import _BoolType as upBool
import itertools
import time

######################
## HYPER PARAMETERS ##
######################

PROBLEM_NAME = 'Rover8_n_t'
# ZenoTravel13, Rover13, Rover8_n, Rover8_n_t, Rover10_n_t, ZenoTravel7, ZenoTravel10, Woodworking7

NB_EXPRESSION =         10
NB_CONSTRAINT_SIMPLE =  NB_EXPRESSION
NB_CONSTRAINT_AND2 =    NB_EXPRESSION
NB_CONSTRAINT_AND3 =    NB_EXPRESSION
NB_CONSTRAINT_OR2 =     NB_EXPRESSION
NB_CONSTRAINT_OR3 =     NB_EXPRESSION
NB_TEST = NB_EXPRESSION*5 # Should be less or equal than NB_EXPRESSION * 5 to avoid redundant constraints

NB_WO = 10

SEED = random.randrange(sys.maxsize)
SEED = 0 # for testing
# 0, 2902480765646109827, 6671597656599831408
random.seed(SEED)

MAX_RETRY_PICK = 300

#######################
## HUMAN CONSTRAINTS ##
#######################

def initializeHumanConstraintsZenotravel13(pb):
    constraints_dict = {"SIMPLE":[]}
    
    # ONLY USE PLANE1
    p = Variable('p', pb.user_type('person'))
    constraint = Always(And(
        Forall(Not(pb.fluent('in')(p, pb.object('plane2'))), p),
        Forall(Not(pb.fluent('in')(p, pb.object('plane3'))), p),
        pb.fluent('located')(pb.object('plane2'), pb.object('city2')),
        pb.fluent('located')(pb.object('plane3'), pb.object('city3')),
    ))
    duration = 2.615387201309204 + 16.52852725982666 + 13.851156949996948 + 10.916101217269897 + 16.49752712249756   
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    # PERSON7 SHOULD NOT MOVE
    constraint = Always(pb.fluent('located')(pb.object('person7'), pb.object('city0')))
    duration = 5.320336818695068 + 14.295466423034668 + 1.1159181594848633 + 0 + 42.560056924819946
    constraints_dict['SIMPLE'].append((constraint, duration))


    # PLANES SHOULD ONLY FLY SLOWLY
    a = Variable('a', pb.user_type('aircraft'))
    c1 = Variable('c1', pb.user_type('city'))
    c2 = Variable('c2', pb.user_type('city'))
    constraint = Always(Forall( Equals(pb.fluent('n_flyfast')(a, c1, c2), 0) , a, c1, c2))
    duration = 10.133426904678345 + 13.860996961593628 + 4.325040340423584 + 0 + 13.88686227798462
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    # PLANE1 SHOULD NEVER FLY TO A SAME CITY MORE THAN 3 TIMES
    constraint = Always(Forall(LE(Plus(
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city0'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city1'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city2'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city3'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city4'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city5'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city0'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city1'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city2'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city3'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city4'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city5'), c1),
        ),3), c1))
    duration = 8.530399799346924 + 16.361482858657837 + 8.234846830368042 + 0 + 34.751404762268066
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    
    # PERSON1 AND PERSON3 SHOULD TRAVEL TOGETHER
    constraint = Always(Or(
        Exists(And( pb.fluent('in')(pb.object('person1'), a), pb.fluent('in')(pb.object('person3'), a) ), a),
        Exists(And( pb.fluent('located')(pb.object('person1'), c1), pb.fluent('located')(pb.object('person3'), c1) ), c1),
        Exists(And( pb.fluent('in')(pb.object('person1'), a), pb.fluent('located')(pb.object('person3'), c1), pb.fluent('located')(a, c1)), c1, a),
        Exists(And( pb.fluent('in')(pb.object('person3'), a), pb.fluent('located')(pb.object('person1'), c1), pb.fluent('located')(a, c1)), c1, a),
    ))
    duration = 90.0
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    constraints_dict['AND'] = []
    for i in range(2, len(constraints_dict['SIMPLE'])+1):
        for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
            constraints = [c[0] for c in x]
            times = [c[1] for c in x]
            constraints_dict['AND'].append( (And(constraints), sum(times)) )
    
    # constraints_dict['OR'] = []
    # for i in range(2, len(constraints_dict['SIMPLE'])+1):
    #     for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
    #         constraints_dict['OR'].append( Or(x) )
    
    return constraints_dict

def initializeHumanConstraintsZenotravel7(pb):
    constraints_dict = {"SIMPLE":[]}

    # PERSON2 SHOULD NOT MOVE
    constraint = Always(pb.fluent('located')(pb.object('person2'), pb.object('city3')))
    duration = 0.0
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    # PERSON3 SHOULD NOT MOVE
    constraint = Always(pb.fluent('located')(pb.object('person3'), pb.object('city3')))
    duration = 0.0
    constraints_dict['SIMPLE'].append((constraint, duration))


    # PLANES SHOULD ONLY FLY SLOWLY
    a = Variable('a', pb.user_type('aircraft'))
    c1 = Variable('c1', pb.user_type('city'))
    c2 = Variable('c2', pb.user_type('city'))
    constraint = Always(Forall( Equals(pb.fluent('n_flyfast')(a, c1, c2), 0) , a, c1, c2))
    duration = 0.0
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    # PLANE1 SHOULD NEVER FLY TO A SAME CITY MORE THAN 3 TIMES
    constraint = Always(Forall(LE(Plus(
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city0'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city1'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city2'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city3'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city0'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city1'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city2'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city3'), c1),
        ),3), c1))
    duration = 0.0
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    # PLANE2 SHOULD NEVER FLY TO A SAME CITY MORE THAN 3 TIMES
    constraint = Always(Forall(LE(Plus(
        pb.fluent('n_flyslow')(pb.object('plane2'), pb.object('city0'), c1),
        pb.fluent('n_flyslow')(pb.object('plane2'), pb.object('city1'), c1),
        pb.fluent('n_flyslow')(pb.object('plane2'), pb.object('city2'), c1),
        pb.fluent('n_flyslow')(pb.object('plane2'), pb.object('city3'), c1),
        pb.fluent('n_flyfast')(pb.object('plane2'), pb.object('city0'), c1),
        pb.fluent('n_flyfast')(pb.object('plane2'), pb.object('city1'), c1),
        pb.fluent('n_flyfast')(pb.object('plane2'), pb.object('city2'), c1),
        pb.fluent('n_flyfast')(pb.object('plane2'), pb.object('city3'), c1),
        ),3), c1))
    duration = 0.0
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    constraints_dict['AND'] = []
    for i in range(2, len(constraints_dict['SIMPLE'])+1):
        for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
            constraints = [c[0] for c in x]
            times = [c[1] for c in x]
            constraints_dict['AND'].append( (And(constraints), sum(times)) )
    
    return constraints_dict

def initializeHumanConstraintsZenotravel10(pb):
    
    constraints_dict = {"SIMPLE":[]}
    
    # PLANES SHOULD ONLY FLY SLOWLY
    a = Variable('a', pb.user_type('aircraft'))
    c1 = Variable('c1', pb.user_type('city'))
    c2 = Variable('c2', pb.user_type('city'))
    constraint = Always(Forall( Equals(pb.fluent('n_flyfast')(a, c1, c2), 0) , a, c1, c2))
    constraints_dict['SIMPLE'].append(constraint)
    
    # PLANE1 SHOULD NEVER FLY TO A SAME CITY MORE THAN 3 TIMES
    constraint = Always(Forall(LE(Plus(
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city0'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city1'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city2'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city3'), c1),
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city4'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city0'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city1'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city2'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city3'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city4'), c1),
        ),3), c1))
    constraints_dict['SIMPLE'].append(constraint)
    
    # PLANE2 SHOULD NEVER FLY TO A SAME CITY MORE THAN 3 TIMES
    constraint = Always(Forall(LE(Plus(
        pb.fluent('n_flyslow')(pb.object('plane2'), pb.object('city0'), c1),
        pb.fluent('n_flyslow')(pb.object('plane2'), pb.object('city1'), c1),
        pb.fluent('n_flyslow')(pb.object('plane2'), pb.object('city2'), c1),
        pb.fluent('n_flyslow')(pb.object('plane2'), pb.object('city3'), c1),
        pb.fluent('n_flyslow')(pb.object('plane2'), pb.object('city4'), c1),
        pb.fluent('n_flyfast')(pb.object('plane2'), pb.object('city0'), c1),
        pb.fluent('n_flyfast')(pb.object('plane2'), pb.object('city1'), c1),
        pb.fluent('n_flyfast')(pb.object('plane2'), pb.object('city2'), c1),
        pb.fluent('n_flyfast')(pb.object('plane2'), pb.object('city3'), c1),
        pb.fluent('n_flyfast')(pb.object('plane2'), pb.object('city4'), c1),
        ),3), c1))
    constraints_dict['SIMPLE'].append(constraint)
    
    # PLANE3 SHOULD NEVER FLY TO A SAME CITY MORE THAN 3 TIMES
    constraint = Always(Forall(LE(Plus(
        pb.fluent('n_flyslow')(pb.object('plane3'), pb.object('city0'), c1),
        pb.fluent('n_flyslow')(pb.object('plane3'), pb.object('city1'), c1),
        pb.fluent('n_flyslow')(pb.object('plane3'), pb.object('city2'), c1),
        pb.fluent('n_flyslow')(pb.object('plane3'), pb.object('city3'), c1),
        pb.fluent('n_flyslow')(pb.object('plane3'), pb.object('city4'), c1),
        pb.fluent('n_flyfast')(pb.object('plane3'), pb.object('city0'), c1),
        pb.fluent('n_flyfast')(pb.object('plane3'), pb.object('city1'), c1),
        pb.fluent('n_flyfast')(pb.object('plane3'), pb.object('city2'), c1),
        pb.fluent('n_flyfast')(pb.object('plane3'), pb.object('city3'), c1),
        pb.fluent('n_flyfast')(pb.object('plane3'), pb.object('city4'), c1),
        ),3), c1))
    constraints_dict['SIMPLE'].append(constraint)
    
    # PERSON6 AND PERSON8 SHOULD TRAVEL TOGETHER
    constraint = Always(Or(
        Exists(And( pb.fluent('in')(pb.object('person6'), a), pb.fluent('in')(pb.object('person8'), a) ), a),
        Exists(And( pb.fluent('located')(pb.object('person6'), c1), pb.fluent('located')(pb.object('person8'), c1) ), c1),
        Exists(And( pb.fluent('in')(pb.object('person6'), a), pb.fluent('located')(pb.object('person8'), c1), pb.fluent('located')(a, c1)), c1, a),
        Exists(And( pb.fluent('in')(pb.object('person8'), a), pb.fluent('located')(pb.object('person6'), c1), pb.fluent('located')(a, c1)), c1, a),
    ))
    constraints_dict['SIMPLE'].append(constraint)
    
    constraints_dict['AND'] = []
    for i in range(2, len(constraints_dict['SIMPLE'])+1):
        for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
            constraints_dict['AND'].append( And(x) )
            
    return constraints_dict

def initializeHumanConstraintsRover13(pb):
    constraints_dict = {}
    return constraints_dict

def initializeHumanConstraintsRover8n(pb):
    constraints_dict = {'SIMPLE':[]}
    
    # ENERGY NEVER DROPS BELOW 16
    r = Variable('r', pb.user_type('rover'))
    w = Variable('w', pb.user_type('waypoint'))
    constraint = Always(Forall( Or(Not(pb.fluent('in')(r, w)), pb.fluent('in_sun')(w), LE(16, pb.fluent('energy')(r))), r, w ))
    constraints_dict['SIMPLE'].append(constraint)
    
    # ONLY R0, R2, R3 CAN HAVE ROCK DATA FROM W4
    constraint = Always(Not(pb.fluent('have_rock_analysis')(pb.object('rover1'), pb.object('waypoint4'))))
    constraints_dict['SIMPLE'].append(constraint)
    
    # ONLY R1, R2 CAN HAVE ROCK DATA FROM W5
    constraint = Always(Forall(Or(Not(pb.fluent('have_rock_analysis')(r, pb.object('waypoint5'))), Or(Equals(r, pb.object('rover1')), Equals(r, pb.object('rover2')))), r))
    constraints_dict['SIMPLE'].append(constraint)
    
    # SOIL DATA FROM WAYPOINT3 MUST BE COMMUNICATED BEFORE ANY ROVER COLLECTS SOIL FROM WAYPOINT1"
    constraint = Always(
        Or(
            And(
                pb.fluent('at_soil_sample')(pb.object('waypoint1')),
                Not(pb.fluent('communicated_soil_data')(pb.object('waypoint3')))
            ),
            
            And(
                pb.fluent('at_soil_sample')(pb.object('waypoint1')),
                pb.fluent('communicated_soil_data')(pb.object('waypoint3'))
            ),
            
            And(
                Not(pb.fluent('at_soil_sample')(pb.object('waypoint1'))),
                pb.fluent('communicated_soil_data')(pb.object('waypoint3'))
            )
        )
    )
    constraints_dict['SIMPLE'].append(constraint)
    
    # BEFORE ANY ROVER COLLECTS A ROCK SAMPLE FROM WAYPOINT5, THE SOIL DATA FROM WAYPOINT4 MUST HAVE BEEN COMMUNICATED 
    constraint = Always(
        Or(
            And(
                pb.fluent('at_rock_sample')(pb.object('waypoint5')),
                Not(pb.fluent('communicated_soil_data')(pb.object('waypoint4')))
            ),
            
            And(
                pb.fluent('at_rock_sample')(pb.object('waypoint5')),
                pb.fluent('communicated_soil_data')(pb.object('waypoint4'))
            ),
            
            And(
                Not(pb.fluent('at_rock_sample')(pb.object('waypoint5'))),
                pb.fluent('communicated_soil_data')(pb.object('waypoint4'))
            )
        )
    )
    constraints_dict['SIMPLE'].append(constraint)
    
    
    ### Generate AND constraints from SIMPLE constraints
    constraints_dict['AND'] = []
    for i in range(2, len(constraints_dict['SIMPLE'])+1):
        for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
            constraints_dict['AND'].append( And(x) )
    
    return constraints_dict

def initializeHumanConstraintsRover8nt(pb):
    constraints_dict = {'SIMPLE':[]}
    
    r = Variable('r', pb.user_type('rover'))
    w = Variable('w', pb.user_type('waypoint'))
    o = Variable('o', pb.user_type('objective'))
    m = Variable('m', pb.user_type('mode'))
    
    # ROVER2 SHOULD NEVER BE USED
    constraint = Always(And(
            pb.fluent('in')(pb.object('rover2'), pb.object('waypoint2')),
            LE(50, pb.fluent('energy')(pb.object('rover2'))),
            pb.fluent('empty')(pb.object('rover2store')),
            Forall(Not(pb.fluent('have_soil_analysis')(pb.object('rover2'), w)), w),
            Forall(Not(pb.fluent('have_rock_analysis')(pb.object('rover2'), w)), w),
            Forall(Not(pb.fluent('have_image')(pb.object('rover2'), o, m)), o, m),
    ))
    duration = 0.0
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    # ONLY ROVER3 SHOULD PERFORM THE ROCK AND SOIL ANALYSIS FOR WAYPOINT 3 AND 4
    constraint = Always(And(
        Not(pb.fluent('have_soil_analysis')(pb.object('rover0'), pb.object('waypoint3'))),
        Not(pb.fluent('have_soil_analysis')(pb.object('rover1'), pb.object('waypoint3'))),
        Not(pb.fluent('have_soil_analysis')(pb.object('rover2'), pb.object('waypoint3'))),
        
        Not(pb.fluent('have_soil_analysis')(pb.object('rover0'), pb.object('waypoint4'))),
        Not(pb.fluent('have_soil_analysis')(pb.object('rover1'), pb.object('waypoint4'))),
        Not(pb.fluent('have_soil_analysis')(pb.object('rover2'), pb.object('waypoint4'))),
        
        Not(pb.fluent('have_rock_analysis')(pb.object('rover0'), pb.object('waypoint3'))),
        Not(pb.fluent('have_rock_analysis')(pb.object('rover1'), pb.object('waypoint3'))),
        Not(pb.fluent('have_rock_analysis')(pb.object('rover2'), pb.object('waypoint3'))),
    ))
    duration = 0.0
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    
    # ROVER3 SHOULD NEVER TAKE AN IMAGE
    constraint = Always(Forall(Not(pb.fluent('have_image')(pb.object('rover3'), o, m)), o, m))
    duration = 0.0
    constraints_dict['SIMPLE'].append((constraint, duration))
    
    ### Generate AND constraints from SIMPLE constraints
    constraints_dict['AND'] = []
    for i in range(2, len(constraints_dict['SIMPLE'])+1):
        for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
            constraints = [c[0] for c in x]
            times = [c[1] for c in x]
            constraints_dict['AND'].append( (And(constraints), sum(times)) )
    
    return constraints_dict

def initializeHumanConstraintsRover10nt(pb):
    constraints_dict = {'SIMPLE':[]}
    
    r = Variable('r', pb.user_type('rover'))
    w = Variable('w', pb.user_type('waypoint'))
    o = Variable('o', pb.user_type('objective'))
    m = Variable('m', pb.user_type('mode'))
    
    r0 = pb.object('rover0')
    r1 = pb.object('rover1')
    r2 = pb.object('rover2')
    r3 = pb.object('rover3')
    
    w0 = pb.object('waypoint0')
    w1 = pb.object('waypoint1')
    w2 = pb.object('waypoint2')
    w3 = pb.object('waypoint3')
    w4 = pb.object('waypoint4')
    w5 = pb.object('waypoint5')
    w6 = pb.object('waypoint6')
    
    # ROVER0 SHOULD HANDLE SOIL AND ROCK DATA FROM WAYPOINT4
    constraint = Always(And(
            Forall(Or(
                Equals(r, r0),
                Not(pb.fluent('have_soil_analysis')(r, w4))
            ), r),
            
            Not(pb.fluent('have_rock_analysis')(r1, w4)),
            Not(pb.fluent('have_rock_analysis')(r2, w4)),
            Not(pb.fluent('have_rock_analysis')(r3, w4)),
    ))
    duration = 11.641509294509888 + 44.54672193527222 + 15.726255416870117 + 0 + 34.23581695556640
    constraints_dict["SIMPLE"].append((constraint, duration))
    
    # NO ROVER SHOULD EVER BE IN WAYPOINT2 OR WAYPOINT5
    constraint = Always(And(
        Forall(Not(pb.fluent('in')(r, w2)), r),
        Forall(Not(pb.fluent('in')(r, w5)), r)
    ))
    duration = 0.8064041137695312 + 12.046087741851807 + 3.909336566925049 + 0 + 14.28100085258483
    constraints_dict["SIMPLE"].append((constraint, duration))
            
    # ROVER3 SHOULD NEVER TAKE AN IMAGE
    constraint = Always(And(
            Forall(Not(pb.fluent('have_image')(r3, o, pb.object('colour'))), o),
            Forall(Not(pb.fluent('have_image')(r3, o, pb.object('highres'))), o),
            Forall(Not(pb.fluent('have_image')(r3, o, pb.object('lowres'))), o),
                            
        ))
    duration = 40.21577548980713 + 19.244122982025146 + 8.325299739837646 + 0 + 26.8240303993225
    constraints_dict["SIMPLE"].append((constraint, duration))

    # WAYPOINT6 SHOULD ALWAYS HAVE SAME ROCK SAMPLE
    constraint = Always(pb.fluent('at_rock_sample')(w6))
    duration = 17.851055145263672 + 18.543925762176514 + 14.049310684204102 + 0 + 9.07705426216125
    constraints_dict["SIMPLE"].append((constraint, duration))
    
    ### Generate AND constraints from SIMPLE constraints
    constraints_dict['AND'] = []
    for i in range(2, len(constraints_dict['SIMPLE'])+1):
        for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
            constraints = [c[0] for c in x]
            times = [c[1] for c in x]
            constraints_dict['AND'].append( (And(constraints), sum(times)) )

    return constraints_dict

def initializeHumanConstraintsWoodworking7(pb):
    return None

##############
## PROBLEMS ##
##############

problems = {
    'Woodworking7': [    
        '/home/afavier/ws/CAI/domain.pddl',
        '/home/afavier/ws/CAI/p07.pddl',
        ['goalsize', 'boardsize-successor', 'has-colour', 'contains-part', 'grind-treatment-change', 'is-smooth', 'spray-varnish-cost', 'glaze-cost', 'grind-cost', 'plane-cost'],
        initializeHumanConstraintsWoodworking7,
    ],
    'Parking283': [    
        '/home/afavier/ws/CAI/domain.pddl',
        '/home/afavier/ws/CAI/p28-3.pddl',
        [],
        initializeHumanConstraintsWoodworking7,
    ],
    'ZenoTravel13': [    
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl',
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile13.pddl',
        ['distance', 'slow-burn', 'fast-burn', 'capacity', 'zoom-limit'],
        initializeHumanConstraintsZenotravel13,
    ],
    'ZenoTravel7': [    
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl',
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile7.pddl',
        ['distance', 'slow-burn', 'fast-burn', 'capacity', 'zoom-limit'],
        initializeHumanConstraintsZenotravel7,
    ],
    'ZenoTravel10': [    
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl',
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile10.pddl',
        ['distance', 'slow-burn', 'fast-burn', 'capacity', 'zoom-limit'],
        initializeHumanConstraintsZenotravel10,
    ],
    'Rover13': [
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/Rover-Numeric/domain.pddl',
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/Rover-Numeric/pfile13.pddl',
        ['in', 'empty', 'have_rock_analysis', 'have_soil_analysis', 'full', 'calibrated', 'available', 'have_image', 'communicated_soil_data', 'communicated_rock_data', 'communicated_image_data', 'energy', 'recharges'],
        initializeHumanConstraintsRover13,
    ],
    'Rover8_n': [
    # Comment: Can't find a valid in within 15min, neither using anytime or sat-hmrph. But can find a 55 long solution with just 5 TO and random constraints
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/Rover-Numeric/domain_n.pddl',
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/Rover-Numeric/pfile8.pddl',
        ['in', 'empty', 'have_rock_analysis', 'have_soil_analysis', 'full', 'calibrated', 'available', 'have_image', 'communicated_soil_data', 'communicated_rock_data', 'communicated_image_data', 'energy', 'recharges'],
        initializeHumanConstraintsRover8n,
    ],
    'Rover8_n_t': [
    # Comment: Can't find a valid in within 15min, neither using anytime or sat-hmrph. But can find a 55 long solution with just 5 TO and random constraints
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/Rover-Numeric/domain_n_t.pddl',
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/Rover-Numeric/pfile8_t.pddl',
        ['in', 'empty', 'have_rock_analysis', 'have_soil_analysis', 'full', 'calibrated', 'available', 'have_image', 'communicated_soil_data', 'communicated_rock_data', 'communicated_image_data', 'energy', 'recharges'],
        initializeHumanConstraintsRover8nt,
    ],
    'Rover10_n_t': [
    # Comment: Can't find a valid in within 15min, neither using anytime or sat-hmrph. But can find a 55 long solution with just 5 TO and random constraints
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/Rover-Numeric/domain_n_t.pddl',
        '/home/afavier/ws/CAI/NumericTCORE/benchmark/Rover-Numeric/pfile10_t.pddl',
        ['in', 'empty', 'have_rock_analysis', 'have_soil_analysis', 'full', 'calibrated', 'available', 'have_image', 'communicated_soil_data', 'communicated_rock_data', 'communicated_image_data', 'energy', 'recharges'],
        initializeHumanConstraintsRover10nt,
    ],
}

###############
### HELPERS ###
###############

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

##########################
## GENERATE CONSTRAINTS ##
##########################
def make_random_expression(changing_fluents, original_problem, expressions):
    
    i=0
    while i<MAX_RETRY_PICK:
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
                
        # Only go out if not already in expressions
        if not exp in expressions:
            break
        elif i+1==MAX_RETRY_PICK:
            raise Exception("make_random_expression: MAX_RETRY_PICK reached")
        i+=1
        
    expressions.append(exp)
    return exp
                
def generate_constraints(original_problem, names_of_constants):
    # Select only changing fluents (not constants)
    changing_fluents = []
    for f in original_problem.fluents:
        if not f.name in names_of_constants:
            changing_fluents.append(f)
            
    constraints_dict = {}
    expressions = []
    
    # SIMPLE
    constraints_dict['SIMPLE'] = []
    for i in range(NB_CONSTRAINT_SIMPLE):
        exp = make_random_expression(changing_fluents, original_problem, expressions)
        constraint = Always(exp)
        constraints_dict['SIMPLE'].append(constraint)
        expressions += [exp]
         
    # AND2   
    constraints_dict['AND2'] = []
    for i in range(NB_CONSTRAINT_AND2):
        e1 = make_random_expression(changing_fluents, original_problem, expressions)
        e2 = make_random_expression(changing_fluents, original_problem, expressions)
        constraint = Always(And(e1, e2))
        constraints_dict['AND2'].append(constraint)
        expressions += [e1, e2]
             
    # AND3
    constraints_dict['AND3'] = []
    for i in range(NB_CONSTRAINT_AND3):
        e1 = make_random_expression(changing_fluents, original_problem, expressions)
        e2 = make_random_expression(changing_fluents, original_problem, expressions)
        e3 = make_random_expression(changing_fluents, original_problem, expressions)
        constraint = Always(And(e1, e2, e3))
        constraints_dict['AND3'].append(constraint)
        expressions += [e1, e2, e3]
        
    # OR2    
    constraints_dict['OR2'] = []
    for i in range(NB_CONSTRAINT_OR2):
        e1 = make_random_expression(changing_fluents, original_problem, expressions)
        e2 = make_random_expression(changing_fluents, original_problem, expressions)
        constraint = Always(Or(e1, e2))
        constraints_dict['OR2'].append(constraint)
        expressions += [e1, e2]
        
    # OR3                
    constraints_dict['OR3'] = []
    for i in range(NB_CONSTRAINT_OR3):
        e1 = make_random_expression(changing_fluents, original_problem, expressions)
        e2 = make_random_expression(changing_fluents, original_problem, expressions)
        e3 = make_random_expression(changing_fluents, original_problem, expressions)
        constraint = Always(Or(e1, e2, e3))
        constraints_dict['OR3'].append(constraint)
        expressions += [e1, e2, e3]
        
    return expressions, constraints_dict

g_expressions = {}
g_constraints_dict = {}
def init_global_constraints(problemname):
    global g_expressions, g_constraints_dict
    random.seed(SEED)
    
    print(f"Generates random constraints for {problemname} with seed={SEED} ... ", end='', flush=True)
    reader = PDDLReader()
    domain = problems[problemname][0]
    problem = problems[problemname][1]
    names_of_constants = problems[problemname][2]
    original_problem: upProblem = reader.parse_problem(domain, problem) 
    
    # Check if original problem has no constraints
    if original_problem.trajectory_constraints!=[]:
        raise Exception('Already some constraints in original problem')
    
    g_expressions[problemname], g_constraints_dict[problemname] = generate_constraints(original_problem, names_of_constants)
        
    print('Done')

###########
## SOLVE ##
###########

def randomc(problemname, timeout, hideprogressbar=False):
    run_name = f"{problemname}-W-{NB_EXPRESSION}-{NB_TEST}-TO{timeout}"
    if not hideprogressbar:
        print(run_name)
    
    # # Parse original problem
    reader = PDDLReader()
    domain = problems[problemname][0]
    problem = problems[problemname][1]
    original_problem: upProblem = reader.parse_problem(domain, problem) 

    # Check if original problem has no constraints
    if original_problem.trajectory_constraints!=[]:
        raise Exception('Already some constraints in original problem')

    # Create result file
    all_results = {}
    all_results['seed'] = SEED
    all_results['timeout'] = timeout
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'{run_name}_{date}.json'
    path = 'results_constraints/'
    all_results['domain'] = domain
    all_results['problem'] = problem
    with open(path+filename, 'w') as f:
        f.write(json.dumps(all_results, indent=4))

    # Init constraints
    if problemname not in g_constraints_dict:
        init_global_constraints(problemname)
    expressions = g_expressions[problemname]
    constraints_dict = g_constraints_dict[problemname]
    all_results['generated_constraints'] = {'EXPRESSIONS': [str(e) for e in expressions]}
    for k,l in constraints_dict.items():
        all_results['generated_constraints'][k] = [str(c) for c in l]
    with open(path+filename, 'w') as f:
        f.write(json.dumps(all_results, indent=4))

    # Tests
    t_elapsed = time.time()
    all_results['tests'] = []
    all_results['general_status'] = 'in progress'
    with open(path+filename, 'w') as f:
        all_results['elapsed'] = str(time.time()-t_elapsed)
        f.write(json.dumps(all_results, indent=4))
    itType = iter(MyIterator(constraints_dict))
    if not hideprogressbar:
        bar = IncrementalBar('Processsing', max=NB_TEST, suffix = '%(percent).1f%% - ETA %(eta_td)s')
    for i in range(NB_TEST):
        
        if not hideprogressbar:
            bar.start()
        test = {}
        
        # Get current type and pickRandom of this type
        type_name, type_list = next(itType)
        picked_constraint = pickRandom(type_list)
        n_retry = 1
        while str(picked_constraint) in [t['constraint'] for t in all_results['tests']]:
            if n_retry>MAX_RETRY_PICK:
                raise Exception("MAX_RETRY_PICK reached")
            picked_constraint = pickRandom(type_list)
            n_retry+=1
        test['constraint'] = str(picked_constraint)
        test['constraint_type'] = type_name
        all_results['tests'].append(test)
        
        # Update problem with constraint
        new_problem = original_problem.clone()
        new_problem.add_trajectory_constraint(picked_constraint)

        # Write new problem with up
        problem_name = filename.replace('.json', '')
        w = PDDLWriter(new_problem)
        w.write_domain(f'tmp/{problem_name}_updated_domain.pddl')
        w.write_problem(f'tmp/{problem_name}_updated_problem.pddl')

        # Compile
        test['result'] = 'Compiling...'
        with open(path+filename, 'w') as f:
            all_results['elapsed'] = str(time.time()-t_elapsed)
            f.write(json.dumps(all_results, indent=4))
        t1_compile = time.time()
        ntcore(f'tmp/{problem_name}_updated_domain.pddl', f'tmp/{problem_name}_updated_problem.pddl', "tmp/", filename=problem_name, achiever_strategy=NtcoreStrategy.DELTA, verbose=False)
        t2_compile = time.time()
        compile_duration = t2_compile-t1_compile
        test['compilation_time'] = compile_duration

        # Plan
        test['result'] = 'Planning...'
        with open(path+filename, 'w') as f:
            all_results['elapsed'] = str(time.time()-t_elapsed)
            f.write(json.dumps(all_results, indent=4))
        PROBLEMS[problem_name] = (f"tmp/{problem_name}_compiled_dom.pddl", f"tmp/{problem_name}_compiled_prob.pddl")
        t1_plan = time.time()
        result, plan, planlength, metric, fail_reason = planner(problem_name, plan_mode=PlanMode.ANYTIME, hide_plan=True, timeout=timeout-compile_duration)
        t2_plan = time.time()
        plan_duration = round(t2_plan-t1_plan, 5)
        test['planning_time'] = plan_duration

        # Get Metric
        test['result'] = result
        test['plan'] = plan
        test['planlength'] = planlength
        test['metric'] = metric
        test['reason'] = fail_reason
        with open(path+filename, 'w') as f:
            all_results['elapsed'] = str(time.time()-t_elapsed)
            f.write(json.dumps(all_results, indent=4))
            
        if not hideprogressbar:
            bar.next()
    
        
    all_results['general_status'] = 'completed'
    with open(path+filename, 'w') as f:
        all_results['elapsed'] = str(time.time()-t_elapsed)
        f.write(json.dumps(all_results, indent=4))
    
def original(problemname, timeout, hideprogressbar=False):
    
    run_name = f"{problemname}-WO-{NB_WO}-TO{timeout}"
    if not hideprogressbar:
        print(run_name)

    domain = problems[problemname][0]
    problem = problems[problemname][1]
    
    # Create result file
    all_results = {}
    all_results['timeout'] = timeout
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'{run_name}_{date}.json'
    path = 'results_constraints/'
    all_results['domain'] = domain
    all_results['problem'] = problem
    with open(path+filename, 'w') as f:
        f.write(json.dumps(all_results, indent=4))


    all_results['tests'] = []
    all_results['general_status'] = 'in progress'
    t_elapsed = time.time()
    with open(path+filename, 'w') as f:
        all_results['elapsed'] = str(time.time()-t_elapsed)
        f.write(json.dumps(all_results, indent=4))
    if not hideprogressbar:
        bar = IncrementalBar('Processsing', max=NB_WO, suffix = '%(percent).1f%% - ETA %(eta_td)s')
    for i in range(NB_WO):
        if not hideprogressbar:
            bar.start()
        test = {}
        all_results['tests'].append(test)
        
        # plan
        test['result'] = 'Planning...'
        with open(path+filename, 'w') as f:
            all_results['elapsed'] = str(time.time()-t_elapsed)
            f.write(json.dumps(all_results, indent=4))
        PROBLEMS[run_name] = (domain, problem)
        t1_plan = time.time()
        result, plan, planlength, metric, fail_reason = planner(run_name, plan_mode=PlanMode.ANYTIME, hide_plan=True, timeout=timeout)
        t2_plan = time.time()
        plan_duration = t2_plan-t1_plan
        test['planning_time'] = plan_duration
        
        test['result'] = result
        test['reason'] = fail_reason
        test['plan'] = plan
        test['planlength'] = planlength
        test['metric'] = metric
            
        with open(path+filename, 'w') as f:
            all_results['elapsed'] = str(time.time()-t_elapsed)
            f.write(json.dumps(all_results, indent=4))
            
        if not hideprogressbar:
            bar.next()
    
    all_results['general_status'] = 'completed'
    with open(path+filename, 'w') as f:
        all_results['elapsed'] = str(time.time()-t_elapsed)
        f.write(json.dumps(all_results, indent=4))

def humanc(problemname, timeout, remove_translation_time=False, hideprogressbar=False):
    if not remove_translation_time:
        run_name = f"{problemname}-H-TO{timeout}"
    else:
        run_name = f"{problemname}-HT-TO{timeout}"
    if not hideprogressbar:
        print(run_name)
    
    # Parse original problem
    reader = PDDLReader()
    domain = problems[problemname][0]
    problem = problems[problemname][1]
    original_problem: upProblem = reader.parse_problem(domain, problem) 

    # Check if original problem has no constraints
    if original_problem.trajectory_constraints!=[]:
        raise Exception('Already some constraints in original problem')

    # Create result file
    all_results = {}
    all_results['seed'] = SEED
    all_results['timeout'] = timeout
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'{run_name}_{date}.json'
    path = 'results_constraints/'
    all_results['domain'] = domain
    all_results['problem'] = problem
    with open(path+filename, 'w') as f:
        f.write(json.dumps(all_results, indent=4))

    # Generate constraints
    human_constraints_init = problems[problemname][3]
    constraints_dict = human_constraints_init(original_problem)
    all_results['generated_constraints'] = {}
    for k,l in constraints_dict.items():
        all_results['generated_constraints'][k] = [str(c) for c in l]
    with open(path+filename, 'w') as f:
        f.write(json.dumps(all_results, indent=4))

    # Tests
    t_elapsed = time.time()
    all_results['tests'] = []
    all_results['general_status'] = 'in progress'
    with open(path+filename, 'w') as f:
        all_results['elapsed'] = str(time.time()-t_elapsed)
        f.write(json.dumps(all_results, indent=4))
    N_TOTAL = len(constraints_dict['SIMPLE'])+len(constraints_dict['AND'])
    if not hideprogressbar:
        bar =  IncrementalBar(f'Processsing', max=N_TOTAL, suffix = '%(percent).1f%% - ETA %(eta_td)s')
    for type_name in constraints_dict:
        type_list = constraints_dict[type_name]
        for picked_constraint in type_list:
            
            translation_duration = picked_constraint[1] if remove_translation_time else 0.0
            picked_constraint = picked_constraint[0]
            
            if not hideprogressbar:
                bar.start()
            test = {}
            
            # Get current type and pickRandom of this type
            test['constraint'] = str(picked_constraint)
            test['constraint_type'] = type_name
            all_results['tests'].append(test)
            test['translation_time'] = translation_duration
            
            # Update problem with constraint
            new_problem = original_problem.clone()
            new_problem.add_trajectory_constraint(picked_constraint)

            # Write new problem with up
            problem_name = filename.replace('.json', '')
            w = PDDLWriter(new_problem)
            w.write_domain(f'tmp/{problem_name}_updated_domain.pddl')
            w.write_problem(f'tmp/{problem_name}_updated_problem.pddl')

            # Compile
            test['result'] = 'Compiling...'
            with open(path+filename, 'w') as f:
                all_results['elapsed'] = str(time.time()-t_elapsed)
                f.write(json.dumps(all_results, indent=4))
            t1_compile = time.time()
            ntcore(f'tmp/{problem_name}_updated_domain.pddl', f'tmp/{problem_name}_updated_problem.pddl', "tmp/", filename=problem_name, achiever_strategy=NtcoreStrategy.DELTA, verbose=False)
            t2_compile = time.time()
            compile_duration = t2_compile-t1_compile
            test['compilation_time'] = compile_duration
            
            # Plan
            test['result'] = 'Planning...'
            with open(path+filename, 'w') as f:
                all_results['elapsed'] = str(time.time()-t_elapsed)
                f.write(json.dumps(all_results, indent=4))
            PROBLEMS[problem_name] = (f"tmp/{problem_name}_compiled_dom.pddl", f"tmp/{problem_name}_compiled_prob.pddl")
            t1_plan = time.time()
            compile_duration=0.0
            result, plan, planlength, metric, fail_reason = planner(problem_name, plan_mode=PlanMode.ANYTIME, hide_plan=True, timeout=timeout-compile_duration-translation_duration)
            t2_plan = time.time()
            plan_duration = t2_plan-t1_plan
            test['planning_time'] = plan_duration

            # Get Metric
            test['result'] = result
            test['plan'] = plan
            test['planlength'] = planlength
            test['metric'] = metric
            test['reason'] = fail_reason
                
            with open(path+filename, 'w') as f:
                all_results['elapsed'] = str(time.time()-t_elapsed)
                f.write(json.dumps(all_results, indent=4))
                
            if not hideprogressbar:
                bar.next()
        
    all_results['general_status'] = 'completed'
    with open(path+filename, 'w') as f:
        all_results['elapsed'] = str(time.time()-t_elapsed)
        f.write(json.dumps(all_results, indent=4))
            
def h_translation(problemname, timeout, hideprogressbar=False):
    humanc(problemname, timeout, remove_translation_time=True, hideprogressbar=hideprogressbar)

################
## MAIN + CLI ##
################

@click.group(help=f'{[p for p in problems]}')
def cli():
    pass

@cli.command(help=f'{[p for p in problems]}')
@click.argument('timeout', default=1)
@click.option('-p', '--problemname', 'problemname', default=PROBLEM_NAME)
@click.option('--hideprogressbar', 'hideprogressbar', is_flag=True, default=False)
def randomc_command(timeout: int, problemname: str, hideprogressbar: bool):
    randomc(problemname, timeout, hideprogressbar)

@cli.command(help=f'{[p for p in problems]}')
@click.argument('timeout', default=1)
@click.option('-p', '--problamname', 'problemname', default=PROBLEM_NAME)
@click.option('--hideprogressbar', 'hideprogressbar', is_flag=True, default=False)
def original_command(timeout: int, problemname: str, hideprogressbar: bool):
    original(problemname, timeout, hideprogressbar)
    
@cli.command(help=f'{[p for p in problems]}')
@click.argument('timeout', default=1)
@click.option('-p', '--problemname', 'problemname', default=PROBLEM_NAME)
@click.option('--hideprogressbar', 'hideprogressbar', is_flag=True, default=False)
def humanc_command(timeout: int, problemname: str, hideprogressbar: bool):
    humanc(problemname, timeout, remove_translation_time=False, hideprogressbar=hideprogressbar)

@cli.command(help=f'{[p for p in problems]}')
@click.argument('timeout', default=1)
@click.option('-p', '--problemname', 'problemname', default=PROBLEM_NAME)
@click.option('--hideprogressbar', 'hideprogressbar', is_flag=True, default=False)
def h_translation_command(timeout: int, problemname: str, hideprogressbar: bool):
    h_translation(problemname, timeout, hideprogressbar=hideprogressbar)

if __name__=="__main__":
    try:
        cli()
    except KeyboardInterrupt:
        print("Ctrl+C detected. Exiting...")
        # Kill ENHSP java process
        # for proc in psutil.process_iter():
        #     if proc.name() == "java":
        #         proc.kill()
