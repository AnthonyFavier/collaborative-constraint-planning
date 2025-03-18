import anthropic
client = anthropic.Anthropic(
    api_key=None
)
MAX_TOKEN=5000
TEMPERATURE=0.0
MODEL="claude-3-7-sonnet-20250219"


g_message_history = []
def clear_message_history():
    global g_message_history
    g_message_history = []

def decompose(domain, problem, constraint):
    global g_message_history
    
    # Setup request
    # systemMsg="You are a PDDL planning expert and your purpose is to decompose constraints given in natural language into lower level constraints that can be applied to a given PDDL problem. Doing so consists in rephrasing and decomposing the initial contraint into one or several to remove ambiguities and match the predicates defined in the PDDL problem. It's important to note that constraints cannot directly affect an action, only predicates describing the state of the world. For example, the constraint 'Never use plane1.' could be decomposed into 'There should always be nobody onboard plane1.' and 'Plane1 should always be in its initial city.'. The final constraints should be in natural language but match a linear temporal logic description as in the given example."
    
    systemMsg="Your role is to decompose natural language constraints into natural language lower-level constraints to later apply them to a given PDDL problem. Doing so consists in rephrasing and decomposing the initial contraint into one or several to remove ambiguities and more importantly to match the predicates defined in a given PDDL problem. It's important to note that constraints cannot directly affect an action, only predicates describing the state of the world. The lower-level constraints should be in natural language, no PDDL, and refer to predicates."
    
    messages=[
            {"role": "user", "content": "I will share a PDDL domain followed by a corresponding PDDL problem. After that, I will share the constraint to decompose."},
            {"role": "assistant", "content": "Got it now share with me the PDDL domain and problem."},
            {"role": "user", "content": domain + '\n' + problem},   
            {"role": "assistant", "content": "Got it now share with me the constraints to decompose. I will format my answer in a very clear and consise numbered list where the lower-level constraints referring to predicates are the main items and the subitems are explanations or descriptions. I should not put any PDDL code in the main items."},
            {"role": "user", "content": constraint},
        ]
    
    # Call LLM
    message = client.messages.create( model=MODEL, max_tokens=MAX_TOKEN, temperature=TEMPERATURE, system=systemMsg, messages= messages)
    
    # Update history with request and LLM answer
    g_message_history += messages + [{"role": "assistant", "content": message.content[0].text}]
    
    print('[LLM]\n', message.content[0].text, "\n[END LLM]")
    
    return message.content[0].text

def oldremoveFormating(text):
    
    # Setup request
    systemMsg="You're expected to work as a text formatter. You will be given a text including a numbered list where the main items correspond to constraints and the subitems to explanations. Your job is first to only extract the mains items from the list, not the associated description or explanation. Then, you should remove any formatting and output each extracted constraint on a new line. Each item should eventually be on a new line, without any number or symbol. There should be no empty line."
    
    messages=[
            {"role": "user", "content": text},
        ]
    
    # Call LLM
    message = client.messages.create( model=MODEL, max_tokens=MAX_TOKEN, temperature=TEMPERATURE, system=systemMsg, messages= messages)
    
    print('[LLM]\n', message.content[0].text, "\n[END LLM]")
    
    # t = [ f'{l}\n' for l in message.content[0].text.splitlines() ]
    
    return message.content[0].text

def removeFormating(text):
    
    # Remove initial white spaces and empty lines
    newtext = ""
    for l in text.splitlines():
        if l=='':
            continue
        i = 0
        while i<len(l) and l[i]==' ':
            i+=1
        l = l[i:]
        newtext += l + '\n'
        
        
    # Get main items
    main_items = []
    for l in newtext.splitlines():
        try:
            int(l[0])
            main_items.append(l)
        except:
            continue
    
    symbols = [
        '#',
        '*',
        '=',
        '-',
    ]
    
    newtext = ""
    for l in main_items:
        for s in symbols:
            l = l.replace(s, '')
        i = 0
        while not l[i].isalpha():
            i+=1
        l = l[i:]
        newtext += l + '\n'
    newtext = newtext[:-1]
        
    return newtext

def encodePrefs(domain, problem, constraint):
    global g_message_history
    
    # Setup request
    systemMsg="You are a PDDL planning expert. Your purpose is to translate natural language constraints into PDDL3.0 constraints to be used in a classical PDDL planner. Respond to the requested translations only with consise and accurate PDDL language. PDDL3.0 constraints should only concer predicates and functions, they cannot refer directly to actions."
    
    messages=[
            {"role": "user", "content": "When translating natural language inputs into PDDL3.0 constraints, only use the following keywords: 'and','or','not','=','<','<=','>','>=','+','-','*','/','forall','exists','always','sometime','within','at-most-once','sometime-after','sometime-before','always-within','holding-during','hold-after','at-end'. After, I will share a PDDL domain followed by a corresponding PDDL problem. After that, I will share a contraint to translate."},
        
            {"role": "assistant", "content": "Got it now share with me the PDDL domain and problem."},
            {"role": "user", "content": domain + '\n' + problem},   
            {"role": "assistant", "content": "Got it now share with me the constraint to translate."},
            {"role": "user", "content": constraint},
        ]
    
    # Call LLM
    message = client.messages.create( model=MODEL, max_tokens=MAX_TOKEN, temperature=TEMPERATURE, system=systemMsg, messages= messages)
    
    # Update history with request and LLM answer
    g_message_history += messages + [{"role": "assistant", "content": message.content[0].text}]
    
    print('LLM:', message.content[0].text, "[END LLM]")
    
    return message.content[0].text

if __name__=='__main__':
    text = """
    # Decomposition of "Never use plane1" constraint

    This constraint needs to be decomposed into lower-level constraints that prevent the use of plane1 in any capacity:

    1. **Plane1 should never have any person on board**
    - This means: The predicate `(in ?p - person plane1)` should never be true for any person
    - This prevents anyone from boarding plane1

    2. **Plane1 should never change its location**
    - This means: The predicate `(located plane1 ?c - city)` should remain unchanged from its initial value
    - This prevents plane1 from flying between cities

    3. **The onboard count for plane1 should always remain at 0**
    - This means: The function `(onboard plane1)` should always equal 0
    - This ensures no boarding actions are performed with plane1

    These constraints collectively ensure that plane1 is never used for transportation, refueling, or any other purpose in the solution plan. 
    """

    print(removeFormating(text))