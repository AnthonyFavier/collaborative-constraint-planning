from pulp import *
from MILP.boxprint import boxprint
from MILP.convert_pddl import load_pddl
from datetime import datetime
import time
import click
import math


##################
## LOAD PROBLEM ##
##################
def load_problem(n_problem):
    global problem_name, Vp, Vn, actions, I, Gp, Gn
    global w_c_v, w_0_c, k_v_a_w, k_v_a
    global pref, addf, delf, se, le


    t1 = time.time()
    boxprint('Loading problem')

    if n_problem!=None:
        domain_filename = 'classical-domains/classical/zenotravel/domain.pddl'  
        problem_filename = f'classical-domains/classical/zenotravel/pfile{n_problem}.pddl'
    else:
        # domain_filename = "classical-domains/classical/blocks/domain.pddl"
        # problem_filename = "classical-domains/classical/blocks/probBLOCKS-8-0.pddl"

        # domain_filename = "MILP/propositional_zeno/pzeno_dom.pddl"
        # problem_filename = "MILP/propositional_zeno/pzeno0.pddl"

        domain_filename = 'classical-domains/classical/zenotravel/domain.pddl'
        problem_filename = 'classical-domains/classical/zenotravel/pfile3.pddl'


        # domain_filename = '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl'

        # problem_filename = '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile0.pddl'
        # problem_filename = '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile1.pddl'
        # problem_filename = '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile3.pddl'
        # problem_filename = '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile4.pddl'
        # problem_filename = '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile5.pddl'
        # problem_filename = '/home/afavier/ws/CAI/NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile13.pddl'

        # domain_filename = 'MILP/simple_num/domain.pddl'
        # problem_filename = 'MILP/simple_num/pfile1.pddl'

    print('domain_filename=', domain_filename)
    print('problem_filename=', problem_filename)

    loaded_problem = load_pddl(domain_filename, problem_filename, show=False, solve=False)

    # unpacking
    problem_name, V, actions, I, G, num_param, actionsAffectingF = loaded_problem
    Vp, Vn = V # Fluents
    Gp, Gn = G # Goal state
    w_c_v, w_0_c, k_v_a_w, k_v_a = num_param # Parameters describing numerical preconditions, goals, and effects
    pref, addf, delf, se, le = actionsAffectingF # Actions affecting given fluent

    # TODO: Merge both functions (convert_pddl and this one)

    global g_loading_problem_time
    g_loading_problem_time = time.time()-t1
    print(f"[Loading Problem: {g_loading_problem_time:.2f}s]")

#################
## BUILD MODEL ##
#################
def build_model_vossen2001_state_change_prop(T, sequential):
    global u
    global x_m, x_pa, x_pd, x_a
    
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
        for i in range(1, T+1):
            u[a][i] = LpVariable(f'u_{a}_{i}', cat='Binary') # True if action a is executed at time step i
            
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
                L.append(u[a][t])
        m += lpSum(L)
    
    obj_nb_actions(m)
        
        
    #################
    ## CONSTRAINTS ##
    #################
    
    # Initial/Goal State
    for f in Vp:
        # (10)
        x_a[f][0] = I[f]
        x_m[f][0] = 0
        x_pa[f][0] = 0
        x_pd[f][0] = 0
        
    for f in Gp:
        # (9)
        m += x_a[f][T] + x_pa[f][T] + x_m[f][T] >= 1
    
    for f in Vp:
        for i in range(1, T+1):
            # (1)
            m += lpSum(u[a][i] for a in pref[f].difference(delf[f])) >= x_pa[f][i]
            # (2)
            for a in pref[f].difference(delf[f]):
                m += u[a][i] <= x_pa[f][i]
            # (3)
            m += lpSum(u[a][i] for a in addf[f].difference(pref[f])) >= x_a[f][i]
            # (4)
            for a in addf[f].difference(pref[f]):
                m += u[a][i] <= x_a[f][i]
            # (5)
            m += lpSum(u[a][i] for a in pref[f].intersection(delf[f])) == x_pd[f][i]
            
            # (6)(7)
            m += x_a[f][i] + x_m[f][i] + x_pd[f][i] <= 1
            m += x_pa[f][i] + x_m[f][i] + x_pd[f][i] <= 1
            
            # (8)
            m += x_pa[f][i] + x_m[f][i] + x_pd[f][i] <= x_a[f][i-1] + x_pa[f][i-1] + x_m[f][i-1]
            
            # (own)
            if sequential:
                m += lpSum(u[a][i] for a in actions) <= 1
      
    global g_building_model_time
    g_building_model_time = time.time()-t1
    print(f"[Building Model: {g_building_model_time:.2f}s]")
    return m 

