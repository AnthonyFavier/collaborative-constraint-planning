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
def get_problem_filenames(domain_name, i_instance, classical=False):
    """
    ** Numerical ***
    block-grouping, counters, delivery, drone, expedition, ext-plant-watering, farmland, fo-counters, fo-farmland, fo-sailing, hydropower, markettrader, mprime, pathwaysmetric, rover, sailing, settlersnumeric, sugar, tpp, zenotravel

    ** Classical **
    agricola-opt18, caldera-sat18, elevators-00-adl, floortile-sat14-strips, maintenance-sat14-adl, openstacks, organic-synthesis-split-opt18, pegsol-sat11-strips, scanalyzer-08-strips, spider-sat18, transport-opt14-strips, woodworking-opt11-strips, agricola-sat18, caldera-split-opt18, elevators-00-full, freecell, miconic, openstacks-opt08-adl, organic-synthesis-split-sat18, petri-net-alignment-opt18, scanalyzer-opt11-strips, storage, transport-sat08-strips, woodworking-sat08-strips, airport, caldera-split-sat18, elevators-00-strips, fridge, miconic-fulladl, openstacks-opt08-strips, parcprinter-08-strips, petri-net-alignment-sat18, scanalyzer-sat11-strips, termes-opt18, transport-sat11-strips, woodworking-sat11-strips, airport-adl, cavediving, elevators-opt08-strips, ged-opt14-strips, miconic-simpleadl, openstacks-opt11-strips, parcprinter-opt11-strips, philosophers, schedule, termes-sat18, transport-sat14-strips, zenotravel, assembly, childsnack-opt14-strips, elevators-opt11-strips, ged-sat14-strips, movie, openstacks-opt14-strips, parcprinter-sat11-strips, pipesworld-06, settlers-opt18, tetris-opt14-strips, trucks, barman-opt11-strips, childsnack-sat14-strips, elevators-sat08-strips, grid, mprime, openstacks-sat08-adl, parking-opt11-strips, pipesworld-notankage, settlers-sat18, tetris-sat14-strips, trucks-strips, barman-opt14-strips, citycar-opt14-adl, elevators-sat11-strips, gripper, mystery, openstacks-sat08-strips, parking-opt14-strips, pipesworld-tankage, snake-opt18, thoughtful-sat14-strips, tsp, barman-sat11-strips, citycar-sat14-adl, ferry, hanoi, no-mprime, openstacks-sat11-strips, parking-sat11-strips, psr-large, snake-sat18, tidybot-opt11-strips, tyreworld, barman-sat14-strips, cybersec, flashfill-opt18, hiking-opt14-strips, no-mystery, openstacks-sat14-strips, parking-sat14-strips, psr-middle, sokoban-opt08-strips, tidybot-opt14-strips, visitall-opt11-strips, blocks, data-network-opt18, flashfill-sat18, hiking-sat14-strips, nomystery-opt11-strips, openstacks-strips, pathways, psr-small, sokoban-opt11-strips, tidybot-sat11-strips, visitall-opt14-strips, blocks-3op, data-network-sat18, floortile-opt11-strips, logistics00, nomystery-sat11-strips, optical-telegraphs, pathways-noneg, rovers, sokoban-sat08-strips, tpp, visitall-sat11-strips, briefcaseworld, depot, floortile-opt14-strips, logistics98, nurikabe-opt18, organic-synthesis-opt18, pegsol-08-strips, rovers-02, sokoban-sat11-strips, transport-opt08-strips, visitall-sat14-strips, caldera-opt18, driverlog, floortile-sat11-strips, maintenance-opt14-adl, nurikabe-sat18, organic-synthesis-sat18, pegsol-opt11-strips, satellite, spider-opt18, transport-opt11-strips, woodworking-opt08-strips
    """

    if classical:
        domain_filename = f'classical-domains/classical/{domain_name}/domain.pddl'  
        problem_filename = f'classical-domains/classical/{domain_name}/pfile{i_instance}.pddl'

    else:
        domain_filename = f'ipc2023-dataset/{domain_name}/domain.pddl'  
        problem_filename = f'ipc2023-dataset/{domain_name}/instances/pfile{i_instance}.pddl'

    return domain_filename, problem_filename

