import CAI
import GUI_agentic
from defs import *
import click
import sys
import faulthandler
from enum import auto, Enum

#########################################################################################################

class AblationSetting(Enum):
    """
    [S1] Direct LLM translation                : WITH_E2NL=False,   WITH_VERIFIER=False,    WITH_DECOMP=False,    WITH_DECOMP_CONFIRM=False, 
    [S2]  + E2NL (human review + intervention) : WITH_E2NL=True,    WITH_VERIFIER=False,    WITH_DECOMP=False,    WITH_DECOMP_CONFIRM=False, 
    [S3] Verifier loops                        : WITH_E2NL=False,   WITH_VERIFIER=True,     WITH_DECOMP=False,    WITH_DECOMP_CONFIRM=False, 
    [S4]  + E2NL (human review + intervention) : WITH_E2NL=True,    WITH_VERIFIER=True,     WITH_DECOMP=False,    WITH_DECOMP_CONFIRM=False, 
    [S5] Decomposition (no human)              : WITH_E2NL=False,   WITH_VERIFIER=True,     WITH_DECOMP=True,     WITH_DECOMP_CONFIRM=False, 
    [S6]  + human review + intervention        : WITH_E2NL=False,   WITH_VERIFIER=True,     WITH_DECOMP=True,     WITH_DECOMP_CONFIRM=True, 
    [S7]  + E2NL (human review + intervention) : WITH_E2NL=True,    WITH_VERIFIER=True,     WITH_DECOMP=True,     WITH_DECOMP_CONFIRM=True, 
    """
    #                   WITH_E2NL,    WITH_VERIFIER,    WITH_DECOMP,    WITH_DECOMP_CONFIRM
    DIRECT =            (False,       False,            False,          False)
    DIRECT_E2NL =       (True,        False,            False,          False)
    VERIFIER =          (False,       True,             False,          False)
    VERIFIER_E2NL =     (True,        True,             False,          False)
    DECOMP =            (False,       True,             True,           False)
    DECOMP_CONFIRM =    (False,       True,             True,           True)
    DECOMP_E2NL =       (True,        True,             True,           True)
    
    def apply(setting):
        CAI.WITH_E2NL, CAI.WITH_VERIFIER, CAI.WITH_DECOMP, CAI.WITH_DECOMP_CONFIRM = setting.value
        CAI.SETTING_NAME = setting.name

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
