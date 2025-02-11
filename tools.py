from unified_planning.io import PDDLReader

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
        filteredEncoding = '\n(:constraints ' + encodedPref[i_s:i+1] + ')\n'
    else:
        filteredEncoding = '\n' + encodedPref[i_s:i+1] + '\n'
    return filteredEncoding

def initialFixes(filteredEncoding):
    i = filteredEncoding.find('at end')
    if i!=-1:
        filteredEncoding = filteredEncoding[:i] + 'at-end' + filteredEncoding[i+len('at-end'):]
        print('Fixed at end -> at-end')
    return filteredEncoding

def updateProblem(problem, filteredEncoding):
    """
    Currently MOCK
    """
    updatedProblem = None 
    
    # Find position to insert (last parenthesis)
    i_insert=len(problem)-1
    while True:
        if problem[i_insert]==')':
            break
        i_insert-=1
    
    # Insert constraints into problem
    updatedProblem = problem[:i_insert] + filteredEncoding + problem[i_insert:]
    
    return updatedProblem

def verifyEncoding(updatedProblem, domain, filteredEncoding):
    """
    Should look for action_name, specific unsupported constraints (e.g. imply)
    return encodingOk: Bool, error_description: str
    """
    
    # Parsing test
    reader = PDDLReader()
    try:
        pddl_problem = reader.parse_problem_string(domain, updatedProblem)
    except:
        return False, "Unable to parse the updated problem with the encoding. The encoding is probably erroneous, try again."
    
    domain_specific_keywords = [f.name for f in pddl_problem.fluents]
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
    authorized_keywords = PDDL_keywords + domain_specific_keywords

    # Split into a list
    A = filteredEncoding.split(' ')

    B = []
    for t in A:
        B += t.split('\n')
    A = B
    
    B = []
    for t in A:
        if t != '':
            B += [t]
    A = B

    B = []
    for t in A:
        if t[0]=='(':
            B += [t[0]] + [t[1:]]
        else:
            B += [t]
    A = B

    del B, t


    for i in range(len(A)):
        w = A[i]
        if w=='(':
            w_next = A[i+1]
            if w_next not in authorized_keywords:
                if w_next[0]=='?':
                    continue
                
                return False, f"{w_next} isn't a known PDDL keyword or part of the domain description. Re-encode correctly."
            
    # encodingOk, error_description
    return True, ""
