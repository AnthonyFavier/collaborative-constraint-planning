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
import psutil
from datetime import datetime

import typing
from unified_planning.model.problem import Problem as upProblem
from unified_planning.model.fluent import Fluent as upFluent
from unified_planning.model.parameter import Parameter as upParameter
from unified_planning.model.types import _RealType as upReal
from unified_planning.model.types import _BoolType as upBool
import itertools

######################
## HYPER PARAMETERS ##
######################

PROBLEM_NAME = 'Rover8_n'
# ZenoTravel13, Rover13, Rover8_n, Rover8_n_t, Rover10_n_t, ZenoTravel7

NB_EXPRESSION =         50
NB_CONSTRAINT_SIMPLE =  NB_EXPRESSION
NB_CONSTRAINT_AND2 =    NB_EXPRESSION
NB_CONSTRAINT_AND3 =    NB_EXPRESSION
NB_CONSTRAINT_OR2 =     NB_EXPRESSION
NB_CONSTRAINT_OR3 =     NB_EXPRESSION
NB_TEST = NB_EXPRESSION*5 # Should be less or equal than NB_EXPRESSION * 5 to avoid redundant constraints

NB_WO = 10

SEED = random.randrange(sys.maxsize)
SEED = 0 # for testing

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
    constraints_dict['SIMPLE'].append(constraint)
    
    # PERSON7 SHOULD NOT MOVE
    constraint = Always(pb.fluent('located')(pb.object('person7'), pb.object('city0')))
    constraints_dict['SIMPLE'].append(constraint)


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
        pb.fluent('n_flyslow')(pb.object('plane1'), pb.object('city5'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city0'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city1'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city2'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city3'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city4'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city5'), c1),
        ),3), c1))
    constraints_dict['SIMPLE'].append(constraint)
    
    
    # PERSON1 AND PERSON3 SHOULD TRAVEL TOGETHER
    constraint = Always(Or(
        Exists(And( pb.fluent('in')(pb.object('person1'), a), pb.fluent('in')(pb.object('person3'), a) ), a),
        Exists(And( pb.fluent('located')(pb.object('person1'), c1), pb.fluent('located')(pb.object('person3'), c1) ), c1),
        Exists(And( pb.fluent('in')(pb.object('person1'), a), pb.fluent('located')(pb.object('person3'), c1), pb.fluent('located')(a, c1)), c1, a),
        Exists(And( pb.fluent('in')(pb.object('person3'), a), pb.fluent('located')(pb.object('person1'), c1), pb.fluent('located')(a, c1)), c1, a),
    ))
    constraints_dict['SIMPLE'].append(constraint)
    
    constraints_dict['AND'] = []
    for i in range(2, len(constraints_dict['SIMPLE'])):
        for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
            constraints_dict['AND'].append( And(x) )
    
    # constraints_dict['OR'] = []
    # for i in range(2, len(constraints_dict['SIMPLE'])):
    #     for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
    #         constraints_dict['OR'].append( Or(x) )
    
    return constraints_dict

def initializeHumanConstraintsZenotravel7(pb):
    constraints_dict = {"SIMPLE":[]}

    # PERSON2 SHOULD NOT MOVE
    constraint = Always(pb.fluent('located')(pb.object('person2'), pb.object('city3')))
    constraints_dict['SIMPLE'].append(constraint)
    
    # PERSON3 SHOULD NOT MOVE
    constraint = Always(pb.fluent('located')(pb.object('person3'), pb.object('city3')))
    constraints_dict['SIMPLE'].append(constraint)


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
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city0'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city1'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city2'), c1),
        pb.fluent('n_flyfast')(pb.object('plane1'), pb.object('city3'), c1),
        ),3), c1))
    constraints_dict['SIMPLE'].append(constraint)
    
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
    constraints_dict['SIMPLE'].append(constraint)
    
    constraints_dict['AND'] = []
    for i in range(2, len(constraints_dict['SIMPLE'])):
        for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
            constraints_dict['AND'].append( And(x) )
    
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
    for i in range(2, len(constraints_dict['SIMPLE'])):
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
    for i in range(2, len(constraints_dict['SIMPLE'])):
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
    constraints_dict['SIMPLE'].append(constraint)
    
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
    constraints_dict['SIMPLE'].append(constraint)
    
    
    # ROVER3 SHOULD NEVER TAKE AN IMAGE
    constraint = Always(Forall(Not(pb.fluent('have_image')(pb.object('rover3'), o, m)), o, m))
    constraints_dict['SIMPLE'].append(constraint)
    
    ### Generate AND constraints from SIMPLE constraints
    constraints_dict['AND'] = []
    for i in range(2, len(constraints_dict['SIMPLE'])):
        for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
            constraints_dict['AND'].append( And(x) )
    
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
    constraints_dict["SIMPLE"].append(constraint)
    
    # NO ROVER SHOULD EVER BE IN WAYPOINT2 OR WAYPOINT5
    constraint = Always(And(
        Forall(Not(pb.fluent('in')(r, w2)), r),
        Forall(Not(pb.fluent('in')(r, w5)), r)
    ))    
    constraints_dict["SIMPLE"].append(constraint)
            
    # ROVER3 SHOULD NEVER TAKE AN IMAGE
    constraint = Always(And(
            Forall(Not(pb.fluent('have_image')(r3, o, pb.object('colour'))), o),
            Forall(Not(pb.fluent('have_image')(r3, o, pb.object('highres'))), o),
            Forall(Not(pb.fluent('have_image')(r3, o, pb.object('lowres'))), o),
                            
        ))
    constraints_dict["SIMPLE"].append(constraint)

    # WAYPOINT6 SHOULD ALWAYS HAVE SAME ROCK SAMPLE
    constraint = Always(pb.fluent('at_rock_sample')(w6))
    constraints_dict["SIMPLE"].append(constraint)
    
    ### Generate AND constraints from SIMPLE constraints
    constraints_dict['AND'] = []
    for i in range(2, len(constraints_dict['SIMPLE'])):
        for x in list(itertools.combinations(constraints_dict['SIMPLE'], i)):
            constraints_dict['AND'].append( And(x) )

    return constraints_dict

