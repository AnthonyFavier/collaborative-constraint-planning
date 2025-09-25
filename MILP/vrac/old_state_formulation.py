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

def generatePreF(actions, Vp):
    pref = {}
    for f in Vp:
        pref[f] = []
        for a in actions:
            if f in pre_p[a]:
                pref[f].append(a)
    return pref
def generateAddF(actions, Vp):
    addf = {}
    for f in Vp:
        addf[f] = []
        for a in actions:
            if f in add_p[a]:
                addf[f].append(a)
    return addf
def generateDelF(actions, Vp):
    delf = {}
    for f in Vp:
        delf[f] = []
        for a in actions:
            if f in del_p[a]:
                delf[f].append(a)
    return delf
pref = generatePreF(actions, Vp)
addf = generateAddF(actions, Vp)
delf = generateDelF(actions, Vp)

#################
## BUILD MODEL ##
#################
def build_model(solver_name, T):
    global y
    

    ###########
    ## MODEL ##
    ###########
    m = mip.Model(solver_name=solver_name)


    ###############
    ## VARIABLES ##
    ###############
    x = {}
    for f in Vp:
        x[f] = {}
        for i in range(1, T+2):
            x[f][i] = m.add_var(var_type=mip.BINARY)
    
    y = {}
    for a in actions:
        y[a] = {}
        for i in range(1, T+1):
            y[a][i] = m.add_var(var_type=mip.BINARY)
        
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
            m += x[f][i+1] <= sum(y[a][i] for a in addf[f])
            
    # Conflict Exclusion Constraints
    for a1 in actions:
        for a2 in actions:
            for f in Vp:
                if a1 != a2 and a1 in delf[f] and a2 in pref[f]+addf[f]:
                    for i in range(1, T+1):
                        m += y[a1][i] + y[a2][i] <= 1
    
    ###############
    ## OBJECTIVE ##
    ###############
    L = []
    for a in actions:
        for i in range(1, T+1):
            L.append(y[a][i])
    m.objective = mip.minimize(mip.xsum(L))
    
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
for i in range(1, time_horizon+1):
    print(f"## t={i} ##")
    for a in actions:
        if round(y[a][i].x)==1:
            print(a)
            plan.append(a)
            
# Print the solution.
print("MILP solution")
print(f"Solver status: {solver_status}")
