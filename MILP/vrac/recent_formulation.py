import mip


##################
## PROBLEM INFO ##
##################

Vp = [
    "located_person1_city2",
    "in_person1_plane1",
    "located_person1_city1",
    "located_plane1_city1",
    "located_plane1_city2",
]

I = [
    "located_person1_city1",
    "located_plane1_city1",
]

Gp = [
	"located_person1_city2"
]

actions = []
pre_p = {}
del_p = {}
add_p = {}

# A1-BOARD_PERSON1_PLANE1_CITY1
actions.append("board_person1_plane1_city1")
pre_p["board_person1_plane1_city1"] = {
      "located_person1_city1",
      "located_plane1_city1",
    }
del_p["board_person1_plane1_city1"] = {"located_person1_city1"}
add_p["board_person1_plane1_city1"] = {"in_person1_plane1"}

# A2-FLYSLOW_PLANE1_CITY1_CITY2
actions.append("flyslow_plane1_city1_city2")
pre_p["flyslow_plane1_city1_city2"] = {"located_plane1_city1"}
del_p["flyslow_plane1_city1_city2"] = {"located_plane1_city1"}
add_p["flyslow_plane1_city1_city2"] = {"located_plane1_city2"}

# A3-DEBARK_PERSON1_PLANE1_CITY1
actions.append("debark_person1_plane1_city1")
pre_p["debark_person1_plane1_city1"] = {
    "in_person1_plane1",
    "located_plane1_city1",
    }
del_p["debark_person1_plane1_city1"] = {"in_person1_plane1"}
add_p["debark_person1_plane1_city1"] = {"located_person1_city1"}

# # DEBARK_PERSON1_PLANE1_CITY2
# actions.append("debark_person1_plane1_city2")
# pre_p["debark_person1_plane1_city2"] = {
#     "in_person1_plane1",
#     "located_plane1_city2"
#     }
# del_p["debark_person1_plane1_city2"] = {"in_person1_plane1"}
# add_p["debark_person1_plane1_city2"] = {"located_person1_city2"}

# # FLYSLOW_PLANE1_CITY2_CITY1
# actions.append("flyslow_plane1_city2_city1")
# pre_p["flyslow_plane1_city2_city1"] = {"located_plane1_city2"}
# del_p["flyslow_plane1_city2_city1"] = {"located_plane1_city2"}
# add_p["flyslow_plane1_city2_city1"] = {"located_plane1_city1"}

# # BOARD_PERSON1_PLANE1_CITY2
# actions.append("board_person1_plane1_city2")
# pre_p["board_person1_plane1_city2"] = {
#     "located_person1_city2",
#     "located_plane1_city2"
#     }
# del_p["board_person1_plane1_city2"] = {"located_person1_city2"}
# add_p["board_person1_plane1_city2"] = {"in_person1_plane1"}

def generatePND(actions, Vp):
    pnd = {}
    for p in Vp:
        pnd[p] = []
        for a in actions:
            if p in pre_p[a] and p not in del_p[a]:
                pnd[p].append(a)
    return pnd
                
def generateANP(actions, Vp):
    anp = {}
    for p in Vp:
        anp[p] = []
        for a in actions:
            if p not in pre_p[a] and p in add_p[a]:
                anp[p].append(a)
    return anp
                
def generatePD(actions, Vp):
    pd = {}
    for p in Vp:
        pd[p] = []
        for a in actions:
            if p in pre_p[a] and p in del_p[a] and p not in add_p[a]:
                pd[p].append(a)
    return pd

pnd = generatePND(actions, Vp) # require and don't delete p
anp = generateANP(actions, Vp) # add and don't require p
pd = generatePD(actions, Vp) # require and delete p

def old_pnd_anp_pd():
    pnd = {}
    pnd["located_plane1_city1"] = [
        "board_person1_plane1_city1",
        "debark_person1_plane1_city1",
    ]
    pnd["located_plane1_city2"] = [
        "board_person1_plane1_city2",
        "debark_person1_plane1_city2",
    ]
    pnd["located_person1_city1"] = []
    pnd["located_person1_city2"] = []
    pnd["in_person1_plane1"] = []

    anp = {}
    anp["located_plane1_city1"] = [
        "flyslow_plane1_city2_city1",
    ]
    anp["located_plane1_city2"] = [
        "flyslow_plane1_city1_city2",
    ]
    anp["located_person1_city1"] = [
        "debark_person1_plane1_city1",
    ]
    anp["located_person1_city2"] = [
        "debark_person1_plane1_city2",
    ]
    anp["in_person1_plane1"] = [
        "board_person1_plane1_city1",
        "board_person1_plane1_city2",
    ]
    
    pd = {}
    pd["located_plane1_city1"] = [
        "flyslow_plane1_city1_city2",
    ]
    pd["located_plane1_city2"] = [
        "flyslow_plane1_city2_city1",
    ]
    pd["located_person1_city1"] = [
        "board_person1_plane1_city1",
    ]
    pd["located_person1_city2"] = [
        "board_person1_plane1_city2",
    ]
    pd["in_person1_plane1"] = [
        "debark_person1_plane1_city1",
        "debark_person1_plane1_city2",
    ]


