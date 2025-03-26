import CAI
import GUI
from defs import *
import click
import sys

@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name')
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, default=True, help="Set the planning mode to 'Default' (default)")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, help="Set the planning mode to 'Optimal'")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
def main(problem_name, planning_mode):
    
    # r = cai.CM.createRaw("never use plane1")
    # d = cai.CM.createDecomposed(r, "Person1, person2, person3, and person4 should never be in plane1.")
    # d.encoding = "(always (and (not (in person1 plane1)) (not (in person2 plane1)) (not (in person3 plane1)) (not (in person4 plane1))))"
    # d = cai.CM.createDecomposed(r, "Plane1 should remain at its initial location (city1) throughout the plan.")
    # d.encoding = "(always (located plane1 city1))"
    # d = cai.CM.createDecomposed(r, "The number of people onboard plane1 should always be zero.")
    # d.encoding = "(always (= (onboard plane1) 0))"
    # d = cai.CM.createDecomposed(r, "The fuel level of plane1 should remain unchanged from its initial value.")
    # d.encoding = "(always (= (fuel plane1) 174))"
    # r = cai.CM.createRaw("plane2 should be in city2 at the end")
    # d = cai.CM.createDecomposed(r, "plane2 must be located in city2 in the final state")
    # d.encoding = "(at-end (located plane2 city2))"
    
    app = GUI.App()
    setPromptFunction(app.display_frame.prompt)
    CAI.init(problem_name, planning_mode)
    app.mainloop()
if __name__ == '__main__':
    # sys.argv.append('zeno5_n')
    # sys.argv.append('zeno5_bis')
    main()