def build_model_piacentini2018_state_change_prop(T, sequential):
    global u 
    
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
            u[a][i] = LpVariable(f'u_{a}_{i}', cat='Binary') # True if action a is executed at time step i
            
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
        # (10)
        m += u_a[f][0] == I[f]
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
      
    global g_building_model_time
    g_building_model_time = time.time()-t1
    print(f"[Building Model: {g_building_model_time:.2f}s]")
    return m 

###############################

def compute_m_constants(T):

    # compute m_v_t, M_v_t
    m_v_t = {}
    M_v_t = {}
    for v in Vn:
        m_v_t[v] = {}
        M_v_t[v] = {}
        for t in range(0, T+1):
            if t==0:
                m_v_t[v][t] = I[v]
                M_v_t[v][t] = I[v]

            else:
                min_a_bot = min(
                    sum(k_v_a_w[v][a][w] * m_v_t[w][t-1] for w in Vn if k_v_a_w[v][a][w] > 0)\
                    + sum(k_v_a_w[v][a][w] * M_v_t[w][t-1] for w in Vn if k_v_a_w[v][a][w] < 0)\
                    for a in le[v]
                ) if le[v] else math.inf

                max_a_top = max(
                    sum(k_v_a_w[v][a][w] * M_v_t[w][t-1] for w in Vn if k_v_a_w[v][a][w] > 0) \
                    + sum(k_v_a_w[v][a][w] * m_v_t[w][t-1] for w in Vn if k_v_a_w[v][a][w] < 0)\
                    for a in le[v]
                ) if le[v] else -math.inf

                m_v_t[v][t] = min(
                    m_v_t[v][t-1] + sum(k_v_a[v][a] for a in se[v] if k_v_a[v][a] < 0),
                    min_a_bot
                )
 
                M_v_t[v][t] = max(
                    M_v_t[v][t-1] + sum(k_v_a[v][a] for a in se[v] if k_v_a[v][a] > 0),
                    max_a_top
                )

    # Compute m_c_t
    m_c_t = {}
    for a in actions:
        for c in actions[a]['pre_n']:
            m_c_t[c] = {}
            for t in range(0, T):
                m_c_t[c][t] = sum(w_c_v[c][v] * M_v_t[v][t] for v in Vn if w_c_v[c][v]<0)\
                + sum(w_c_v[c][v] * m_v_t[v][t] for v in Vn if w_c_v[c][v]>0)\
                + w_0_c[c]

    # Compute m/M_step_c_t
    M_step_v_t = {}
    m_step_v_t = {}
    for v in Vn:
        M_step_v_t[v] = {}
        m_step_v_t[v] = {}
        for t in range(0, T+1):
            if t==0:
                M_step_v_t[v][t] = M_v_t[v][t]
                m_step_v_t[v][t] = m_v_t[v][t]
            else:
                M_step_v_t[v][t] = M_v_t[v][t] - m_v_t[v][t-1]
                m_step_v_t[v][t] = m_v_t[v][t] - M_v_t[v][t-1]

    # Compute m/M_v_a_t
    M_v_a_t = {}
    m_v_a_t = {}
    for v in Vn:
        M_v_a_t[v] = {}
        m_v_a_t[v] = {}
        for a in le[v]:
            M_v_a_t[v][a] = {}
            m_v_a_t[v][a] = {}
            for t in range(0, T+1):
                if t==0:
                    M_v_a_t[v][a][t] = M_v_t[v][t]
                    m_v_a_t[v][a][t] = m_v_t[v][t]
                else:
                    M_v_a_t[v][a][t] = M_v_t[v][t]\
                    - sum(k_v_a_w[v][a][w] * M_v_t[v][t-1] for w in Vn if k_v_a_w[v][a][w]<0)\
                    + sum(k_v_a_w[v][a][w] * m_v_t[v][t-1] for w in Vn if k_v_a_w[v][a][w]>0)\
                    - k_v_a[v][a]
                    
                    m_v_a_t[v][a][t] = m_v_t[v][t]\
                    - sum(k_v_a_w[v][a][w] * M_v_t[v][t-1] for w in Vn if k_v_a_w[v][a][w]>0)\
                    + sum(k_v_a_w[v][a][w] * m_v_t[v][t-1] for w in Vn if k_v_a_w[v][a][w]<0)\
                    - k_v_a[v][a]

    return m_c_t, m_step_v_t, M_step_v_t, m_v_a_t, M_v_a_t

