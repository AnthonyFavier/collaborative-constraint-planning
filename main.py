import CAI
import GUI
from defs import *
import click
import sys
import faulthandler

def initZeno13():
    # ZENO 13 #
    r = CAI.CM.createRaw("Person7 should not move.")
    d = CAI.CM.createDecomposed(r, "Person7 should always be located in city0.")
    d.encoding = "(always (located person7 city0))"
    
    r = CAI.CM.createRaw("Plane2 should never be used.")
    d = CAI.CM.createDecomposed(r, "Plane2 should remain at its initial location (city2) throughout the plan.")
    d.encoding = "(always (located plane2 city2))"
    d = CAI.CM.createDecomposed(r, "The number of people onboard plane2 should always be zero.")
    d.encoding = "(always (= (onboard plane2) 0))"
    d = CAI.CM.createDecomposed(r, "The fuel level of plane2 should remain unchanged from its initial value.")
    d.encoding = "(always (= (fuel plane2) 1469))"
    
    r = CAI.CM.createRaw("Plane3 should never be used.")
    d = CAI.CM.createDecomposed(r, "Plane3 should remain at its initial location (city3) throughout the plan.")
    d.encoding = "(always (located plane3 city3))"
    d = CAI.CM.createDecomposed(r, "The number of people onboard plane3 should always be zero.")
    d.encoding = "(always (= (onboard plane3) 0))"
    d = CAI.CM.createDecomposed(r, "The fuel level of plane3 should remain unchanged from its initial value.")
    d.encoding = "(always (= (fuel plane3) 1532))"
    
    r = CAI.CM.createRaw("No plane should even use flyfast.")
    d = CAI.CM.createDecomposed(r, "No plane should never execute flyfast.")
    d.encoding = "(always (forall (?p - aircraft ?c1 ?c2 - city) (= (n_flyfast ?p ?c1 ?c2) 0)))"


def ablation(app, type):
    if type not in ['A', 'B', 'C']:
        raise Exception("Wrong ablation type")

    if 'A'==type:
        Zeno13A()
    elif 'B'==type:
        Zeno13B()
    elif 'C'==type:
        Zeno13C()
        
    CAI.CM.show()
    app.constraints_frame.updateFrame()
        
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
        

def initdemo():
    # ZENO 13 #
    r = CAI.CM.createRaw("Plane2 and plane3 should never be used")
    d = CAI.CM.createDecomposed(r, "Person1 through person10 should never be in plane2")
    d.encoding = "(always (forall (?p - person) (not (in ?p plane2))))"
    d = CAI.CM.createDecomposed(r, "Person1 through person10 should never be in plane3")
    d.encoding = "(always (forall (?p - person) (not (in ?p plane3))))"
    d = CAI.CM.createDecomposed(r, "Plane2 should remain located in city2 throughout the entire plan")
    d.encoding = "(always (located plane2 city2))"
    d = CAI.CM.createDecomposed(r, "Plane3 should remain located in city3 throughout the entire plan")
    d.encoding = "(always (located plane3 city3))"
    d = CAI.CM.createDecomposed(r, "The fuel level of plane2 should never exceed its initial value of 1469")
    d.encoding = "(always (= (fuel plane2) 1469))"
    d = CAI.CM.createDecomposed(r, "The fuel level of plane3 should never exceed its initial value of 1532")
    d.encoding = "(always (= (fuel plane3) 1532))"
    
    r = CAI.CM.createRaw("Person7 should never move and planes should never fly fast")
    d = CAI.CM.createDecomposed(r, "Person7 should always remain located in city0.")
    d.encoding = "(always (located person7 city0))"
    d = CAI.CM.createDecomposed(r, "No aircraft should ever use the flyfast mode of transportation.")
    d.encoding = "(always (forall (?p - aircraft ?c1 ?c2 - city) (= (n_flyfast ?p ?c1 ?c2) 0)))"
    
    r = CAI.CM.createRaw("Plane1 should never fly to a same city more than 3 times")
    d = CAI.CM.createDecomposed(r, "ss")
    d.encoding = "(always (forall (?d - city) (<= (+  (n_flyslow plane1 city0 ?d) (n_flyfast plane1 city0 ?d) (n_flyslow plane1 city1 ?d) (n_flyfast plane1 city1 ?d) (n_flyslow plane1 city2 ?d) (n_flyfast plane1 city2 ?d) (n_flyslow plane1 city3 ?d) (n_flyfast plane1 city3 ?d) (n_flyslow plane1 city4 ?d) (n_flyfast plane1 city4 ?d) (n_flyslow plane1 city5 ?d) (n_flyfast plane1 city5 ?d) ) 2)))"
    
def loadDump():
    # put dump code
    pass



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
    faulthandler.enable()
    
    CAI.g_with_e2nl = e2nl
    
    app = GUI.App()
    setPrintFunction(app.display_frame.prompt)
    setInputFunction(app.display_frame.getFromEntry)
    
    CAI.init(problem_name, planning_mode, timeout)
    
    # Ask for initial suggestions
    # app.suggestions()
    
    # FOR ABLATION # A, B, or C
    # ablation(app, 'A') 
    
    app.mainloop()
if __name__ == '__main__':
    # sys.argv += ['zeno13_n']
    
    # loadDump()
    main()