from pulp import *
from boxprint import boxprint
from convert_pddl import load_pddl
from datetime import datetime
import time
import click


##################
## LOAD PROBLEM ##
##################
def load_problem():
    global Vp, actions, pre_p, del_p, add_p, problem_name, Ip, Gp
    global pref, addf, delf
    
    t1 = time.time()
    print('Loading problem...')
    
    # from pb_zeno import *
    # from pb_blocks import *
    # from pb_log import *

    # domain_filename = "classical-domains/classical/blocks/domain.pddl"
    # problem_filename = "classical-domains/classical/blocks/probBLOCKS-8-0.pddl"

    # domain_filename = "MILP/propositional_zeno/pzeno_dom.pddl"
    # problem_filename = "MILP/propositional_zeno/pzeno0.pddl"

    # domain_filename = 'classical-domains/classical/zenotravel/domain.pddl'
    # problem_filename = 'classical-domains/classical/zenotravel/pfile5.pddl'

    domain_filename = '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl'
    problem_filename = '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile3.pddl'

    loaded_problem = load_pddl(domain_filename, problem_filename, show=True, solve=False)
    Vp, actions, pre_p, del_p, add_p, problem_name, Ip, Gp = loaded_problem
    Vp, actions, problem_name, Ip, Gp = loaded_problem

    exit()

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
 
    print(f"[Loading Problem: {time.time()-t1:.2f}s]")
 
#################
## BUILD MODEL ##
#################
def build_model_vossen2001_state_change_prop(T, sequential):
    global y, x_m, x_pa, x_pd, x_a
    
    t1 = time.time()
    print('Building model...')

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
            y[a][i] = LpVariable(f'y_{a}_{i}', cat='Binary') # True if action a is executed at time step i
            
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
            
            # (own)
            if sequential:
                m += lpSum(y[a][i] for a in actions) <= 1
      
    print(f"[Building Model: {time.time()-t1:.2f}s]")
    return m      

def build_model_piacentini2018_state_change_prop(T, sequential):
    
    t1 = time.time()
    print('Building model...')

    ###########
    ## MODEL ##
    ###########
    m = LpProblem(sense=LpMinimize)
 

    ###############
    ## VARIABLES ##
    ###############
    u = {}
    for a in actions:
        u[a] = {}
        for i in range(0, T):
            u[a][i] = LpVariable(f'y_{a}_{i}', cat='Binary') # True if action a is executed at time step i
            
    u_m = {} 
    u_pa = {}
    u_pd = {}
    u_a = {}
    for f in Vp:
        u_m[f] = {}
        u_pa[f] = {}
        u_pd[f] = {}
        u_a[f] = {}
        for i in range(0, T+1):
            u_m[f][i] = LpVariable(f'u_m_{f}_{i}', cat='Binary') # True if fluent is propagated (noop)
            u_pa[f][i] = LpVariable(f'u_pa_{f}_{i}', cat='Binary') # True if an action is executed at i and has f as precondition and doesn't delete it (maintainted/propagated)
            u_pd[f][i] = LpVariable(f'u_pd_{f}_{i}', cat='Binary') # True if an action is executed at i and has f as precondition and delete effect
            u_a[f][i] = LpVariable(f'u_a_{f}_{i}', cat='Binary') # True if an action is executed at i and has f in add effect but not in precondition
    
            
    ###############
    ## OBJECTIVE ##
    ###############
    def obj_nb_actions(m):
        L = []
        for a in actions:
            for t in range(0, T):
                L.append(u[a][t])
        m += lpSum(L)
    obj_nb_actions(m)
        
        
    #################
    ## CONSTRAINTS ##
    #################
    
    # Initial/Goal State
    for f in Vp:
        if f in Ip:
            # (10)
            m += u_a[f][0] == 1
        else:
            # (10)
            m += u_a[f][0] == 0
        m += u_m[f][0] == 0
        m += u_pa[f][0] == 0
        m += u_pd[f][0] == 0
        
    for f in Gp:
        # (9)
        m += u_a[f][T] + u_pa[f][T] + u_m[f][T] >= 1
    
    for f in Vp:
        for i in range(0, T):
            m += lpSum(u[a][i] for a in pref[f].difference(delf[f])) >= u_pa[f][i+1]
            for a in pref[f].difference(delf[f]):
                m += u[a][i] <= u_pa[f][i+1]
            m += lpSum(u[a][i] for a in addf[f].difference(pref[f])) >= u_a[f][i+1]
            for a in addf[f].difference(pref[f]):
                m += u[a][i] <= u_a[f][i+1]
            m += lpSum(u[a][i] for a in pref[f].intersection(delf[f])) == u_pd[f][i+1]
            
            m += u_pa[f][i+1] + u_m[f][i+1] + u_pd[f][i+1] <= u_a[f][i] + u_pa[f][i] + u_m[f][i]
            
            # (own)
            if sequential:
                m += lpSum(u[a][i] for a in actions) <= 1
        
        for i in range(0, T+1):
            m += u_a[f][i] + u_m[f][i] + u_pd[f][i] <= 1
            m += u_pa[f][i] + u_m[f][i] + u_pd[f][i] <= 1
      
    print(f"[Building Model: {time.time()-t1:.2f}s]")
    
    global y 
    y = u
    return m      


