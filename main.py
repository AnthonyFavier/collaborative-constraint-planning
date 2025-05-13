import CAI
import GUI
from defs import *
import click
import sys
def Zeno13A(decomp=CAI.WITH_DECOMP):
    print("Zeno13A")
    constraints = [
        "Person7, plane2 and plane3 should be ignored.",
        "Also, planes should only fly slowly to save fuel.",
    ]
    
    if decomp:
        CAI.addConstraints(constraints)
    else:
        txt = " ".join(constraints)
        CAI.addConstraints([txt])
        
def Zeno13B(decomp=CAI.WITH_DECOMP):
    print("Zeno13B")
    constraints = [
        "Person7 should not move.","Plane2 and plane3 should never be used.",
        "No plane should ever use flyfast.",
    ]
    
    if decomp:
        CAI.addConstraints(constraints)
    else:
        txt = " ".join(constraints)
        CAI.addConstraints([txt])
        
def Zeno13C(decomp=CAI.WITH_DECOMP):
    print("Zeno13C")
    constraints = [
        "Person7 should always be located in city0.", 
        "Plane2 should always be located in city2.", 
        "Plane2 should always have no person onboard.", 
        "Plane2 fuel level should always be 1469.",
        "Plane3 should always be located in city3.", 
        "Plane3 should always have no person onboard.", 
        "Plane3 fuel level should always be 1532.",
        "For all planes and cities, there should always be no flyfast.",
    ]
    
    if decomp:
        CAI.addConstraints(constraints)
    else:
        txt = " ".join(constraints)
        CAI.addConstraints([txt])
        
#########################################################################################################

@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name')
@click.option('-a', '--anytime', 'planning_mode', flag_value=PlanMode.ANYTIME, default=True, help="Set the planning mode to 'Anytime' (default)")
@click.option('-aa', '--anytimeauto', 'planning_mode', flag_value=PlanMode.ANYTIMEAUTO, help="Set the planning mode to 'AnytimeAuto'")
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, help="Set the planning mode to 'Optimal'")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('-t', '--timeout', 'timeout', default=15.0, help="Timeout for planning")
@click.option('--e2nl', 'e2nl', is_flag=True, default=False, help="Activates the translation of encodings back to NL")
def main(problem_name, planning_mode, timeout, e2nl):
    CAI.g_with_e2nl = e2nl
    
    app = GUI.App()
    setPromptFunction(app.display_frame.prompt)
    setInputFunction(app.display_frame.getFromEntry)
    
    CAI.init(problem_name, planning_mode, timeout)
    
    # FOR ABLATION #
    # Zeno13A()
    # Zeno13B()
    # Zeno13C()
    # CAI.CM.show()
    # app.constraints_frame.updateFrame()
    
    app.mainloop()
if __name__ == '__main__':
    # sys.argv.append('zeno5_n')
    # sys.argv.append('zeno5_bis')
    main()