import CAI
import GUI
from defs import *
import click
import sys
import faulthandler

def initZeno5():
    # ZENO 5 #
    r = CAI.CM.createRaw("Plane1 should never be used.")
    d = CAI.CM.createDecomposed(r, "There must always be no person in plane1.")
    d.encoding = '''(always (forall (?p - person) (not (in ?p plane1))))'''
    d = CAI.CM.createDecomposed(r, "Plane1 should remain at its initial location (city1) throughout the plan.")
    d.encoding = "(always (located plane1 city1))"
    # d = CAI.CM.createDecomposed(r, "The number of people onboard plane1 should always be zero")
    # d.encoding = "(always (= (onboard plane1) 0))"
    d = CAI.CM.createDecomposed(r, "The fuel level of plane1 should remain unchanged from its initial value.")
    d.encoding = "(always (= (fuel plane1) 174))"
    
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
        

def initDemo():
    # ZENO 13 #
    r = CAI.CM.createRaw("Only use plane1.")
    d = CAI.CM.createDecomposed(r, "No person is ever inside plane2 throughout the entire plan execution")
    d.encoding = '''(always (forall (?p - person) (not (in ?p plane2))))'''
    d = CAI.CM.createDecomposed(r, "No person is ever inside plane3 throughout the entire plan execution")
    d.encoding = '''(always (forall (?p - person) (not (in ?p plane3))))'''
    d = CAI.CM.createDecomposed(r, "Plane2 always remains at city2 throughout the entire plan execution")
    d.encoding = '''(always (located plane2 city2))'''
    d = CAI.CM.createDecomposed(r, "Plane3 always remains at city3 throughout the entire plan execution")
    d.encoding = '''(always (located plane3 city3))'''

    r = CAI.CM.createRaw("Person7 should not move")
    d = CAI.CM.createDecomposed(r, "Person7 must remain at city0 throughout the entire plan execution")
    d.encoding = '''(always (located person7 city0))'''

    r = CAI.CM.createRaw("Planes should only fly slowly")
    d = CAI.CM.createDecomposed(r, "Throughout the entire plan execution, for every aircraft and every pair of cities, the number of fast flights performed by that aircraft between those cities must always remain zero.")
    d.encoding = '''(always (forall (?a - aircraft ?c1 - city ?c2 - city) 
        (= (n_flyfast ?a ?c1 ?c2) 0)))'''

    r = CAI.CM.createRaw("Plane1 should never fly to a same city more than 3 times")
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city0 (from any origin city, using either slow or fast flight) must never exceed 3")
    d.encoding = '''(always (<= 
        (+ (n_flyslow plane1 city0 city0) (n_flyslow plane1 city1 city0) (n_flyslow plane1 city2 city0) (n_flyslow plane1 city3 city0) (n_flyslow plane1 city4 city0) (n_flyslow plane1 city5 city0)
          (n_flyfast plane1 city0 city0) (n_flyfast plane1 city1 city0) (n_flyfast plane1 city2 city0) (n_flyfast plane1 city3 city0) (n_flyfast plane1 city4 city0) (n_flyfast plane1 city5 city0))
        3))'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city1 (from any origin city, using either slow or fast flight) must never exceed 3")
    d.encoding = '''(always (<= (+ (n_flyslow plane1 city0 city1) (n_flyslow plane1 city1 city1) (n_flyslow plane1 city2 city1) (n_flyslow plane1 city3 city1) (n_flyslow plane1 city4 city1) (n_flyslow plane1 city5 city1) (n_flyfast plane1 city0 city1) (n_flyfast plane1 city1 city1) (n_flyfast plane1 city2 city1) (n_flyfast plane1 city3 city1) (n_flyfast plane1 city4 city1) (n_flyfast plane1 city5 city1)) 3))'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city2 (from any origin city, using either slow or fast flight) must never exceed 3")
    d.encoding = '''(always 
      (<= 
        (+ 
          (n_flyslow plane1 city0 city2) 
          (n_flyslow plane1 city1 city2) 
          (n_flyslow plane1 city2 city2) 
          (n_flyslow plane1 city3 city2) 
          (n_flyslow plane1 city4 city2) 
          (n_flyslow plane1 city5 city2)
          (n_flyfast plane1 city0 city2) 
          (n_flyfast plane1 city1 city2) 
          (n_flyfast plane1 city2 city2) 
          (n_flyfast plane1 city3 city2) 
          (n_flyfast plane1 city4 city2) 
          (n_flyfast plane1 city5 city2)
        ) 
        3
      )
    )'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city3 (from any origin city, using either slow or fast flight) must never exceed 3")
    d.encoding = '''(always 
      (<= 
        (+ 
          (n_flyslow plane1 city0 city3)
          (n_flyslow plane1 city1 city3) 
          (n_flyslow plane1 city2 city3)
          (n_flyslow plane1 city3 city3)
          (n_flyslow plane1 city4 city3)
          (n_flyslow plane1 city5 city3)
          (n_flyfast plane1 city0 city3)
          (n_flyfast plane1 city1 city3)
          (n_flyfast plane1 city2 city3)
          (n_flyfast plane1 city3 city3)
          (n_flyfast plane1 city4 city3)
          (n_flyfast plane1 city5 city3)
        )
        3
      )
    )'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city4 (from any origin city, using either slow or fast flight) must never exceed 3")
    d.encoding = '''(always (<= (+ (n_flyslow plane1 city0 city4) (n_flyslow plane1 city1 city4) (n_flyslow plane1 city2 city4) (n_flyslow plane1 city3 city4) (n_flyslow plane1 city4 city4) (n_flyslow plane1 city5 city4) (n_flyfast plane1 city0 city4) (n_flyfast plane1 city1 city4) (n_flyfast plane1 city2 city4) (n_flyfast plane1 city3 city4) (n_flyfast plane1 city4 city4) (n_flyfast plane1 city5 city4)) 3))'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city5 (from any origin city, using either slow or fast flight) must never exceed 3")
    d.encoding = '''(always (<= (+ (n_flyslow plane1 city0 city5) (n_flyslow plane1 city1 city5) (n_flyslow plane1 city2 city5) (n_flyslow plane1 city3 city5) (n_flyslow plane1 city4 city5) (n_flyfast plane1 city0 city5) (n_flyfast plane1 city1 city5) (n_flyfast plane1 city2 city5) (n_flyfast plane1 city3 city5) (n_flyfast plane1 city4 city5)) 3))'''

    r = CAI.CM.createRaw("Plane1 should never fly to a same city more than twice")
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city0 (from any origin city, using either slow or fast flight) must never exceed 2")
    d.encoding = '''(always (<= 
        (+ (n_flyslow plane1 city0 city0) (n_flyslow plane1 city1 city0) (n_flyslow plane1 city2 city0) (n_flyslow plane1 city3 city0) (n_flyslow plane1 city4 city0) (n_flyslow plane1 city5 city0)
          (n_flyfast plane1 city0 city0) (n_flyfast plane1 city1 city0) (n_flyfast plane1 city2 city0) (n_flyfast plane1 city3 city0) (n_flyfast plane1 city4 city0) (n_flyfast plane1 city5 city0))
        2))'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city1 (from any origin city, using either slow or fast flight) must never exceed 2")
    d.encoding = '''(always (<= (+ (n_flyslow plane1 city0 city1) (n_flyslow plane1 city1 city1) (n_flyslow plane1 city2 city1) (n_flyslow plane1 city3 city1) (n_flyslow plane1 city4 city1) (n_flyslow plane1 city5 city1) (n_flyfast plane1 city0 city1) (n_flyfast plane1 city1 city1) (n_flyfast plane1 city2 city1) (n_flyfast plane1 city3 city1) (n_flyfast plane1 city4 city1) (n_flyfast plane1 city5 city1)) 2))'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city2 (from any origin city, using either slow or fast flight) must never exceed 2")
    d.encoding = '''(always 
      (<= 
        (+ 
          (n_flyslow plane1 city0 city2) 
          (n_flyslow plane1 city1 city2) 
          (n_flyslow plane1 city2 city2) 
          (n_flyslow plane1 city3 city2) 
          (n_flyslow plane1 city4 city2) 
          (n_flyslow plane1 city5 city2)
          (n_flyfast plane1 city0 city2) 
          (n_flyfast plane1 city1 city2) 
          (n_flyfast plane1 city2 city2) 
          (n_flyfast plane1 city3 city2) 
          (n_flyfast plane1 city4 city2) 
          (n_flyfast plane1 city5 city2)
        ) 
        2
      )
    )'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city3 (from any origin city, using either slow or fast flight) must never exceed 2")
    d.encoding = '''(always 
      (<= 
        (+ 
          (n_flyslow plane1 city0 city3)
          (n_flyslow plane1 city1 city3) 
          (n_flyslow plane1 city2 city3)
          (n_flyslow plane1 city3 city3)
          (n_flyslow plane1 city4 city3)
          (n_flyslow plane1 city5 city3)
          (n_flyfast plane1 city0 city3)
          (n_flyfast plane1 city1 city3)
          (n_flyfast plane1 city2 city3)
          (n_flyfast plane1 city3 city3)
          (n_flyfast plane1 city4 city3)
          (n_flyfast plane1 city5 city3)
        )
        2
      )
    )'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city4 (from any origin city, using either slow or fast flight) must never exceed 2")
    d.encoding = '''(always (<= (+ (n_flyslow plane1 city0 city4) (n_flyslow plane1 city1 city4) (n_flyslow plane1 city2 city4) (n_flyslow plane1 city3 city4) (n_flyslow plane1 city4 city4) (n_flyslow plane1 city5 city4) (n_flyfast plane1 city0 city4) (n_flyfast plane1 city1 city4) (n_flyfast plane1 city2 city4) (n_flyfast plane1 city3 city4) (n_flyfast plane1 city4 city4) (n_flyfast plane1 city5 city4)) 2))'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city5 (from any origin city, using either slow or fast flight) must never exceed 2")
    d.encoding = '''(always (<= (+ (n_flyslow plane1 city0 city5) (n_flyslow plane1 city1 city5) (n_flyslow plane1 city2 city5) (n_flyslow plane1 city3 city5) (n_flyslow plane1 city4 city5) (n_flyfast plane1 city0 city5) (n_flyfast plane1 city1 city5) (n_flyfast plane1 city2 city5) (n_flyfast plane1 city3 city5) (n_flyfast plane1 city4 city5)) 2))'''

    r = CAI.CM.createRaw("Plane1 should never fly to a same city more than once")
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city0 (from any origin city, using either slow or fast flight) must never exceed 1")
    d.encoding = '''(always (<= 
        (+ (n_flyslow plane1 city0 city0) (n_flyslow plane1 city1 city0) (n_flyslow plane1 city2 city0) (n_flyslow plane1 city3 city0) (n_flyslow plane1 city4 city0) (n_flyslow plane1 city5 city0)
          (n_flyfast plane1 city0 city0) (n_flyfast plane1 city1 city0) (n_flyfast plane1 city2 city0) (n_flyfast plane1 city3 city0) (n_flyfast plane1 city4 city0) (n_flyfast plane1 city5 city0))
        1))'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city1 (from any origin city, using either slow or fast flight) must never exceed 1")
    d.encoding = '''(always (<= (+ (n_flyslow plane1 city0 city1) (n_flyslow plane1 city1 city1) (n_flyslow plane1 city2 city1) (n_flyslow plane1 city3 city1) (n_flyslow plane1 city4 city1) (n_flyslow plane1 city5 city1) (n_flyfast plane1 city0 city1) (n_flyfast plane1 city1 city1) (n_flyfast plane1 city2 city1) (n_flyfast plane1 city3 city1) (n_flyfast plane1 city4 city1) (n_flyfast plane1 city5 city1)) 1))'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city2 (from any origin city, using either slow or fast flight) must never exceed 1")
    d.encoding = '''(always 
      (<= 
        (+ 
          (n_flyslow plane1 city0 city2) 
          (n_flyslow plane1 city1 city2) 
          (n_flyslow plane1 city2 city2) 
          (n_flyslow plane1 city3 city2) 
          (n_flyslow plane1 city4 city2) 
          (n_flyslow plane1 city5 city2)
          (n_flyfast plane1 city0 city2) 
          (n_flyfast plane1 city1 city2) 
          (n_flyfast plane1 city2 city2) 
          (n_flyfast plane1 city3 city2) 
          (n_flyfast plane1 city4 city2) 
          (n_flyfast plane1 city5 city2)
        ) 
        1
      )
    )'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city3 (from any origin city, using either slow or fast flight) must never exceed 1")
    d.encoding = '''(always 
      (<= 
        (+ 
          (n_flyslow plane1 city0 city3)
          (n_flyslow plane1 city1 city3) 
          (n_flyslow plane1 city2 city3)
          (n_flyslow plane1 city3 city3)
          (n_flyslow plane1 city4 city3)
          (n_flyslow plane1 city5 city3)
          (n_flyfast plane1 city0 city3)
          (n_flyfast plane1 city1 city3)
          (n_flyfast plane1 city2 city3)
          (n_flyfast plane1 city3 city3)
          (n_flyfast plane1 city4 city3)
          (n_flyfast plane1 city5 city3)
        )
        1
      )
    )'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city4 (from any origin city, using either slow or fast flight) must never exceed 1")
    d.encoding = '''(always (<= (+ (n_flyslow plane1 city0 city4) (n_flyslow plane1 city1 city4) (n_flyslow plane1 city2 city4) (n_flyslow plane1 city3 city4) (n_flyslow plane1 city4 city4) (n_flyslow plane1 city5 city4) (n_flyfast plane1 city0 city4) (n_flyfast plane1 city1 city4) (n_flyfast plane1 city2 city4) (n_flyfast plane1 city3 city4) (n_flyfast plane1 city4 city4) (n_flyfast plane1 city5 city4)) 1))'''
    d = CAI.CM.createDecomposed(r, "The total number of times plane1 flies to city5 (from any origin city, using either slow or fast flight) must never exceed 1")
    d.encoding = '''(always (<= (+ (n_flyslow plane1 city0 city5) (n_flyslow plane1 city1 city5) (n_flyslow plane1 city2 city5) (n_flyslow plane1 city3 city5) (n_flyslow plane1 city4 city5) (n_flyfast plane1 city0 city5) (n_flyfast plane1 city1 city5) (n_flyfast plane1 city2 city5) (n_flyfast plane1 city3 city5) (n_flyfast plane1 city4 city5)) 1))'''
    
    r = CAI.CM.createRaw("Person1 and person3 should travel together. By this I mean that person1 and 3 should either be in the same plane, either be in the same city, either if one is in a plane then the other should be in the city where the plane is.")
    d = CAI.CM.createDecomposed(r, "Person1 and person3 should either be in the same plane, in the same city, or when if one is in a plane then other should be in the city where the place is located.")
    d.encoding = '''(always (or
      (exists (?a - aircraft) (and (in person1 ?a) (in person3 ?a)))
      (exists (?c - city) (and (located person1 ?c) (located person3 ?c)))
      (exists (?a - aircraft ?c - city) (and (in person1 ?a) (located person3 ?c) (located ?a ?c)))
      (exists (?a - aircraft ?c - city) (and (in person3 ?a) (located person1 ?c) (located ?a ?c)))
    )))'''