#################
## BUILD MODEL ##
#################
def build_model(solver_name, T):
    global u
    
    Tau = range(0, T)
    TauT = range(0, T+1)

    ###########
    ## MODEL ##
    ###########
    m = mip.Model(solver_name=solver_name)


    ###############
    ## VARIABLES ##
    ###############
    u = {}
    for a in actions:
        u[a] = {}
        for t in Tau:
            u[a][t] = m.add_var(var_type=mip.BINARY)
        
    u_a = {}
    u_pa = {}
    u_pd = {}
    u_m = {}
    for p in Vp:
        u_a[p] = {}
        u_pa[p] = {}
        u_pd[p] = {}
        u_m[p] = {}
        for t in TauT:
            u_a[p][t] = m.add_var(var_type=mip.BINARY)
            u_pa[p][t] = m.add_var(var_type=mip.BINARY)
            u_pd[p][t] = m.add_var(var_type=mip.BINARY)
            u_m[p][t] = m.add_var(var_type=mip.BINARY)


    #################
    ## CONSTRAINTS ##
    #################
    
    # (1)
    for p in Vp:
        if p in I:
            m += u_a[p][0] == 1
        else:
            m += u_a[p][0] == 0

    # (2)
    for p in Gp:
        m += u_a[p][T] + u_pa[p][T] + u_m[p][T] >= 1
        
    # (3)
    for p in Vp:
        for t in Tau:
            m += mip.xsum(u[a][t] for a in pnd[p]) >= u_pa[p][t+1]
            
    # (4)
    for p in Vp:
        for t in Tau:
            m += mip.xsum(u[a][t] for a in anp[p]) >= u_a[p][t+1]
    # (5)
    for p in Vp:
        for t in Tau:
            m += mip.xsum(u[a][t] for a in pd[p]) == u_pd[p][t+1]

    # (6)
    for p in Vp:
        for a in pnd[p]:
            for t in Tau:
                m += u[a][t] <= u_pa[p][t+1]

    # (7)
    for p in Vp:
        for a in anp[p]:
            for t in Tau:
                m += u[a][t] <= u_a[p][t+1]
                
    # (8)
    for p in Vp:
        for t in TauT:
            m += u_a[p][t] + u_m[p][t] + u_pd[p][t] <= 1
            
    # (9)
    for p in Vp:
        for t in TauT:
            m += u_pa[p][t] + u_m[p][t] + u_pd[p][t] <= 1

    # (10)
    # import itertools
    # for a1, a2 in itertools.combinations(actions, 2):
    #     if (del_p[a1] & ( add_p[a2] | pre_p[a2] )) != set():
    #         print(a1 + " - " + a2)
    #         for t in TauT:
    #             m += u[a1][t] + u[a2][t] <= 1
                
    # (10 bis)
    for a1 in actions:
        for a2 in actions:
            if a1 != a2:
                if (del_p[a1] & ( add_p[a2] | pre_p[a2] )) != set():
                    print(a1 + " - " + a2)
                    for t in Tau:
                        m += u[a1][t] + u[a2][t] <= 1

    # (11)
    for p in Vp:
        for t in Tau:
            m += u_pa[p][t+1] + u_m[p][t+1] + u_pd[p][t+1] <= u_a[p][t] + u_pa[p][t] + u_m[p][t]

    # # (23)
    # for t in range(1, T+1):
    #     m += mip.xsum(u[a][t] for a in actions) <= 1
        
    # # (24)
    # for a in actions:
    #     for t in range(1, T+1):
    #         m += mip.xsum(u[a][t+1] for a in actions) <= mip.xsum(u[a][t] for a in actions)


    ###############
    ## OBJECTIVE ##
    ###############
    L = []
    for a in actions:
        for t in Tau:
            L.append(u[a][t])
    # m.objective = mip.minimize(mip.xsum(L))
    
    return m
time_horizon = 3
m = build_model("cbc", time_horizon)

###########
## SOLVE ##
###########
solver_status = m.optimize()


######################
## EXTRACT SOLUTION ##
######################
plan = []
for t in range(0, time_horizon):
    print(f"## t={t} ##")
    for a in actions:
        if round(u[a][t].x)==1:
            print(a)
            plan.append(a)
            
# Print the solution.
print("MILP solution")
print(f"Solver status: {solver_status}")
