from pulp import *

from pb_zeno import *
# from pb_blocks import *
# from pb_log import *

############
## NO-OPS ##
############
# for f in Vp:
#     actions.append(f'noop_{f}')
#     pre_p[f'noop_{f}'] = {f}
#     del_p[f'noop_{f}'] = set()
#     add_p[f'noop_{f}'] = {f}

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

def vossen2011_state_change(T):
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
            y[a][i] = LpVariable(f'x_{a}_{i}', cat='Binary') # True if action a is executed at time step i
            
    x_m = {} 
    x_pa = {}
    x_pd = {}
    x_a = {}
    for f in Vp:
        x_m[f] = {}
        x_pa[f] = {}
        x_pd[f] = {}
        x_a[f] = {}
        for i in range(1, T+1):
            x_m[f][i] = LpVariable(f'x_m_{f}_{i}', cat='Binary') # True if fluent is propagated (noop)
            x_pa[f][i] = LpVariable(f'x_pa_{f}_{i}', cat='Binary') # True if an action is executed at i and has f as precondition and doesn't delete it (maintainted/propagated)
            x_pd[f][i] = LpVariable(f'x_pd_{f}_{i}', cat='Binary') # True if an action is executed at i and has f as precondition and delete effect
            x_a[f][i] = LpVariable(f'x_a_{f}_{i}', cat='Binary') # True if an action is executed at i and has f in add effect but not in precondition
    
            
    ###############
    ## OBJECTIVE ##
    ###############
    def obj_nb_actions(m):
        L = []
        for a in actions:
            for t in range(1, T+1):
                L.append(y[a][t])
        m += lpSum(L)
    
    obj_nb_actions(m)
        
        
    #################
    ## CONSTRAINTS ##
    #################
    
    # Initial/Goal State
    for f in Vp:
        if f in Ip:
            # (10)
            x_a[f][0] = 1
        else:
            # (10)
            x_a[f][0] = 0
        x_m[f][0] = 0
        x_pa[f][0] = 0
        x_pd[f][0] = 0
        
    for f in Gp:
        # (9)
        m += x_a[f][T] + x_pa[f][T] + x_m[f][T] >= 1
    
    for f in Vp:
        for i in range(1, T+1):
            # (1)
            m += lpSum(y[a][i] for a in pref[f].difference(delf[f])) >= x_pa[f][i]
            # (2)
            for a in pref[f].difference(delf[f]):
                m += y[a][i] <= x_pa[f][i]
            # (3)
            m += lpSum(y[a][i] for a in addf[f].difference(pref[f])) >= x_a[f][i]
            # (4)
            for a in addf[f].difference(pref[f]):
                m += y[a][i] <= x_a[f][i]
            # (5)
            m += lpSum(y[a][i] for a in pref[f].intersection(delf[f])) == x_pd[f][i]
            
            # (6)(7)
            m += x_a[f][i] + x_m[f][i] + x_pd[f][i] <= 1
            m += x_pa[f][i] + x_m[f][i] + x_pd[f][i] <= 1
            
            # (8)
            m += x_pa[f][i] + x_m[f][i] + x_pd[f][i] <= x_a[f][i-1] + x_pa[f][i-1] + x_m[f][i-1]
            
    
    #############
    ## SOLVING ##
    #############
    m.solve()
    
    
    ############
    ## EXPORT ##
    ############
    export_constraints(m.constraints)

    with open('variables.txt', 'w') as file:
        file.write(f"\n-----------------\n")
        file.write(f"----- t = 0 -----\n")
        file.write(f"-----------------\n")
        file.write(f"\n-- FLUENTS --\n")
        for f in Vp:
            if f!=Vp[0]: file.write('\n')
            file.write(f'x_m_{f}_0 = {x_m[f][0]}\n')
            file.write(f'x_pa_{f}_0 = {x_pa[f][0]}\n')
            file.write(f'x_pd_{f}_0 = {x_pd[f][0]}\n')
            file.write(f'x_a_{f}_0 = {x_a[f][0]}\n')
        
        for t in range(1, T+1):
            file.write(f"\n-----------------\n")
            file.write(f"----- t = {t} -----\n")
            file.write(f"-----------------\n")
                    
            file.write(f"\n-- FLUENTS --\n")
            for f in Vp:
                if f!=Vp[0]: file.write('\n')
                file.write(f'{x_m[f][t]} = {round(x_m[f][t].value())}\n')
                file.write(f'{x_pa[f][t]} = {round(x_pa[f][t].value())}\n')
                file.write(f'{x_pd[f][t]} = {round(x_pd[f][t].value())}\n')
                file.write(f'{x_a[f][t]} = {round(x_a[f][t].value())}\n')
            
            if t!=0:
                file.write(f"\n-- ACTIONS --\n")
                for a in actions:
                    file.write(f'{y[a][t]} = {round(y[a][t].value())}\n')
    return m

import sys
time_horizon = int(sys.argv[1]) if len(sys.argv)>=2 else 2
m = vossen2011_state_change(time_horizon)

######################
## EXTRACT SOLUTION ##
######################

from boxprint import boxprint

boxprint(f'Problem name: {problem_name}')

boxprint(f'Time horizon: {time_horizon}')

if m.status!=1:
    boxprint(f'Problem: {LpStatus[m.status]}', mode='d')
else:
    boxprint(LpSolution[m.sol_status])
    
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
                    
                plan[t].append( action_name )
                
                print(f'{spaces}{action_name}')
                
        if plan[t] == []:
            print('<noop>')
                