def build_nmutex():
    def are_nmutex(a1, a2):
        if a1 != a2:
            for e1 in actions[a1]['num']:
                v = e1.split(':=')[0].strip()

                # check (i): v is assigned by a1 and is also used in one of the numeric effects of a2
                for e2 in actions[a2]['num']:
                    # if v in e2: 
                        # return True

                    # paper exact below
                    xi = e2.split(':=')[1].strip()
                    if v in xi:
                        return True

                # check (ii): v is assigned by a1 and is also part of a precondition of a2
                for pre in actions[a2]['pre_n']:
                    # if v in pre:
                    #     return True

                    # paper exact below
                    if w_c_v[pre][v]!=0:
                        return True

        return False

    nmutex = {}
    for a1 in actions:
        nmutex[a1] = set()
        for a2 in actions:
            if are_nmutex(a1, a2):
                nmutex[a1].add(a2)

    return nmutex

def get_op(c):
    rel_ops = ['>=', '>', '==', None]
    for op in rel_ops:
        if op in c:
            break
    assert op != None
    return op
                
def build_model_piacentini2018_state_change_numeric(T, sequential):
    global u

    m_c_t, m_step_v_t, M_step_v_t, m_v_a_t, M_v_a_t = compute_m_constants(T)
    nmutex = build_nmutex()

    t1 = time.time()
    print('Building model...')

    ###########
    ## MODEL ##
    ###########
    m = LpProblem(sense=LpMinimize)
 

    ###############
    ## VARIABLES ##
    ###############
    # Action variables
    u = {}
    for a in actions:
        u[a] = {}
        for t in range(0, T):
            u[a][t] = LpVariable(f'u_{a}_{t}', cat='Binary') # True if action a is executed at time step t
            
    # Propositional fluent state change variables
    u_m = {} 
    u_pa = {}
    u_pd = {}
    u_a = {}
    for p in Vp:
        u_m[p] = {}
        u_pa[p] = {}
        u_pd[p] = {}
        u_a[p] = {}
        for t in range(0, T+1):
            u_m[p][t] = LpVariable(f'u_m_{p}_{t}', cat='Binary') # True if fluent is propagated (noop)
            u_pa[p][t] = LpVariable(f'u_pa_{p}_{t}', cat='Binary') # True if an action is executed at t and has f as precondition and doesn't delete it (maintainted/propagated)
            u_pd[p][t] = LpVariable(f'u_pd_{p}_{t}', cat='Binary') # True if an action is executed at t and has f as precondition and delete effect
            u_a[p][t] = LpVariable(f'u_a_{p}_{t}', cat='Binary') # True if an action is executed at t and has f in add effect but not in precondition
    
    # Numeric fluent value variables
    y_v_t = {}
    for v in Vn:
        y_v_t[v] = {}
        for t in range(0, T+1):
            y_v_t[v][t] = LpVariable(f'y_v_t_{v}_{t}', cat='Continuous') # value of fluent v at time step t
            

    ###############
    ## OBJECTIVE ##
    ###############
    def obj_nb_actions(m):
        L = []
        for a in actions:
            for t in range(0, T):
                cost_a = 1
                L.append(cost_a * u[a][t])
        m += lpSum(L)
    obj_nb_actions(m)
        
        
    ###############################
    ## CONSTRAINTS PROPOSITIONAL ##
    ###############################
    
    # Initial State
    for p in Vp:
        m += u_a[p][0] == I[p] #(1)
        m += u_m[p][0] == 0 #?
        m += u_pa[p][0] == 0 #?
        m += u_pd[p][0] == 0 #?
        
    # Goal State
    for p in Gp:
        m += u_a[p][T] + u_pa[p][T] + u_m[p][T] >= 1 #(2)
    
    for p in Vp:
        for t in range(0, T):
            m += lpSum(u[a][t] for a in pref[p].difference(delf[p])) >= u_pa[p][t+1] #(3)
            for a in pref[p].difference(delf[p]):
                m += u[a][t] <= u_pa[p][t+1] #(6)

            m += lpSum(u[a][t] for a in addf[p].difference(pref[p])) >= u_a[p][t+1] #(4)
            for a in addf[p].difference(pref[p]):
                m += u[a][t] <= u_a[p][t+1] #(7)
                
            m += lpSum(u[a][t] for a in pref[p].intersection(delf[p])) == u_pd[p][t+1] #(5)
            
            m += u_pa[p][t+1] + u_m[p][t+1] + u_pd[p][t+1] <= u_a[p][t] + u_pa[p][t] + u_m[p][t] #(11)
            
        for t in range(0, T+1):
            m += u_a[p][t] + u_m[p][t] + u_pd[p][t] <= 1 #(8)
            m += u_pa[p][t] + u_m[p][t] + u_pd[p][t] <= 1 #(9)


    #########################
    ## CONSTRAINTS NUMERIC ##
    #########################

    for v in Vn:
        m += y_v_t[v][0] == I[v] #(12)
        # y_v_t[v][0] = I[v] #(12)
    
    for c in Gn: #(13)
        op = get_op(c)
        if op=='>=':
            m += lpSum(w_c_v[c][v] * y_v_t[v][T] for v in Vn) + w_0_c[c] >= 0
        elif op=='==':
            m += lpSum(w_c_v[c][v] * y_v_t[v][T] for v in Vn) + w_0_c[c] == 0
        else:
            raise Exception('Numeric goal constraint: op not supported')

    for a in actions: #(14)
        for c in actions[a]['pre_n']:
            for t in range(0, T):
                op = get_op(c)
                if op=='>=':
                    m += sum(w_c_v[c][v] * y_v_t[v][t] for v in Vn) + w_0_c[c] >= m_c_t[c][t]*(1-u[a][t])
                if op=='==':
                    m += sum(w_c_v[c][v] * y_v_t[v][t] for v in Vn) + w_0_c[c] == m_c_t[c][t]*(1-u[a][t])

    for v in Vn: #(15)
        for t in range(0, T):
            m += y_v_t[v][t+1] <= y_v_t[v][t]\
            + sum(k_v_a[v][a] * u[a][t] for a in se[v])\
            + M_step_v_t[v][t+1] * sum(u[a][t] for a in le[v])

    for v in Vn: #(16)
        for t in range(0, T):
            m += y_v_t[v][t+1] >= y_v_t[v][t]\
            + sum(k_v_a[v][a] * u[a][t] for a in se[v])\
            + m_step_v_t[v][t+1] * sum(u[a][t] for a in le[v])

    for v in Vn: #(17)
        for a in le[v]:
            for t in range(0, T):
                m += y_v_t[v][t+1] - sum(k_v_a_w[v][a][w] * y_v_t[w][t] for w in Vn) <=\
                k_v_a[v][a] + M_v_a_t[v][a][t+1] * (1-u[a][t])

    for v in Vn: #(18)
        for a in le[v]:
            for t in range(0, T):
                m += y_v_t[v][t+1] - sum(k_v_a_w[v][a][w] * y_v_t[w][t] for w in Vn) >=\
                k_v_a[v][a] + m_v_a_t[v][a][t+1] * (1-u[a][t])

    for a1 in actions: #(19)
        for a2 in nmutex[a1]:
            for t in range(0, T):
                m += u[a1][t] + u[a2][t] <= 1

    ############################
    ## ADDITIONAL CONSTRAINTS ##
    ############################

    # (own)
    if sequential:
        for i in range (0, T):
            m += lpSum(u[a][i] for a in actions) <= 1

    #########################
    
    global g_building_model_time
    g_building_model_time = time.time()-t1
    print(f"[Building Model: {g_building_model_time:.2f}s]")
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

    global g_solving_time
    g_solving_time = time.time()-t1
    print(f'elapsed: {g_solving_time:.2f}s')
    

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
                    file.write(f'{u[a][t]} = {round(u[a][t].value())  if u[a][t].value()!=None else None}\n')
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
        # for t in range(1, time_horizon+1): # for vossen
        for t in range(0, time_horizon): # for piacentini
            time_stamp_txt = f'{t}: '
            print(time_stamp_txt, end='')
            for a in u:
                if t not in plan:
                    plan[t] = []
                    
                if u[a][t].value():
                    spaces = '' if len(plan[t])==0 else ' '*(len(time_stamp_txt))
                    
                    action_name = str(u[a][t])
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
@click.option('--n_problem', 'n_problem', default=None)
def mainCLI(T_min, T_max, T_user, sol_gap, sequential, export, n_problem):
    main(T_min, T_max, T_user, sol_gap, sequential, export, n_problem)
