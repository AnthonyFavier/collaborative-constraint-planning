#######################
#### LOAD API KEYS ####
#######################

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

#######################

import click
import faulthandler

from CAI_pkg.Globals import *
from CAI_pkg import GUI_agentic
from CAI_pkg.ConstraintPlanning import CAI
from CAI_pkg.Agentic_constraint import init_agentic
from CAI_pkg.Logger import init_logger

#########################################################################################################

@click.command(help=f"{PROBLEMS.get_known_problems()}")
@click.argument('problem_name', default='zeno13_n') # zeno13_n, zeno5, rover8_n, rover8_n_t, rover10_n_t
@click.option('-a', '--anytime', 'planning_mode', flag_value=PlanMode.ANYTIME, default=True, help="Set the planning mode to 'Anytime' (default)")
@click.option('-aa', '--anytimeauto', 'planning_mode', flag_value=PlanMode.ANYTIMEAUTO, help="Set the planning mode to 'AnytimeAuto'")
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, help="Set the planning mode to 'Optimal'")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('-t', '--timeout', 'timeout', default=15.0, help="Timeout for planning")
def main(problem_name, planning_mode, timeout):
    faulthandler.enable()

    init_logger()

    applyAblation(AblationSetting.REGULAR)

    CAI.init(problem_name, planning_mode, timeout)
    # CAI.load_constraints('validated.json')

    init_agentic()

    app = GUI_agentic.App()
    
    CAI.showSettings()
    
    app.mainloop()
if __name__ == '__main__':
    main()