class MILP_data_extracted:
    def __init__(self, data_extracted):
        V, actions, I, G, num_param, actionsAffectingF = data_extracted
        Vp, Vn = V # Fluents
        Gp, Gn = G # Goal state
        w_c_v, w_0_c, k_v_a_w, k_v_a = num_param # Parameters describing numerical preconditions, goals, and effects
        pref, addf, delf, se, le = actionsAffectingF # Actions affecting given fluent

        self.actions = actions
        self.Vp = Vp
        self.Vn = Vn
        self.I = I
        self.Gp = Gp
        self.Gn = Gn
        self.w_c_v = w_c_v
        self.w_0_c = w_0_c
        self.k_v_a_w = k_v_a_w
        self.k_v_a = k_v_a
        self.pref = pref
        self.addf = addf
        self.delf = delf
        self.se = se
        self.le = le

#################
## BUILD MODEL ##
#################
def compute_m_constants(M: MILP_data_extracted, T):

    # compute m_v_t, M_v_t
    global M_v_t, m_v_t
    m_v_t = {}
    M_v_t = {}
    for v in M.Vn:
        m_v_t[v] = {}
        M_v_t[v] = {}
        for t in range(0, T+1):
            if t==0:
                m_v_t[v][t] = M.I[v]
                M_v_t[v][t] = M.I[v]

            else:
                min_a_bot = min(
                    sum(M.k_v_a_w[v][a][w] * m_v_t[w][t-1] for w in M.Vn if M.k_v_a_w[v][a][w] > 0)\
                    + sum(M.k_v_a_w[v][a][w] * M_v_t[w][t-1] for w in M.Vn if M.k_v_a_w[v][a][w] < 0)\
                    for a in M.le[v]
                ) if M.le[v] else math.inf

                max_a_top = max(
                    sum(M.k_v_a_w[v][a][w] * M_v_t[w][t-1] for w in M.Vn if M.k_v_a_w[v][a][w] > 0) \
                    + sum(M.k_v_a_w[v][a][w] * m_v_t[w][t-1] for w in M.Vn if M.k_v_a_w[v][a][w] < 0)\
                    for a in M.le[v]
                ) if M.le[v] else -math.inf

                m_v_t[v][t] = min(
                    m_v_t[v][t-1] + sum(M.k_v_a[v][a] for a in M.se[v] if M.k_v_a[v][a] < 0),
                    min_a_bot
                )
 
                M_v_t[v][t] = max(
                    M_v_t[v][t-1] + sum(M.k_v_a[v][a] for a in M.se[v] if M.k_v_a[v][a] > 0),
                    max_a_top
                )

    # Compute m_c_t
    m_c_t = {}
    for a in M.actions:
        for c in M.actions[a]['pre_n']:
            m_c_t[c] = {}
            for t in range(0, T):
                m_c_t[c][t] = sum(M.w_c_v[c][v] * M_v_t[v][t] for v in M.Vn if M.w_c_v[c][v]<0)\
                + sum(M.w_c_v[c][v] * m_v_t[v][t] for v in M.Vn if M.w_c_v[c][v]>0)\
                + M.w_0_c[c]

    # Compute m/M_step_c_t
    M_step_v_t = {}
    m_step_v_t = {}
    for v in M.Vn:
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
    for v in M.Vn:
        M_v_a_t[v] = {}
        m_v_a_t[v] = {}
        for a in M.le[v]:
            M_v_a_t[v][a] = {}
            m_v_a_t[v][a] = {}
            for t in range(0, T+1):
                if t==0:
                    M_v_a_t[v][a][t] = M_v_t[v][t]
                    m_v_a_t[v][a][t] = m_v_t[v][t]
                else:
                    M_v_a_t[v][a][t] = M_v_t[v][t]\
                    - sum(M.k_v_a_w[v][a][w] * M_v_t[v][t-1] for w in M.Vn if M.k_v_a_w[v][a][w]<0)\
                    + sum(M.k_v_a_w[v][a][w] * m_v_t[v][t-1] for w in M.Vn if M.k_v_a_w[v][a][w]>0)\
                    - M.k_v_a[v][a]
                    
                    m_v_a_t[v][a][t] = m_v_t[v][t]\
                    - sum(M.k_v_a_w[v][a][w] * M_v_t[v][t-1] for w in M.Vn if M.k_v_a_w[v][a][w]>0)\
                    + sum(M.k_v_a_w[v][a][w] * m_v_t[v][t-1] for w in M.Vn if M.k_v_a_w[v][a][w]<0)\
                    - M.k_v_a[v][a]

    return m_c_t, m_step_v_t, M_step_v_t, m_v_a_t, M_v_a_t

