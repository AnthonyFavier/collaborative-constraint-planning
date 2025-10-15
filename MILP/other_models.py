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