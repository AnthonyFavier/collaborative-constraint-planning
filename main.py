import CAI
import GUI
from defs import *
import click
import sys

@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name')
@click.option('-a', '--anytime', 'planning_mode', flag_value=PlanMode.ANYTIME, default=True, help="Set the planning mode to 'Anytime' (default)")
@click.option('-aa', '--anytimeauto', 'planning_mode', flag_value=PlanMode.ANYTIMEAUTO, help="Set the planning mode to 'AnytimeAuto'")
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, help="Set the planning mode to 'Optimal'")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('-t', '--timeout', 'timeout', default=10.0, help="Timeout for planning")
def main(problem_name, planning_mode, timeout):
    
    # r = CAI.CM.createRaw("never use plane1")
    # d = CAI.CM.createDecomposed(r, "Person1, person2, person3, and person4 should never be in plane1.")
    # d.encoding = "(always (and (not (in person1 plane1)) (not (in person2 plane1)) (not (in person3 plane1)) (not (in person4 plane1))))"
    # d = CAI.CM.createDecomposed(r, "Plane1 should remain at its initial location (city1) throughout the plan.")
    # d.encoding = "(always (located plane1 city1))"
    # d = CAI.CM.createDecomposed(r, "The number of people onboard plane1 should always be zero.")
    # d.encoding = "(always (= (onboard plane1) 0))"
    # d = CAI.CM.createDecomposed(r, "The fuel level of plane1 should remain unchanged from its initial value.")
    # d.encoding = "(always (= (fuel plane1) 174))"
    # r = CAI.CM.createRaw("plane2 should be in city2 at the end")
    # d = CAI.CM.createDecomposed(r, "plane2 must be located in city2 in the final state")
    # d.encoding = "(at-end (located plane2 city2))"
    
    app = GUI.App()
    setPromptFunction(app.display_frame.prompt)
    CAI.init(problem_name, planning_mode, timeout)
    app.mainloop()
if __name__ == '__main__':
    # sys.argv.append('zeno5_n')
    # sys.argv.append('zeno5_bis')
    main()