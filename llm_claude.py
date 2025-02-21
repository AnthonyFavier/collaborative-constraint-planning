import anthropic
client = anthropic.Anthropic(
    api_key=None
)
MAX_TOKEN=2000
TEMPERATURE=0.0
# MODEL="claude-3-5-haiku-20241022"
MODEL="claude-3-5-sonnet-20241022"

new_pddl_constraints_description="""
As with all previous installations of PDDL, PDDL 3.0 introduces new requirements. It also introduces syntax for defining constraints. Constraints are form of goal which must be satisfied in all states of the plan.

As an additional curiosity note, whilst it may seem that a constraint adds more complexity to a state space, in general it allows us to reduce it significantly, by increasing the number of invalid states.

Example domain:

(define
    (domain logistics)
    (:requirements :preferences :constraints)
    (:types
        lorry package recipient location - object
    )
    (:predicates
        (deliver-to ?r - recipient ?p - package)
        (delivered ?p - package)
        (in ?p - package ?l - lorry)
        (at ?l - lorry ?loc - location)
    )
    (:constraints
        (and
            (forall (?l - lorry ?loc - location) (at-most-once (at ?l ?loc)))
            ... additional constraints omitted
        )
    )
    ; Actions omitted
)

Note that constraints can also be described in the problem, hence using explicit objects defined in the problem, e.g., package1 or lorry2.

Constraints

(:constraints
    <logical_expression>
)

Constraints are a conjunction of various forall/exists statements, which can make use of the keywords designed to facilitate preferences. Constraints are essentially facts which must be true in all states within a valid plan.

Essentially a constraint expresses something we want to always be true, or some state-trajectory constraint (A constraint on how the state changes over time) . e.g.

(:constraints
    (and
        (forall (?l - lorry ?loc - location) (at-most-once (at ?l ?loc)))
        ... additional constraints omitted
    )
)

The single constraint shown above expresses that for each lorry and location, the lorry should visit that location at most once.

These kind of expressions can help planners reduce the number of states they need to explore by enforcing common sense logic.

Now it may seem logical that if packages can be delivered in any particular order and there could potentially be more than one package to be delivered to a single location, that we would want to express that we only visit any given location exactly once with a given lorry (thus preventing us going to the same place twice).

Users of this feature should be cautious of not ruling out non-apparent solutions. If for example we were planning a lorry based on fuel cost, it may be appropriate for a lorry to visit a location (such as a city) twice, once to deliver a package at the start of the journey, and once at the end to refuel for the journey home at a cheap fuel station.
always

    always <predicate>

The always state-trajectory constraint expresses that every state reached in the execution of the plan, contains the predicate specified.

It essentially creates a constant predicate. In the case below we say that package1 is in lorry1 for all states reached by the plan.

    always (in package1 lorry1)

sometime

    sometime <predicate>

The sometime state trajectory constraint expresses at some point within the states reached by a plan, that the predicate specified is true.

It essentially says, at some point, this fact is true. In the case below we’re saying that at some point, lorry1 should be in glasgow

    sometime (at lorry1 glasgow)

within

    within <number> <predicate>

The within state-trajectory constraint express that some predicate must become true within the specified number of plan steps.

This is a rather unusual constraint because it varies between temporal and STRIPS domain. The number in the statement expresses the point in time in temporal plans. The number in the statement expresses the number of plan steps in STRIPS plans.

    within 10 (at lorry1 collectionpoint)

at-most-once

    at-most-once <predicate>

The at-most-once state-trajectory constraint expresses that a fact be true at most once. It is useful to prevent repeated visits to the same fact. e.g.

    at-most-once (at lorry1 theendoftheworld)

sometime-after

    sometime-after <before_predicate> <after_predicate>

The sometime-after state-trajectory constraint expresses that some predicate becomes true, at some point after a separate predicate becomes true.

    sometime-after (at lorry1 london) (at lorry1 pompey)

The above statement expresses that once lorry1 has been in london some point afterwards in should be in pompey.
sometime-before

    sometime-before <after_predicate> <before_predicate>

The sometime-before state-trajectory constraint expresses that some predicate should become true, before a separate predicate becomes true. e.g.

    sometime-before (delivering lorry1) (at lorry1 warehouse)

The above statement expresses that before lorry1 is marked as delivering it should have been at the warehouse (i.e. to pickup goods).
always-within

    always-within <number> <condition> <predicate>

The always within expresses a composition of always and within, essentially it says that whenever some condition/predicate is true, then within the specified number of steps/time, the other predicate should become true.
hold-during

    hold-during <number> <number> <predicate>

The holding-during state-trajectory constraint expresses that a predicate should hold true between the two points in time expressed. Essentially, action as an always with a fixed start and end point.

    hold-during 20 30 (at lorry1 lorrycarpark)

The statement above expresses that lorry1 should be parked between the points in time 20 and 30. If we imagine that time in our problem represents hours, then 20 would be 8PM on the first day, and 30 would be 6AM on the next day.
hold-after

    hold-after <number> <predicate>

The hold-after state-trajectory constraint expresses that a predicate should hold true after some point in time.

Note that this predicate must remain true, forever after the give point. This makes it assymetric to within which only expresses a fact must become true before some point at least once.

    hold-after 40 (empty lorry1)

The above statement indicates that lorry1 should be empty after 40 and remain empty.
"""