def main(T_min, T_max, T_user, sol_gap, sequential, export, n_problem):
    t_start = time.time()

    load_problem(n_problem)
    
    if T_user!=None:
        T_min = T_max = int(T_user)
    
    solved = False
    T = T_min
    while not solved and T<=T_max:
        boxprint(f"Solving with T={T}")
        
        # m = build_model_vossen2001_state_change_prop(T, sequential)
        # m = build_model_piacentini2018_state_change_prop(T, sequential)
        m = build_model_piacentini2018_state_change_numeric(T, sequential)

        solve(m, sol_gap, solver_name='GUROBI') # solvers: CPLEX_PY, GUROBI, PULP_CBC_CMD
        
        with open('output.txt', 'w') as f:
            txt = ''
            txt += 'Constraints:\n'
            for k,c in m.constraints.items():
                txt += f'{k} = {c}\n'
            txt += '\nVariables:\n'
            for v in m._variables:
                txt += f'{v} = {v.varValue}\n'
            f.write(txt)
            
        if m.status==1:
            solved=True
            global g_total_solving_time
            g_total_solving_time = time.time()-t_start
        elif T==T_max:
            if T_user!=None:
                raise Exception(f"No solution found for time horizon ({T_user}).")
                break
            else:
                raise Exception(f"Max time horizon ({T_max}) reached.")
        else: 
            T+=1
            
    if export:
        export_internal(m, T)
        
    extract_solution(m, T)

    # show times
    boxprint(f'\
Loading problem: {g_loading_problem_time:.2f}s\n\
Building model: {g_building_model_time:.2f}s\n\
Solving instance: {g_solving_time:.2f}s\n\
Total time: {g_total_solving_time:.2f}s\
')

if __name__=='__main__':
    mainCLI()