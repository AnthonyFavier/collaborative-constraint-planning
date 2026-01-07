#######################
#### LOAD API KEYS ####
#######################

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

#######################

import click
import faulthandler

from collab_planning import *

#########################################################################################################

@click.command(help=f"{PROBLEMS.get_known_problems()}")
@click.argument('problem_name', default='zenoreal') # zeno13_n, zeno5, rover8_n, rover8_n_t, rover10_n_t, zenoreal
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

    constraint_planning.init(problem_name, planning_mode, timeout)
    # CAI.load_constraints('validated.json')

    agentic.init()

    app = GUI.App()
    
    constraint_planning.showSettings()
    
    app.mainloop()
if __name__ == '__main__':
    main()