#########################################################################################################

@click.command(help=f"{KNOWN_PROBLEMS_STR}")
@click.argument('problem_name', default='zeno13_n') # zeno13_n, zeno5, rover8_n
@click.option('-a', '--anytime', 'planning_mode', flag_value=PlanMode.ANYTIME, default=True, help="Set the planning mode to 'Anytime' (default)")
@click.option('-aa', '--anytimeauto', 'planning_mode', flag_value=PlanMode.ANYTIMEAUTO, help="Set the planning mode to 'AnytimeAuto'")
@click.option('-d', '--default', 'planning_mode', flag_value=PlanMode.DEFAULT, help="Set the planning mode to 'Default'")
@click.option('-o', '--optimal', 'planning_mode', flag_value=PlanMode.OPTIMAL, help="Set the planning mode to 'Optimal'")
@click.option('-s', '--satisficing', 'planning_mode', flag_value=PlanMode.SATISFICING, help="Set the planning mode to 'Satisficing'")
@click.option('-t', '--timeout', 'timeout', default=15.0, help="Timeout for planning")
@click.option('--e2nl', 'e2nl', is_flag=True, default=False, help="Activates the translation of encodings back to NL")
def main(problem_name, planning_mode, timeout, e2nl):
    faulthandler.enable()
    
    
    # Init CAI 
    CAI.init(problem_name, planning_mode, timeout, e2nl)
    # initZeno5()
    # initZeno13()
    # initDemo()
    # CAI.CM.load('validated.json)
    
    # Create main GUI app
    app = GUI.App()
    
    # Show settings
    CAI.showSettings()
    
    # FOR ABLATION # A, B, or C
    # ablation(app, 'A') 
    
    app.mainloop()
if __name__ == '__main__':
    main()
  
#### Notes ####
#   '''(always (forall (?a - aircraft)
#   (or (not (in person1 ?a))
#       (or (in person3 ?a)
#           (exists (?c - city)
#             (and (located ?a ?c)
#                  (located person3 ?c)))))))'''
# '''(always (forall (?a - aircraft)
#     (or (not (in person3 ?a))
#         (in person1 ?a)
#         (exists (?c - city)
#           (and (located ?a ?c) (located person1 ?c))))))'''
#  
#  Seems to be equivalent to 
#  (OR
#    Person1 not in aircraft and Person3 not in aircraft
#    Person1 and Person3 in aircraft
#    Person1 in city of aircraft
#    Person3 in city of aircraft
#  )
# 
# => Unsolvable problem....