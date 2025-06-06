import numeric_tcore.parsing_extensions as ntcore_parsing_ext

def filterEncoding(encodedPref):
    
    # Skip ':(constraints' if included
    i_s = encodedPref.find('(:constraints')
    if i_s==-1:
        i_s = 0
    else:
        i_s += len('(:constraints')
    
    # Find first open parenthesis
    i_s = encodedPref.find('(', i_s)
    if i_s == -1:
        raise Exception("tools:updateProblem: Can't find encoded contraints in text...")
    
    # Find the matching closing parenthesis
    n=1
    i=i_s
    while True:
        i+=1
        if encodedPref[i]=='(':
            n+=1
        if encodedPref[i]==')':
            n-=1
        if n==0:
            break
    
    # Keep only the parenthesis
    filteredEncoding = encodedPref[i_s:i+1]
    
    return filteredEncoding

def initialFixes(filteredEncoding):
    i = filteredEncoding.find('at end')
    if i!=-1:
        filteredEncoding = filteredEncoding[:i] + 'at-end' + filteredEncoding[i+len('at-end'):]
        print('Fixed at end -> at-end')
    return filteredEncoding

def updateProblem(problem, encodings):
    updatedProblem = None 
    
    # Find position to insert 
    ## find metric
    i_metric = problem.find("(:metric")
    if i_metric!=-1:
        i_insert = i_metric
    ## Else, insert before last parenthesis
    else:
        i_insert=len(problem)-1
        while problem[i_insert]!=')':
            i_insert-=1
    
    # Insert constraints into problem
    encodings_str = "\n".join(encodings)
    updatedProblem = problem[:i_insert] + "\n(:constraints\n" + encodings_str + '\n)\n' + problem[i_insert:]
    
    return updatedProblem

def parse_pddl3(domain_path, problem_path):
    return ntcore_parsing_ext.parse_pddl3(domain_path, problem_path)
def parse_pddl3_str(domain, updatedProblem):
    """
    Adapted from NTCORE parsing_extensions to take string as input instead of file_paths
    """
    reader = ntcore_parsing_ext.PDDLReader()
    parser_extensions = ntcore_parsing_ext.ParserExtension()
    reader._trajectory_constraints["at-end"] = parser_extensions.parse_atend
    reader._trajectory_constraints["within"] = parser_extensions.parse_within
    reader._trajectory_constraints["hold-after"] = parser_extensions.parse_holdafter
    reader._trajectory_constraints["hold-during"] = parser_extensions.parse_holdduring
    reader._trajectory_constraints["always-within"] = parser_extensions.parse_alwayswithin
    problem = reader.parse_problem_string(domain, updatedProblem)
    quantitative_constrants = parser_extensions.constraints
    return ntcore_parsing_ext.PDDL3QuantitativeProblem(problem, quantitative_constrants)

g_fluent_names = []
def set_fluent_names(names):
    global g_fluent_names
    g_fluent_names = names

g_typed_objects = []
def set_typed_objects(objects):
    global g_typed_objects
    g_typed_objects = objects

g_all_objects = []
def set_all_objects(objects):
    global g_all_objects
    g_all_objects = objects

def verifyEncoding(updatedProblem, domain, filteredEncoding):
    """
    Should look for action_name, specific unsupported constraints (e.g. imply)
    return encodingOk: Bool, error_description: str
    """
    
    # Keyword
    PDDL_keywords =[
        ':constraints',
        'and',
        'or',
        'not',
        '=',
        '<',
        '<=',
        '>',
        '>=',
        '+',
        '-',
        '*',
        '/',
        'forall',
        'exists']
    TEMPORAL_keywords =[
        'always',
        'sometime',
        'within',
        'at-most-once',
        'sometime-after',
        'sometime-before',
        'always-within',
        'holding-during',
        'hold-after',
        'at-end',
    ]
    authorized_keywords = PDDL_keywords + TEMPORAL_keywords + g_fluent_names + g_all_objects + [object_type for object_type in g_typed_objects] + ['(', ')']

    L = filteredEncoding
    L = " ( ".join(L.split('('))
    L = " ) ".join(L.split(')'))
    L = " ".join(L.split())
    L = L.split()
    
    # Check if temporal keyword present
    temporal_present = False
    for keyword in TEMPORAL_keywords:
        if keyword in L:
            temporal_present = True
            break
    if not temporal_present:
        print("No temporal keywords")
        print('\t'+filteredEncoding)
        return False, "There is no temporal logic keyword, this is mandatory for a correct PDDL3.0 constraint. Try again."

    # Unknown keyword test #
    for x in L:
        if x not in authorized_keywords:
            try: float(x)
            except:
                try: assert x[0]=='?'
                except:
                    if x in ['imply', 'implies']:
                        print('imply detected')
                        print('\t'+filteredEncoding)
                    return False, f"{x} is not a supported PDDL keyword or part of problem description. Try again to translate correctly."
            
    # Parsing test #
    try:
        parse_pddl3_str(domain, updatedProblem)
    except Exception as err:
        return False, "There is a syntax error. Try again carefully to translate correctly."
    
    # encodingOk, error_description
    return True, ""

def extractTag(tag, txt):
    i_1 = txt.find(f"<{tag}>")
    if i_1==-1:
        raise Exception(f"Can't find tag <{tag}>")
    
    i_2 = txt.find(f"</{tag}>")
    if i_2==-1:
        raise Exception(f"Can't find closing tag </{tag}>")
    
    txt = txt[ i_1 + len(f"<{tag}>") : i_2 ]
    
    if txt[0]=='\n':
        txt = txt[1:]
    if txt[-1]=='\n':
        txt = txt[:-1]
    
    return txt

