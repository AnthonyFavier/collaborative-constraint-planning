
# PDSIM_INSTANCE_PATH = "/home/afavier/pdsim/PDSim/Assets/Scenes/Blocks/Data/PdSimInstance.asset"
# PDSIM_INSTANCE_PATH = "/home/afavier/pdsim/zenotravel_pdsim/Assets/Scenes/simplified zenotravel/Data/PdSimInstance.asset"
# PDSIM_INSTANCE_PATH = "/home/afavier/pdsim/zenotravel_pdsim/Assets/Scenes/ZenoTravel12/Data/PdSimInstance.asset"
# PDSIM_INSTANCE_PATH = "/home/afavier/pdsim/zenotravel_pdsim/Assets/Scenes/Zeno13/Data/PdSimInstance.asset"
# PDSIM_INSTANCE_PATH = "/home/afavier/my_pdsim/PDSim/Assets/Scenes/Zeno13/Data/PdSimInstance.asset"
# PDSIM_INSTANCE_PATH = '/home/afavier/pdsim/zenotravel_pdsim/Assets/Scenes/Zeno13/Data/PdSimInstance.asset'
# PDSIM_INSTANCE_PATH = '/home/afavier/pdsim/zenotravel_pdsim/Assets/Scenes/ZenoR/Data/PdSimInstance.asset'
PDSIM_INSTANCE_PATH = '/home/nicole/research/PDSim_Scenes_zenotravel/Assets/Scenes/ZenoR/Data/PdSimInstance.asset'
# PDSIM_INSTANCE_PATH = "/home/afavier/my_pdsim/PDSim/Assets/Scenes/Rover3/Data/PdSimInstance.asset"

from defs import *


def createActionStr(name, *parameters):
    
    paramstr = ""
    for p in parameters:
        paramstr += f"    - {p}\n"
    paramstr = paramstr[:-1]
    
    action_str = f"""  - id:
    name: {name.lower()}
    parameters:
""" + paramstr.lower() + """
    startTime: -1
    endTime: -1
"""
    
    return action_str 

def convertPlanIntoActionTuples(plan):
    
    actions = []
    
    plan = plan.split('\n')
    
    for l in plan:
        if ''.join(l.split())=='':
            continue
        l = l[l.find("(")+1 : l.find(")") ]
        l = ' '.join(l.split('_'))
        l = l.split(' ')
        name = l[0]
        params = l[1:]
        
        actions.append( (name, *params) )
    
    
    return actions

def main(plan):
    # Takes as input directly a list of actions, without any additional text
    
    try:
        with open(PDSIM_INSTANCE_PATH, 'r') as f:
            pdFileStr = f.read()
    except Exception as e:
        mprint("WARNING: Can't open PDSim file to update simulation plan, check log. [Skipped]")
        mprint('-> ' + str(e), logonly=True)
        return None
        
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