g_message_history = []
def clear_message_history():
    global g_message_history
    g_message_history = []

def encodePrefs(domain, problem, preferences):
    global g_message_history
    
    # Setup request
    systemMsg="You are a PDDL planning expert. Your purpose is to translate natural language human preferences into PDDL3.0 constraints to be used in a classical PDDL planner. Respond to the requested translations only with consise and accurate PDDL language. Prefer using 'forall' keyword to simplify the tranlation (e.g. forall((?o - object) ...) instead of enumating all objects). Try to use only existing fluents but you can reasonably create new ones when relevant."
    messages=[
            # {"role": "user", "content": "I will share with you a text describing how PDDL3.0 constraints works. After I will share a PDDL domain followed by a corresponding PDDL problem. After that I will start to share human preferences to translate."},
            # {"role": "user", "content": new_pddl_constraints_description},
            
            {"role": "user", "content": "When translating natural language inputs into PDDL3.0 constraints, only use the following keywords: 'and','or','not','=','<','<=','>','>=','+','-','*','/','forall','exists','always','sometime','within','at-most-once','sometime-after','sometime-before','always-within','holding-during','hold-after','at-end'. After I will share a PDDL domain followed by a corresponding PDDL problem. After that I will start to share human preferences to translate."},
        
            {"role": "assistant", "content": "Got it now share with me the PDDL domain and problem."},
            {"role": "user", "content": domain + '\n' + problem},   
            {"role": "assistant", "content": "Got it now share with me the human preferences to translate."},
            {"role": "user", "content": preferences},
            # {"role": "user", "content":  f"Here are the huma preferences: {preferences}. First, reformule the preferences in two different manner. After, give me the encoding for the given preferences."},
        ]
    
    # Call LLM
    message = client.messages.create( model=MODEL, max_tokens=MAX_TOKEN, temperature=TEMPERATURE, system=systemMsg, messages= messages)
    
    # Update history with request and LLM answer
    g_message_history += messages + [{"role": "assistant", "content": message.content[0].text}]
    
    # print('LLM:', message.content[0].text)
    
    return message.content[0].text

def reencodePrefs(feedback):
    global g_message_history
    
    # Setup request
    system="You are a PDDL planning expert. Your purpose is to translate natural language human preferences into PDDL3.0 constraints to be used in a classical PDDL planner. Respond to the requested translations only with consise and accurate PDDL language. Only when possible, prefer using 'forall' keyword to simplify the tranlation (e.g. forall((?o - object) ...) instead of enumating all objects). Try to use only existing fluents but you can reasonably create new ones when relevant."
    messages=[
            {"role": "user", "content": "Your last translation is incorrect. Carefully generate a new correct translation considering the following feedback: "+feedback},
        ]
    
    # Call LLM
    message = client.messages.create( model=MODEL, max_tokens=MAX_TOKEN, temperature=TEMPERATURE, system=system, messages=g_message_history + messages)
    
    # Update history with request and LLM answer
    g_message_history += messages + [{"role": "assistant", "content": message.content[0].text},]
    
    return message.content[0].text

