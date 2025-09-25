from pulp import *

from pb_zeno import *
# from pb_blocks import *
# from pb_log import *

############
## NO-OPS ##
############
for f in Vp:
    actions.append(f'noop_{f}')
    pre_p[f'noop_{f}'] = {f}
    del_p[f'noop_{f}'] = set()
    add_p[f'noop_{f}'] = {f}

def generatePreF(actions, Vp):
    pref = {}
    for f in Vp:
        pref[f] = set()
        for a in actions:
            if f in pre_p[a]:
                pref[f] = pref[f].union({a})
    return pref
def generateAddF(actions, Vp):
    addf = {}
    for f in Vp:
        addf[f] = set()
        for a in actions:
            if f in add_p[a]:
                addf[f] = addf[f].union({a})
    return addf
def generateDelF(actions, Vp):
    delf = {}
    for f in Vp:
        delf[f] = set()
        for a in actions:
            if f in del_p[a]:
                delf[f] = delf[f].union({a})
    return delf

pref = generatePreF(actions, Vp) # actions with p in preconditions
addf = generateAddF(actions, Vp) # actions with p in add effects
delf = generateDelF(actions, Vp) # actions with p in del effects
 
#################
## BUILD MODEL ##
#################

def export_constraints(constraints):
    with open('constraints.txt', 'w') as file:
        file.write(f"-----------------------\n")
        file.write(f"----- CONSTRAINTS -----\n")
        file.write(f"-----------------------\n")
        for c in constraints:
            file.write(f'{c}: {constraints[c]}\n')

# Working with all problems! But wrong parallel actions for zeno
def vossen2011_fluent(T):
    global y

    ###########
    ## MODEL ##
    ###########
    m = LpProblem(sense=LpMinimize)
 

    ###############
    ## VARIABLES ##
    ###############
    y = {}
    for a in actions:
        y[a] = {}
        for i in range(1, T+1):
            y[a][i] = LpVariable(f'x_{a}_{i}', cat='Binary')
            
    x = {}
    for f in Vp:
        x[f] = {}
        for i in range(1, T+2):
            x[f][i] = LpVariable(f'y_{f}_{i}', cat='Binary')
    
            
    ###############
    ## OBJECTIVE ##
    ###############
    def obj_nb_actions_wo_noop(m):
        L = []
        for a in actions:
            if 'noop' not in a:
                for t in range(1, T+1):
                    L.append(y[a][t])
        m += lpSum(L)
    
    obj_nb_actions_wo_noop(m)
        
        
    #################
    ## CONSTRAINTS ##
    #################
    
    # Initial/Goal State
    for f in Vp:
        if f in I:
            m += x[f][1] == 1
        else:
            m += x[f][1] == 0
        
        if f in Gp:
            m += x[f][T+1] == 1
    
    
    # Precondition
    for f in Vp:
        for a in pref[f]:
            for i in range(1, T+1):
                m += y[a][i] <= x[f][i]
                
    # Explanatory Frame Conditions Backward chaining 
    for i in range(1, T+1):
        for f in Vp:
            m += x[f][i+1] <= lpSum(y[a][i] for a in addf[f])
            
    # Conflict Exclusion Constraints
    for a1 in actions:
        for a2 in actions:
            for f in Vp:
                if a1 != a2 and a1 in delf[f] and a2 in pref[f].union(addf[f]):
                    for i in range(1, T+1):
                        m += y[a1][i] + y[a2][i] <= 1
    
    #############
    ## SOLVING ##
    #############
    m.solve()
    
    
    ############
    ## EXPORT ##
    ############
    export_constraints(m.constraints)

    with open('variables.txt', 'w') as file:
        for t in range(1, T+2):
            file.write(f"\n-----------------\n")
            file.write(f"----- t = {t} -----\n")
            file.write(f"-----------------\n")
                    
            file.write(f"\n-- FLUENTS --\n")
            for f in Vp:
                file.write(f'{x[f][t]} = {x[f][t].value()}\n')
            
            if t!=T+1:
                file.write(f"\n-- ACTIONS --\n")
                for a in actions:
                    file.write(f'{y[a][t]} = {y[a][t].value()}\n')
    return m

import sys
time_horizon = int(sys.argv[1]) if len(sys.argv)>=2 else 2
m = vossen2011_fluent(time_horizon)

######################
## EXTRACT SOLUTION ##
######################

if m.status!=1:
    print("[ERROR]")
    print('Problem: ', LpStatus[m.status])
    print('Solution: ', LpSolution[m.sol_status])
else:
    print(f'[{LpSolution[m.sol_status]}]')
    
    plan = {}
    print("plan:")
    for t in range(1, time_horizon+1):
        time_stamp_txt = f'{t}: '
        print(time_stamp_txt, end='')
        for a in y:
            if t not in plan:
                plan[t] = []
                
            if y[a][t].value():
                spaces = '' if len(plan[t])==0 else ' '*(len(time_stamp_txt))
                
                action_name = str(y[a][t])
                action_name = action_name[action_name.find('_')+1:action_name.rfind('_')]
                if 'noop' in action_name:
                    action_name = "<"+action_name+">"
                    
                plan[t].append( action_name )
                
                print(f'{spaces}{action_name}')
                