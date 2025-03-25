
# PDSIM_INSTANCE_PATH = "/home/afavier/pdsim/PDSim/Assets/Scenes/Blocks/Data/PdSimInstance.asset"
PDSIM_INSTANCE_PATH = "/home/afavier/pdsim/zenotravel_pdsim/Assets/Scenes/simplified zenotravel/Data/PdSimInstance.asset"

def createActionStr(name, *parameters):
    
    paramstr = ""
    for p in parameters:
        paramstr += f"    - {p}\n"
    paramstr = paramstr[:-1]
    
    action_str = f"""  - id:
    name: {name}
    parameters:
""" + paramstr + """
    startTime: -1
    endTime: -1
"""
    
    return action_str 

def convertPlanIntoActionTuples(plan):
    
    actions = []
    
    plan = plan.split('\n')
    
    for i in range(len(plan)):
        if plan[i].find("Found Plan:"):
            i_s = i+1
        if plan[i].find("Plan-Length:")
            i_e = i-1
            
    plan = plan[i_s:i_e]
    
    for l in plan:
        l = l[l.find("(")+1 : l.find(")") ]
        l = l.split('_')
        name = l[0]
        params = l[1:]
        
        actions.append( (name, *params) )
    
    
    return actions

def main(plan):
    
    with open(PDSIM_INSTANCE_PATH, 'r') as f:
        pdFileStr = f.read()
        
    w = "plan:\n"
    i_plan = pdFileStr.find(w) + len(w)
    
    # actions = [
    #     ('pick-up', 'b'),
    #     ('stack', 'b', 'a'),
    #     ('pick-up', 'c'),
    #     ('stack', 'c', 'b'),
    #     ('pick-up', 'd'),
    #     ('stack', 'd', 'c'),
    # ]
    
    # actions = [
    #     ('pick-up', 'b'),
    #     ('stack', 'b', 'a'),
    #     ('pick-up', 'c'),
    #     ('stack', 'c', 'b'),
    #     ('pick-up', 'd'),
    #     ('stack', 'd', 'c'),
    #     ('pick-up', 'a'),
    #     ('stack', 'a', 'd'),
    #     ('pick-up', 'b'),
    #     ('stack', 'b', 'a'),
    #     ('pick-up', 'c'),
    #     ('stack', 'c', 'b'),
    #     ('pick-up', 'd'),
    #     ('stack', 'd', 'c'),
    # ]
    
    actions = convertPlanIntoActionTuples(plan)
    
    new_plan = ""
    for a in actions:
        new_plan += createActionStr(*a)
    
    pdFileStr = pdFileStr[:i_plan] + new_plan
    
    with open(PDSIM_INSTANCE_PATH, 'w') as f:
        f.write(pdFileStr)

if __name__ == '__main__':
    pass

#     p = """Found Plan:
# 0.0: (board_person4_plane4_city1)
# 1.0: (flyslow_plane4_city1_city3)
# 2.0: (flyslow_plane3_city0_city1)
# 3.0: (flyslow_plane3_city1_city1)
# 4.0: (flyslow_plane2_city2_city3)
# 5.0: (board_person1_plane2_city3)
# 6.0: (refuel_plane2)
# 7.0: (flyslow_plane2_city3_city2)
# 8.0: (flyslow_plane1_city1_city1)
# 9.0: (debark_person1_plane2_city2)
# 10.0: (flyslow_plane2_city2_city0)
# 11.0: (board_person3_plane2_city0)
# 12.0: (flyslow_plane2_city0_city3)
# 13.0: (refuel_plane4)
# 14.0: (refuel_plane2)
# 15.0: (debark_person4_plane4_city3)
# 16.0: (flyslow_plane4_city3_city0)
# 17.0: (board_person4_plane2_city3)
# 18.0: (board_person2_plane4_city0)
# 19.0: (flyslow_plane4_city0_city3)
# 20.0: (debark_person2_plane4_city3)
# 21.0: (debark_person4_plane2_city3)
# 22.0: (debark_person3_plane2_city3)
# Plan-Length:23
# Metric (Search):10630.0
# Planning Time (msec): 220
# """

#     convertPlanIntoActionTuples(p)

#     main()