from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.shortcuts import *
from unified_planning.plans import ActionInstance, SequentialPlan
    
def simulatePlan(domain_path, problem_path, txt_plan, metric_name):
    txt = ''
    reader = PDDLReader()
    problem = reader.parse_problem(domain_path, problem_path)
    
    # convert plan
    txt_plan = txt_plan.split('\n')
    actions = []
    for l in txt_plan:
        if ''.join(l.split())=='':
            continue
        l = l[l.find("(")+1 : l.find(")") ]
        l = ' '.join(l.split('_'))
        l = l.split(' ')
        name = l[0]
        params = l[1:]
        actions.append( (name, *params) )
    up_plan = []
    for a in actions:
        name, *params = a
        up_action = problem.action(name)
        up_params = [problem.object(p.lower()) for p in params]
        up_plan.append(ActionInstance(up_action, up_params))
    up_plan = SequentialPlan(up_plan)
    
    # Simulate
    with SequentialSimulator(problem) as simulator:
        metric = FluentExp(problem.fluent(metric_name))
        state = simulator.get_initial_state()
        for ai in up_plan.actions:
            new_state = simulator.apply(state, ai)
            if new_state==None:
                break
            state = new_state
            
        if new_state==None:
            txt += 'Plan is invalid.\n'
            txt += f"Action {ai} isn't applicable.\n"
        elif not simulator.is_goal(state):
            txt += 'Plan is invalid.\n'
            txt += "The final state doesn't satisfy the goal.\n"
        else:
            txt += 'Plan is valid.\n'
        txt += f"Initial value {metric_name} = {simulator.get_initial_state().get_value(metric)}\n"
        txt += f"Final value {metric_name} = {state.get_value(metric)}\n"
        
    return txt
        
        
if __name__=='__main__':
    
    reader = PDDLReader()
    problem = reader.parse_problem("NumericTCORE/benchmark/Rover-Numeric/domain_n_t.pddl", "NumericTCORE/benchmark/Rover-Numeric/pfile10_t.pddl")

    lines = """
.0: (samplerock_rover0_rover0store_waypoint4)
.0: (drop_rover0_rover0store)
.0: (communicaterockdata_rover0_general_waypoint4_waypoint4_waypoint1)
.0: (samplesoil_rover0_rover0store_waypoint4)
.0: (drop_rover0_rover0store)
.0: (communicatesoildata_rover0_general_waypoint4_waypoint4_waypoint1)

.0: (navigate_rover0_waypoint4_waypoint3)
.0: (samplerock_rover0_rover0store_waypoint3)
.0: (drop_rover0_rover0store)
.0: (samplesoil_rover0_rover0store_waypoint3)
.0: (drop_rover0_rover0store)
.0: (navigate_rover0_waypoint3_waypoint4)
.0: (communicaterockdata_rover0_general_waypoint3_waypoint4_waypoint1)
.0: (recharge_rover0_waypoint4)
.0: (communicatesoildata_rover0_general_waypoint3_waypoint4_waypoint1)

.0: (samplerock_rover3_rover3store_waypoint1)
.0: (drop_rover3_rover3store)
.0: (navigate_rover3_waypoint1_waypoint0))
.0: (communicaterockdata_rover3_general_waypoint1_waypoint0_waypoint1)

.0: (samplerock_rover3_rover3store_waypoint0)
.0: (drop_rover3_rover3store)
.0: (communicaterockdata_rover3_general_waypoint0_waypoint0_waypoint1)

.0: (samplesoil_rover3_rover3store_waypoint0)
.0: (drop_rover3_rover3store)
.0: (communicatesoildata_rover3_general_waypoint0_waypoint0_waypoint1)

.0: (navigate_rover3_waypoint0_waypoint6)
.0: (samplesoil_rover3_rover3store_waypoint6)
.0: (drop_rover3_rover3store)
.0: (recharge_rover3_waypoint6)
.0: (navigate_rover3_waypoint6_waypoint0)
.0: (communicatesoildata_rover3_general_waypoint6_waypoint0_waypoint1)


.0: (calibrate_rover1_camera0_objective2_waypoint0)
.0: (calibrate_rover1_camera1_objective3_waypoint0)
.0: (takeimage_rover1_waypoint0_objective3_camera0_lowres)
.0: (communicateimagedata_rover1_general_objective3_lowres_waypoint0_waypoint1)
.0: (takeimage_rover1_waypoint0_objective3_camera1_colour)
.0: (communicateimagedata_rover1_general_objective3_colour_waypoint0_waypoint1)
.0: (calibrate_rover1_camera1_objective3_waypoint0)
.0: (takeimage_rover1_waypoint0_objective2_camera1_colour)
.0: (communicateimagedata_rover1_general_objective2_colour_waypoint0_waypoint1)
"""[1:-1]
    # total energy 139

    # Constraints:
    #   - ROVER0 SHOULD HANDLE SOIL AND ROCK DATA FROM WAYPOINT4
    #   - ROVER2 SHOULD NEVER BE USED
    #   - NO ROVER SHOULD EVER BE IN WAYPOINT2 OR WAYPOINT5
    #   - ROVER1 SHOULD TAKE ALL IMAGE
    #   - WAYPOINT6 SHOULD ALWAYS HAVE SAME ROCK SAMPLE

    plan = []
    for line in lines.splitlines():
        if line.strip()=='':
            continue
        _, action_str = line.split(": ")
        name, *params = action_str.strip("()").split('_')
        action = problem.action(name)
        up_objects = [problem.object(p) for p in params]
        plan.append(ActionInstance(action, up_objects))
    plan = SequentialPlan(plan)

    print(plan)

    # with PlanValidator(name="tamer") as validator:
    #     result = validator.validate(problem, plan)
    #     print(result)
            
    with SequentialSimulator(problem) as simulator:
        fluent = FluentExp(problem.fluent("total-energy-used"))
        r0e = FluentExp(problem.fluent('energy'), problem.object('rover0'))
        r1e = FluentExp(problem.fluent('energy'), problem.object('rover1'))
        r2e = FluentExp(problem.fluent('energy'), problem.object('rover2'))
        r3e = FluentExp(problem.fluent('energy'), problem.object('rover3'))
        state = simulator.get_initial_state()
        print(f"Initial fluent value = {state.get_value(fluent)}")
        print(f"Initial r0e = {state.get_value(r0e)}")
        print(f"Initial r1e = {state.get_value(r1e)}")
        print(f"Initial r2e = {state.get_value(r2e)}")
        print(f"Initial r3e = {state.get_value(r3e)}")
        for ai in plan.actions:
            state = simulator.apply(state, ai)
            print(f"Applied action: {ai}. ", end="")
            print(f"Fluent value: {state.get_value(fluent)} r0e: {state.get_value(r0e)} r1e: {state.get_value(r1e)} r2e: {state.get_value(r2e)} r3e: {state.get_value(r3e)}")
        if simulator.is_goal(state):
            print("Goal reached!")