##############
## PROBLEMS ##
##############

problems = {
    'ZenoTravel13': [    
        '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl',
        '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile13.pddl',
        ['distance', 'slow-burn', 'fast-burn', 'capacity', 'zoom-limit'],
        initializeHumanConstraintsZenotravel13,
    ],
    'ZenoTravel7': [    
        '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl',
        '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile7.pddl',
        ['distance', 'slow-burn', 'fast-burn', 'capacity', 'zoom-limit'],
        initializeHumanConstraintsZenotravel7,
    ],
    'ZenoTravel10': [    
        '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-n/domain_with_n.pddl',
        '/home/afavier/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile10.pddl',
        ['distance', 'slow-burn', 'fast-burn', 'capacity', 'zoom-limit'],
        initializeHumanConstraintsZenotravel10,
    ],
    'Rover13': [
        '/home/afavier/CAI/NumericTCORE/benchmark/Rover-Numeric/domain.pddl',
        '/home/afavier/CAI/NumericTCORE/benchmark/Rover-Numeric/pfile13.pddl',
        ['in', 'empty', 'have_rock_analysis', 'have_soil_analysis', 'full', 'calibrated', 'available', 'have_image', 'communicated_soil_data', 'communicated_rock_data', 'communicated_image_data', 'energy', 'recharges'],
        initializeHumanConstraintsRover13,
    ],
    'Rover8_n': [
    # Comment: Can't find a valid in within 15min, neither using anytime or sat-hmrph. But can find a 55 long solution with just 5 TO and random constraints
        '/home/afavier/CAI/NumericTCORE/benchmark/Rover-Numeric/domain_n.pddl',
        '/home/afavier/CAI/NumericTCORE/benchmark/Rover-Numeric/pfile8.pddl',
        ['in', 'empty', 'have_rock_analysis', 'have_soil_analysis', 'full', 'calibrated', 'available', 'have_image', 'communicated_soil_data', 'communicated_rock_data', 'communicated_image_data', 'energy', 'recharges'],
        initializeHumanConstraintsRover8n,
    ],
    'Rover8_n_t': [
    # Comment: Can't find a valid in within 15min, neither using anytime or sat-hmrph. But can find a 55 long solution with just 5 TO and random constraints
        '/home/afavier/CAI/NumericTCORE/benchmark/Rover-Numeric/domain_n_t.pddl',
        '/home/afavier/CAI/NumericTCORE/benchmark/Rover-Numeric/pfile8_t.pddl',
        ['in', 'empty', 'have_rock_analysis', 'have_soil_analysis', 'full', 'calibrated', 'available', 'have_image', 'communicated_soil_data', 'communicated_rock_data', 'communicated_image_data', 'energy', 'recharges'],
        initializeHumanConstraintsRover8nt,
    ],
    'Rover10_n_t': [
    # Comment: Can't find a valid in within 15min, neither using anytime or sat-hmrph. But can find a 55 long solution with just 5 TO and random constraints
        '/home/afavier/CAI/NumericTCORE/benchmark/Rover-Numeric/domain_n_t.pddl',
        '/home/afavier/CAI/NumericTCORE/benchmark/Rover-Numeric/pfile10_t.pddl',
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
def generate_constraints(original_problem):
    # Select only changing fluents (not constants)
    changing_fluents = []
    for f in original_problem.fluents:
        if not f.name in names_of_constants:
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
                if n_retry==MAX_RETRY_PICK:
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
                if n_retry==MAX_RETRY_PICK:
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
                if n_retry==MAX_RETRY_PICK:
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
                if n_retry==MAX_RETRY_PICK:
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
                if n_retry==MAX_RETRY_PICK:
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
                if n_retry==MAX_RETRY_PICK:
                    raise Exception("OR3: Too many retry to pick expression: Probably already picked all...")
    constraints_dict['OR3'] = constraints_OR3
    
    return expressions, constraints_dict

###########
## SOLVE ##
###########

def solve_with_constraints():
    run_name = f"{PROBLEM_NAME}-W-{NB_EXPRESSION}-{NB_TEST}-TO{TIMEOUT}"
    print(run_name)
    
    # Parse original problem
    reader = PDDLReader()
    original_problem: upProblem = reader.parse_problem(dp, pp) 

    # Check if original problem has no constraints
    if original_problem.trajectory_constraints!=[]:
        raise Exception('Already some constraints in original problem')

    # Create result file
    all_results = {}
    all_results['seed'] = SEED
    all_results['timeout'] = TIMEOUT
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'{run_name}_{date}.json'
    path = 'results_constraints/'
    all_results['domain'] = dp
    all_results['problem'] = pp
    with open(path+filename, 'w') as f:
        f.write(json.dumps(all_results, indent=4))

    # Generate constraints
    expressions, constraints_dict = generate_constraints(original_problem)
    all_results['generated_constraints'] = {'EXPRESSIONS': [str(e) for e in expressions]}
    for k,l in constraints_dict.items():
        all_results['generated_constraints'][k] = [str(c) for c in l]
    with open(path+filename, 'w') as f:
        f.write(json.dumps(all_results, indent=4))

    # Tests
    all_results['tests'] = []
    itType = iter(MyIterator(constraints_dict))
    with IncrementalBar('Processsing', max=NB_TEST, suffix = '%(percent).1f%% - ETA %(eta_td)s') as bar:
        for i in range(NB_TEST):
            
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
            test['result'] = 'In progress...'
            with open(path+filename, 'w') as f:
                f.write(json.dumps(all_results, indent=4))
            
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
            result, plan, planlength, metric, fail_reason = planner(problem_name, plan_mode=PlanMode.ANYTIME, hide_plan=True, timeout=TIMEOUT)

            # Get Metric
            test['result'] = result
            test['plan'] = plan
            test['planlength'] = planlength
            test['metric'] = metric
            test['reason'] = fail_reason
                
            with open(path+filename, 'w') as f:
                f.write(json.dumps(all_results, indent=4))
                
            bar.next()
    
        all_results['elapsed'] = str(bar.elapsed_td)
        with open(path+filename, 'w') as f:
            f.write(json.dumps(all_results, indent=4))
    
def solve_without_constraints():
    
    run_name = f"{PROBLEM_NAME}-WO-{NB_WO}-TO{TIMEOUT}"
    print(run_name)
    
    # Create result file
    all_results = {}
    all_results['timeout'] = TIMEOUT
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'{run_name}_{date}.json'
    path = 'results_constraints/'
    all_results['domain'] = dp
    all_results['problem'] = pp
    with open(path+filename, 'w') as f:
        f.write(json.dumps(all_results, indent=4))


    all_results['tests'] = []
    with IncrementalBar('Processsing', max=NB_WO, suffix = '%(percent).1f%% - ETA %(eta_td)s') as bar:
        for i in range(NB_WO):
            bar.start()
            test = {}
                
            all_results['tests'].append(test)
            test['all_results'] = 'In progress...'
            with open(path+filename, 'w') as f:
                f.write(json.dumps(all_results, indent=4))
            
            # plan
            PROBLEMS[run_name] = (dp, pp)
            result, plan, planlength, metric, fail_reason = planner(run_name, plan_mode=PlanMode.ANYTIME, hide_plan=True, timeout=TIMEOUT)
            
            test['result'] = result
            test['reason'] = fail_reason
            test['plan'] = plan
            test['planlength'] = planlength
            test['metric'] = metric
                
            with open(path+filename, 'w') as f:
                f.write(json.dumps(all_results, indent=4))
                
            bar.next()
    
        all_results['elapsed'] = str(bar.elapsed_td)
        with open(path+filename, 'w') as f:
            f.write(json.dumps(all_results, indent=4))

def solve_with_human_constraints():
    run_name = f"{PROBLEM_NAME}-H-TO{TIMEOUT}"
    print(run_name)
    
    # Parse original problem
    reader = PDDLReader()
    original_problem: upProblem = reader.parse_problem(dp, pp) 

    # Check if original problem has no constraints
    if original_problem.trajectory_constraints!=[]:
        raise Exception('Already some constraints in original problem')

    # Create result file
    all_results = {}
    all_results['seed'] = SEED
    all_results['timeout'] = TIMEOUT
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'{run_name}_{date}.json'
    path = 'results_constraints/'
    all_results['domain'] = dp
    all_results['problem'] = pp
    with open(path+filename, 'w') as f:
        f.write(json.dumps(all_results, indent=4))

    # Generate constraints
    constraints_dict = human_constraints_init(original_problem)
    all_results['generated_constraints'] = {}
    for k,l in constraints_dict.items():
        all_results['generated_constraints'][k] = [str(c) for c in l]
    with open(path+filename, 'w') as f:
        f.write(json.dumps(all_results, indent=4))

    # Tests
    all_results['tests'] = []
    N_TOTAL = len(constraints_dict['SIMPLE'])+len(constraints_dict['AND'])
    with IncrementalBar(f'Processsing', max=N_TOTAL, suffix = '%(percent).1f%% - ETA %(eta_td)s') as bar:
        for type_name in constraints_dict:
            type_list = constraints_dict[type_name]
            for picked_constraint in type_list:
                
                bar.start()
                test = {}
                
                # Get current type and pickRandom of this type
                test['constraint'] = str(picked_constraint)
                test['constraint_type'] = type_name
                    
                all_results['tests'].append(test)
                test['result'] = 'In progress...'
                with open(path+filename, 'w') as f:
                    f.write(json.dumps(all_results, indent=4))
                
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
                result, plan, planlength, metric, fail_reason = planner(problem_name, plan_mode=PlanMode.ANYTIME, hide_plan=True, timeout=TIMEOUT)

                # Get Metric
                test['result'] = result
                test['plan'] = plan
                test['planlength'] = planlength
                test['metric'] = metric
                test['reason'] = fail_reason
                    
                with open(path+filename, 'w') as f:
                    f.write(json.dumps(all_results, indent=4))
                    
                bar.next()
        
        all_results['elapsed'] = str(bar.elapsed_td)
        with open(path+filename, 'w') as f:
            f.write(json.dumps(all_results, indent=4))

##########
## MAIN ##
##########

def testing():
    run_name = f"{NB_EXPRESSION}-{NB_TEST}-TO{TIMEOUT}"
    print(run_name)
    
    # Parse original problem
    reader = PDDLReader()
    original_problem: upProblem = reader.parse_problem(dp, pp) 

    # Check if original problem has no constraints
    if original_problem.trajectory_constraints!=[]:
        raise Exception('Already some constraints in original problem')

    # Create result file
    all_results = {}
    all_results['seed'] = SEED
    all_results['timeout'] = TIMEOUT
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'{run_name}_{date}.json'
    path = 'results_constraints/'
    all_results['domain'] = dp
    all_results['problem'] = pp

    # Generate constraints
    expressions, constraints_dict = generate_constraints(original_problem)
    all_results['generated_constraints'] = {'EXPRESSIONS': [str(e) for e in expressions]}
    for k,l in constraints_dict.items():
        all_results['generated_constraints'][k] = [str(c) for c in l]
        
@click.command()
@click.argument('mode', default='with_human')
@click.argument('timeout', default=1)
def main_cli(mode: str, timeout: int):
    global TIMEOUT, dp, pp, names_of_constants, human_constraints_init
    TIMEOUT = timeout
    
    random.seed(SEED)
    
    dp = problems[PROBLEM_NAME][0]
    pp = problems[PROBLEM_NAME][1]
    names_of_constants = problems[PROBLEM_NAME][2]
    human_constraints_init = problems[PROBLEM_NAME][3]
    
    modes = {
        'with': solve_with_constraints,
        'without': solve_without_constraints,
        'with_human': solve_with_human_constraints,
        'testing': testing,
    }
    if mode not in modes:
        print('Unknown mode given [' + ', '.join([m for m in modes]) + ']')
    else:
        modes[mode]()

if __name__=="__main__":
    try:
        main_cli()
    except KeyboardInterrupt:
        print("Ctrl+C detected. Exiting...")
        # Kill ENHSP java process
        for proc in psutil.process_iter():
            if proc.name() == "java":
                proc.kill()