def build_nmutex(M: MILP_data_extracted):
    def are_nmutex(a1, a2):
        if a1 != a2:
            for e1 in M.actions[a1]['num']:
                v = e1.split(':=')[0].strip()

                # check (i): v is assigned by a1 and is also used in one of the numeric effects of a2
                for e2 in M.actions[a2]['num']:
                    # if v in e2: 
                        # return True

                    # paper exact below
                    xi = e2.split(':=')[1].strip()
                    if v in xi:
                        return True

                # check (ii): v is assigned by a1 and is also part of a precondition of a2
                for pre in M.actions[a2]['pre_n']:
                    # if v in pre:
                    #     return True

                    # paper exact below
                    if M.w_c_v[pre][v]!=0:
                        return True

        return False

    nmutex = {}
    for a1 in M.actions:
        nmutex[a1] = set()
        for a2 in M.actions:
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
                
def build_model_piacentini2018_state_change_numeric(M: MILP_data_extracted, T, sequential):
    global u

    m_c_t, m_step_v_t, M_step_v_t, m_v_a_t, M_v_a_t = compute_m_constants(M, T)
    nmutex = build_nmutex(M)

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
    for a in M.actions:
        u[a] = {}
        for t in range(0, T):
            u[a][t] = LpVariable(f'u_{a}_{t}', cat='Binary') # True if action a is executed at time step t
            
    # Propositional fluent state change variables
    u_m = {} 
    u_pa = {}
    u_pd = {}
    u_a = {}
    for p in M.Vp:
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
    for v in M.Vn:
        y_v_t[v] = {}
        for t in range(0, T+1):
            y_v_t[v][t] = LpVariable(f'y_v_t_{v}_{t}', cat='Continuous') # value of fluent v at time step t
            

    ###############
    ## OBJECTIVE ##
    ###############
    def obj_nb_actions(m):
        L = []
        for a in M.actions:
            for t in range(0, T):
                cost_a = 1
                L.append(cost_a * u[a][t])
        m += lpSum(L)
    obj_nb_actions(m)
        
        
    ###############################
    ## CONSTRAINTS PROPOSITIONAL ##
    ###############################
    
    # Initial State
    for p in M.Vp:
        m += u_a[p][0] == M.I[p] #(1)
        m += u_m[p][0] == 0 
        m += u_pa[p][0] == 0 
        m += u_pd[p][0] == 0 
        
    # Goal State
    for p in M.Gp:
        m += u_a[p][T] + u_pa[p][T] + u_m[p][T] >= 1 #(2)
    
    for p in M.Vp:
        for t in range(0, T):
            m += lpSum(u[a][t] for a in M.pref[p].difference(M.delf[p])) >= u_pa[p][t+1] #(3)
            for a in M.pref[p].difference(M.delf[p]):
                m += u[a][t] <= u_pa[p][t+1] #(6)

            m += lpSum(u[a][t] for a in M.addf[p].difference(M.pref[p])) >= u_a[p][t+1] #(4)
            for a in M.addf[p].difference(M.pref[p]):
                m += u[a][t] <= u_a[p][t+1] #(7)
                
            m += lpSum(u[a][t] for a in M.pref[p].intersection(M.delf[p])) == u_pd[p][t+1] #(5)
            
            m += u_pa[p][t+1] + u_m[p][t+1] + u_pd[p][t+1] <= u_a[p][t] + u_pa[p][t] + u_m[p][t] #(11)
            
        for t in range(0, T+1):
            m += u_a[p][t] + u_m[p][t] + u_pd[p][t] <= 1 #(8)
            m += u_pa[p][t] + u_m[p][t] + u_pd[p][t] <= 1 #(9)

    # Add (10) back?
    for a1_name in M.actions:
        for a2_name in M.actions:
            if a1_name!=a2_name:
                a1 = M.actions[a1_name]
                a2 = M.actions[a2_name]
                # set operators: | union, & intersection, - difference
                if a1['del'] & (a2['add'] | a2['pre_p']) != set():
                    for t in range(0, T):
                        u[a1_name][t] + u[a2_name][t] <= 1

    #########################
    ## CONSTRAINTS NUMERIC ##
    #########################

    for v in M.Vn:
        m += y_v_t[v][0] == M.I[v] #(12)
    
    for c in M.Gn: #(13)
        op = get_op(c)
        if op=='>=':
            m += lpSum(M.w_c_v[c][v] * y_v_t[v][T] for v in M.Vn) + M.w_0_c[c] >= 0
        elif op=='==':
            m += lpSum(M.w_c_v[c][v] * y_v_t[v][T] for v in M.Vn) + M.w_0_c[c] == 0
        else:
            raise Exception('Numeric goal constraint: op not supported')

    for a in M.actions: #(14)
        for c in M.actions[a]['pre_n']:
            for t in range(0, T):
                op = get_op(c)
                if op=='>=':
                    m += sum(M.w_c_v[c][v] * y_v_t[v][t] for v in M.Vn) + M.w_0_c[c] >= m_c_t[c][t]*(1-u[a][t])
                if op=='==':
                    m += sum(M.w_c_v[c][v] * y_v_t[v][t] for v in M.Vn) + M.w_0_c[c] == m_c_t[c][t]*(1-u[a][t])

    for v in M.Vn: #(15)
        for t in range(0, T):
            m += y_v_t[v][t+1] <= y_v_t[v][t]\
            + sum(M.k_v_a[v][a] * u[a][t] for a in M.se[v])\
            + M_step_v_t[v][t+1] * sum(u[a][t] for a in M.le[v])

    for v in M.Vn: #(16)
        for t in range(0, T):
            m += y_v_t[v][t+1] >= y_v_t[v][t]\
            + sum(M.k_v_a[v][a] * u[a][t] for a in M.se[v])\
            + m_step_v_t[v][t+1] * sum(u[a][t] for a in M.le[v])

    for v in M.Vn: #(17)
        for a in M.le[v]:
            for t in range(0, T):
                m += y_v_t[v][t+1] - sum(M.k_v_a_w[v][a][w] * y_v_t[w][t] for w in M.Vn) <=\
                M.k_v_a[v][a] + M_v_a_t[v][a][t+1] * (1-u[a][t])

    for v in M.Vn: #(18)
        for a in M.le[v]:
            for t in range(0, T):
                m += y_v_t[v][t+1] - sum(M.k_v_a_w[v][a][w] * y_v_t[w][t] for w in M.Vn) >=\
                M.k_v_a[v][a] + m_v_a_t[v][a][t+1] * (1-u[a][t])

    for a1 in M.actions: #(19)
        for a2 in nmutex[a1]:
            for t in range(0, T):
                m += u[a1][t] + u[a2][t] <= 1


    ############################
    ## ADDITIONAL CONSTRAINTS ##
    ############################

    # (own)
    if sequential:
        for t in range (0, T):
            m += lpSum(u[a][t] for a in M.actions) <= 1

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
    

