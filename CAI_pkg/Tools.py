import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import numeric_tcore.parsing_extensions as ntcore_parsing_ext

def initialFixes(filteredEncoding):
    
    # at end
    if (i := filteredEncoding.find('at end')) != -1:
        filteredEncoding = filteredEncoding[:i] + 'at-end' + filteredEncoding[i+len('at-end'):]
        print('initialFixes: Fixed at end -> at-end')
        
    # remove :constraints
    if (i := filteredEncoding.find('(:constraints'))!=-1:
        i2 = filteredEncoding.rfind(')')
        filteredEncoding = filteredEncoding[i+len('(:constraints'):i2].strip()
        print('initialFixes: :constraints removed')
        
    # remove :constraint
    if (i := filteredEncoding.find('(:constraint'))!=-1:
        i2 = filteredEncoding.rfind(')')
        filteredEncoding = filteredEncoding[i+len('(:constraint'):i2].strip()
        print('initialFixes: :constraint removed')
    
    # add always
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
        # 'imply',
        # 'implies',
    ]
    
    L = filteredEncoding
    # remove comments
    while True:
        i1 = L.find(';')
        if i1==-1:
            break
        i2 = L.find('\n', i1)
        L = L[:i1] + L[i2:]
    L = " ( ".join(L.split('('))
    L = " ) ".join(L.split(')'))
    L = " ".join(L.split())
    L = L.split()
    
    temporal_present = False
    for keyword in TEMPORAL_keywords:
        if keyword in L:
            temporal_present = True
            break
    if not temporal_present:
        print("initialFixes: No temporal keywords -> 'always' to add")
        filteredEncoding = "(always "+ filteredEncoding +")"
        
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

def checkTag(tag, txt):
    opening_tag = txt.find(f'<{tag}>')!=-1
    closing_tag = txt.find(f'</{tag}>')!=-1
    
    if not opening_tag and not closing_tag:
        return 'missing_both'
    elif not opening_tag:
        return 'missing_opening'
    elif not closing_tag:
        return 'missing_closing'
    else:
        return 'ok'

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