#############
## SOLVING ##
#############
def solve(m, sol_gap, solver_name="PULP_CBC_CMD"):
    if sol_gap!=None:
        sol_gap = float(sol_gap)
    
    print(f'[{datetime.now()}] Start solving ... ')
    solver = getSolver(solver_name, gapRel=sol_gap)
    t1 = time.time()
    m.solve(solver=solver)
    print(f'elapsed: {time.time()-t1:.2f}s')
    

############
## EXPORT ##
############
def export_internal(m, time_horizon):
    with open('constraints.txt', 'w') as file:
        file.write(f"-----------------------\n")
        file.write(f"----- CONSTRAINTS -----\n")
        file.write(f"-----------------------\n")
        for c in m.constraints:
            file.write(f'{c}: {m.constraints[c]}\n')

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
        
        for t in range(1, time_horizon+1):
            file.write(f"\n-----------------\n")
            file.write(f"----- t = {t} -----\n")
            file.write(f"-----------------\n")
                    
            file.write(f"\n-- FLUENTS --\n")
            for f in Vp:
                if f!=Vp[0]: file.write('\n')
                file.write(f'{x_m[f][t]} = {round(x_m[f][t].value()) if x_m[f][t].value()!=None else None}\n')
                file.write(f'{x_pa[f][t]} = {round(x_pa[f][t].value()) if x_pa[f][t].value()!=None else None}\n')
                file.write(f'{x_pd[f][t]} = {round(x_pd[f][t].value()) if x_pd[f][t].value()!=None else None}\n')
                file.write(f'{x_a[f][t]} = {round(x_a[f][t].value()) if x_a[f][t].value()!=None else None}\n')
            
            if t!=0:
                file.write(f"\n-- ACTIONS --\n")
                for a in actions:
                    file.write(f'{y[a][t]} = {round(y[a][t].value())  if y[a][t].value()!=None else None}\n')
    return m


######################
## EXTRACT SOLUTION ##
######################
def extract_solution(m, time_horizon):

    boxprint(f'Problem name: {problem_name}\nNb Constraints: {m.numConstraints()}\nNb Variables: {m.numVariables()}')

    boxprint(f'Time horizon: {time_horizon}')

    if m.status!=1:
        boxprint(f'Problem: {LpStatus[m.status]}', mode='d')
    else:
        boxprint(LpSolution[m.sol_status])
        
        plan = {}
        print("plan:")
        for t in range(0, time_horizon): # for piacentini
        # for t in range(1, time_horizon+1): # for vossen
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
                

##########
## MAIN ##
##########
@click.command()
@click.option('--tmin', 'T_min', default=1)
@click.option('--tmax', 'T_max', default=200)
@click.option('-t', '--timehorizon', 'T_user', default=None)
@click.option('--gap', 'sol_gap', default=None)
@click.option('--seq', 'sequential', is_flag=True, default=False)
@click.option('--export', 'export', is_flag=True, default=False)
def main(T_min, T_max, T_user, sol_gap, sequential, export):
    load_problem()
    
    if T_user!=None:
        T_min = T_max = int(T_user)
        
    solved = False
    T = T_min
    while not solved and T<=T_max:
        boxprint(f"Solving with T={T}")
        
        # m = build_model_vossen2001_state_change_prop(T, sequential)
        m = build_model_piacentini2018_state_change_prop(T, sequential)
        
        solve(m, sol_gap, solver_name='GUROBI') # solvers: CPLEX_PY, GUROBI, PULP_CBC_CMD
        
        if m.status==1:
            solved=True
        elif T==T_max:
            raise Exception(f"Max time horizon ({T_max}) reached.")
        else: 
            T+=1
            
    if export:
        export_internal(m, T)
        
    extract_solution(m, T)
if __name__=='__main__':
    main()