######################
## EXTRACT SOLUTION ##
######################
def extract_solution(domain_filename, problem_filename, m, time_horizon):

    boxprint(f'{domain_filename}\n{problem_filename}\nNb Constraints: {m.numConstraints()}\nNb Variables: {m.numVariables()}')

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

    return plan


##############
## UP SOLVE ##
##############
def up_solve(domain_name=None, i_instance=None, domain_filename=None, problem_filename=None, classical=False):
    t_total_1 = time.time()

    if domain_name!=None and i_instance!=None:
        domain_filename, problem_filename = get_problem_filenames(domain_name, i_instance, classical=classical)
    problem_name, up_problem, milp_problem = load_pddl(domain_filename, problem_filename, no_data_extraction=True)

    boxprint(f"UP Solving")

    t_solving_1 = time.time()
    with OneshotPlanner(problem_kind=up_problem.kind, 
        optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY
    ) as planner:
        result = planner.solve(up_problem)
        up_solving_time = time.time()-t_solving_1
        plan_str = []
        for t, a in enumerate(str(result.plan).splitlines()[1:]):
            a = a.strip().replace('(','_').replace(')','').replace(', ','_')
            plan_str.append(f'{t}: {a}')
        plan_str = ' | '.join(plan_str)
        plan_length = len(result.plan.actions)

    total_time = time.time()-t_total_1

    from MILP.convert_pddl import g_loading_problem_time
    return plan_str, plan_length, (g_loading_problem_time, up_solving_time, total_time)

