import CAI
import GUI_agentic
from defs import *
import click
import sys
import faulthandler
from ablation import AblationSetting

#########################################################################################################

@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name', default='zeno13_n') # zeno13_n, zeno5, rover8_n, rover8_n_t, rover10_n_t
@click.option('-a', '--anytime', 'planning_mode', flag_value=PlanMode.ANYTIME, default=True, help="Set the planning mode to 'Anytime' (default)")
@click.option('-aa', '--anytimeauto', 'planning_mode', flag_value=PlanMode.ANYTIMEAUTO, help="Set the planning mode to 'AnytimeAuto'")
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, help="Set the planning mode to 'Optimal'")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('-t', '--timeout', 'timeout', default=15.0, help="Timeout for planning")
def main(problem_name, planning_mode, timeout):
    faulthandler.enable()
        
    # FOR ABLATION 
    # AblationSetting.apply(AblationSetting.DIRECT)
    
    # Logging
    setupLogger()
    
    # Init CAI 
    CAI.init(problem_name, planning_mode, timeout)
    # CAI.CM.load('validated.json)
    
    # Create main GUI app
    app = GUI_agentic.App()
    
    # Show settings
    CAI.showSettings()
    
    app.mainloop()
if __name__ == '__main__':
    main()
