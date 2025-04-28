import unified_planning
from unified_planning.shortcuts import *
from unified_planning.io import PDDLReader, PDDLWriter

reader = PDDLReader()
problem = reader.parse_problem("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl", "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile12.pddl")

from unified_planning.engines.results import *
from unified_planning.plans import *

board = problem.action("board")
flyslow = problem.action("flyslow")
flyfast = problem.action("flyfast")
debark = problem.action("debark")
refuel = problem.action("refuel")

plane = {}
person = {}
city = {}

for i in range(20):
    try:
        plane[i] = problem.object(f'plane{i}')
    except: pass
    try:
        person[i] = problem.object(f'person{i}')
    except: pass
    try:
        city[i] = problem.object(f'city{i}')
    except: pass

plan = SequentialPlan([
ActionInstance(board, (person[8], plane[3], city[5])),
ActionInstance(refuel, (plane[2])),
ActionInstance(board, (person[7], plane[3], city[5])),
ActionInstance(board, (person[6], plane[1], city[2])),
ActionInstance(refuel, (plane[1])),
ActionInstance(refuel, (plane[3])),
ActionInstance(flyfast, (plane[2], city[3], city[3])),
ActionInstance(flyslow, (plane[3], city[5], city[0])),
ActionInstance(flyslow, (plane[3], city[0], city[4])),
ActionInstance(debark, (person[6], plane[1], city[2])),
ActionInstance(flyslow, (plane[1], city[2], city[2])),
ActionInstance(debark, (person[8], plane[3], city[4])),
ActionInstance(board, (person[1], plane[3], city[4])),
ActionInstance(board, (person[2], plane[3], city[4])),
ActionInstance(refuel, (plane[3])),
ActionInstance(flyslow, (plane[3], city[4], city[1])),
ActionInstance(board, (person[5], plane[3], city[1])),
ActionInstance(debark, (person[2], plane[3], city[1])),
ActionInstance(flyslow, (plane[3], city[1], city[4])),
ActionInstance(refuel, (plane[3])),
ActionInstance(debark, (person[5], plane[3], city[4])),
ActionInstance(flyslow, (plane[3], city[4], city[2])),
ActionInstance(board, (person[6], plane[3], city[2])),
ActionInstance(debark, (person[1], plane[3], city[2])),
ActionInstance(flyslow, (plane[3], city[2], city[0])),
ActionInstance(board, (person[3], plane[3], city[0])),
ActionInstance(flyslow, (plane[3], city[0], city[3])),
ActionInstance(refuel, (plane[3])),
ActionInstance(debark, (person[7], plane[3], city[3])),
ActionInstance(flyslow, (plane[3], city[3], city[1])),
ActionInstance(debark, (person[3], plane[3], city[1])),
ActionInstance(debark, (person[6], plane[3], city[1])),
])

with PlanValidator(name="aries-val") as validator:
    result = validator.validate(problem, plan)
    print(result)

fuel = FluentExp(problem.fluent("total-fuel-used"))
with SequentialSimulator(problem) as simulator:
    state = simulator.get_initial_state()
    print(f"Initial fuel = {state.get_value(fuel)}")
    for ai in plan.actions:
        state = simulator.apply(state, ai)
        print(f"Applied action: {ai}. ", end="")
        print(f"Total fuel: {state.get_value(fuel)}")
    if simulator.is_goal(state):
        print("Goal reached!")