########################################################

##########
## MAIN ##
##########
@click.command()
@click.option('--tmin', 'T_min', default=1)
@click.option('--tmax', 'T_max', default=200)
@click.option('-t', '--timehorizon', 'T_user', default=None)
@click.option('--gap', 'sol_gap', default=None)
@click.option('--seq', 'sequential', is_flag=True, default=False)
@click.option('--domain_name', 'domain_name', default=None)
@click.option('--i_instance', 'i_instance', default=None)
@click.option('--domain_filename', 'domain_filename', default=None)
@click.option('--problem_filename', 'problem_filename', default=None)
def mainCLI(T_min, T_max, T_user, sol_gap, sequential, domain_name, i_instance, domain_filename, problem_filename):
    main(T_min, T_max, T_user, sol_gap, sequential, domain_name, i_instance, domain_filename, problem_filename)
def main(T_min, T_max, T_user, sol_gap, sequential, domain_name, i_instance, domain_filename, problem_filename):
    t_start = time.time()

    if domain_name==None and i_instance==None and \
    domain_filename==None and problem_filename==None:
        print('ERROR: no problem given.\nSpecify either (domain_name, i_instance) or (domain_filename, problem_filename).')
        return -1


    if domain_name!=None and i_instance!=None:
        domain_filename, problem_filename = get_problem_filenames(domain_name, i_instance)
    
    problem_name, up_problem, data_extracted = load_pddl(domain_filename, problem_filename)
    milp_data_problem = MILP_data_extracted(data_extracted)
    
    if T_user!=None:
        T_min = T_max = int(T_user)
    
    solved = False
    T = T_min
    while not solved and T<=T_max:
        boxprint(f"Solving with T={T}")
        
        m = build_model_piacentini2018_state_change_numeric(milp_data_problem, T, sequential)

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
            
    plan = extract_solution(domain_filename, problem_filename, m, T)

    from MILP.convert_pddl import g_loading_problem_time

    # show times
    boxprint(f'\
Loading problem: {g_loading_problem_time:.2f}s\n\
Building model: {g_building_model_time:.2f}s\n\
Solving instance: {g_solving_time:.2f}s\n\
Total time: {g_total_solving_time:.2f}s\
')
    

    plan_length = 0
    plan_str = []
    for t in plan:
        plan_length += len(plan[t])
        plan_str.append(f'{t}: ' + ', '.join(plan[t]))
    plan_str = ' | '.join(plan_str)

    return plan_str, plan_length, (g_loading_problem_time, g_building_model_time, g_solving_time, g_total_solving_time)

if __name__=='__main__':
    mainCLI()