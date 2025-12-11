
"""
Manipulates PDDL parts: parsing, checking PDDL3 constraints, generating PDDL3 problem
"""

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from .. import Globals as G

from numeric_tcore.parsing_extensions import PDDL3QuantitativeProblem
import numeric_tcore.parsing_extensions as ntcore_parsing_ext

###################################################
# Functions to parse and update problem

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

def getProblemWithConstraints(encodings):
    updatedProblem = None 
    
    # Find position to insert 
    ## find metric
    i_metric = G.PROBLEM_PDDL.find("(:metric")
    if i_metric!=-1:
        i_insert = i_metric
    ## Else, insert before last parenthesis
    else:
        i_insert=len(G.PROBLEM_PDDL)-1
        while G.PROBLEM_PDDL[i_insert]!=')':
            i_insert-=1
    
    # Insert constraints into problem
    encodings_str = "\n".join(encodings)
    updatedProblem = G.PROBLEM_PDDL[:i_insert] + "\n(:constraints\n" + encodings_str + '\n)\n' + G.PROBLEM_PDDL[i_insert:]
    
    return updatedProblem

###################################################
# Verifier fixing and checking encodings

verifier = None

class Verifier:
    def __init__(self, problem: PDDL3QuantitativeProblem):
        self.fluent_names = [f.name for f in problem.fluents]
        self.typed_objects = {}
        self.all_objects = []
        for o in problem.all_objects:
            self.all_objects.append(o.name)
            if o.type.name in self.all_objects:
                self.typed_objects[o.type.name].append(o.name)
            else:
                self.typed_objects[o.type.name] = [o.name]

    def initialEncodingFixes(self, encoding):
        # at end
        if (i := encoding.find('at end')) != -1:
            encoding = encoding[:i] + 'at-end' + encoding[i+len('at-end'):]
            print('initialFixes: Fixed at end -> at-end')
            
        # remove :constraints
        if (i := encoding.find('(:constraints'))!=-1:
            i2 = encoding.rfind(')')
            encoding = encoding[i+len('(:constraints'):i2].strip()
            print('initialFixes: :constraints removed')
            
        # remove :constraint
        if (i := encoding.find('(:constraint'))!=-1:
            i2 = encoding.rfind(')')
            encoding = encoding[i+len('(:constraint'):i2].strip()
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
        
        L = encoding
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
            encoding = "(always "+ encoding +")"
            
        return encoding

    def checkEncoding(self, encoding):
        """
        Should look for action_name, specific unsupported constraints (e.g. imply)
        return encodingOk: Bool, error_description: str
        """

        msg = "Can't find tag <"
        if encoding[:len(msg)]==msg:
            print(f"[VERIFIER]'\n{encoding}")
            logger.info(f"[VERIFIER]'\n{encoding}")
            return encoding
        
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
            'exists',
        ]
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
        authorized_keywords = PDDL_keywords + TEMPORAL_keywords + ['(', ')'] \
            + self.fluent_names + self.all_objects + list(self.typed_objects.keys())

        L = encoding
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
        
        # Check if imply present
        # if ('imply' in L) or ('implies' in L):
        #     print('[VERIFIER]')
        #     print('imply detected')
        #     # print('\t'+encoding)
        #     return f"imply is not supported. Try again without it."
        

        # Unknown keyword test #
        for x in L:
            x = x.lower()
            if x not in authorized_keywords:
                try: float(x)
                except:
                    try: assert x[0]=='?'
                    except:
                        print(f"[VERIFIER]\n{x} is not supported")
                        logger.info(f"[VERIFIER]'\n{x} is not supported")
                        # print('\t'+encoding)
                        return f"{x} is not a supported PDDL keyword or part of problem description."
                    
        # Check if temporal keyword present
        # temporal_present = False
        # for keyword in TEMPORAL_keywords:
        #     if keyword in L:
        #         temporal_present = True
        #         break
        # if not temporal_present:
        #     print('[VERIFIER]')
        #     print("No temporal keywords: Always to add")
        #     return "No temporal keywords: Always to add"
        #     # return "There is no temporal logic keyword, this is mandatory for a correct PDDL3.0 constraint."
            
                
        # Parsing test #
        try:
            updatedProblem = getProblemWithConstraints(G.PROBLEM_PDDL, encoding)
            parse_pddl3_str(G.DOMAIN_PDDL, updatedProblem)
        except Exception as err:
            return "There is a syntax error."
        
        # encodingOk, error_description
        return 'OK'

def init_verifier(problem: PDDL3QuantitativeProblem):
    global verifier
    verifier = Verifier(problem)

