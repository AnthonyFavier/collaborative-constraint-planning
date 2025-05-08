import numeric_tcore.parsing_extensions as ntcore_parsing_ext

def filterEncoding(encodedPref):
    i = i_s = encodedPref.find('(:constraints')
    with_constraints = True
    
    if i_s == -1:
        i = i_s = encodedPref.find('(')
        with_constraints = False
        
    if i_s == -1:
        raise Exception("tools:updateProblem: Can't find encoded contraints in text...")
    
    n=1
    while True:
        i+=1
        if encodedPref[i]=='(':
            n+=1
        if encodedPref[i]==')':
            n-=1
        if n==0:
            break
        
    if not with_constraints:
        filteredEncoding = encodedPref[i_s:i+1]
    else:
        filteredEncoding = encodedPref[i_s+len('(:constraints'):i+1]
        
        
        
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

g_objects = []
def set_objects(objects):
    global g_objects
    g_objects = objects

def verifyEncoding(updatedProblem, domain, filteredEncoding):
    """
    Should look for action_name, specific unsupported constraints (e.g. imply)
    return encodingOk: Bool, error_description: str
    """
    
    # Keyword test
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
        'exists',
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
    authorized_keywords = PDDL_keywords + g_fluent_names

    L = filteredEncoding
    L = " ( ".join(L.split('('))
    L = " ) ".join(L.split(')'))
    L = " ".join(L.split())
    L = L.split()


    # Check if no unknown keyword
    for i in range(len(L)):
        if L[i]=='(':
            if L[i+1] not in authorized_keywords:
                if L[i+1][0]=='?':
                    continue
                
                return False, f"{L[i+1]} isn't a known PDDL keyword or part of the domain description. Try again carefully to translate correctly."
            
    # Parsing test
    try:
        parse_pddl3_str(domain, updatedProblem)
    except:
        return False, "There is a syntax error. Try again carefully to translate correctly."
    
    # encodingOk, error_description
    return True, ""

