import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from . import Tools

from numeric_tcore.parsing_extensions import PDDL3QuantitativeProblem

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

    def checkEncoding(self, updatedProblem, domain, filteredEncoding):
        """
        Should look for action_name, specific unsupported constraints (e.g. imply)
        return encodingOk: Bool, error_description: str
        """

        msg = "Can't find tag <"
        if filteredEncoding[:len(msg)]==msg:
            print(f"[VERIFIER]'\n{filteredEncoding}")
            logger.info(f"[VERIFIER]'\n{filteredEncoding}")
            return filteredEncoding
        
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
        
        # Check if imply present
        # if ('imply' in L) or ('implies' in L):
        #     print('[VERIFIER]')
        #     print('imply detected')
        #     # print('\t'+filteredEncoding)
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
                        # print('\t'+filteredEncoding)
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
            Tools.parse_pddl3_str(domain, updatedProblem)
        except Exception as err:
            return "There is a syntax error."
        
        # encodingOk, error_description
        return 'OK'
