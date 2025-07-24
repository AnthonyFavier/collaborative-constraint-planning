from defs import *
from datetime import datetime
import jsonpickle

class Constraint:
    _ID = 0
    def __init__(self, nl_constraint):
        self.symbol = 'C'+str(Constraint._ID)
        self.nl_constraint = nl_constraint
        Constraint._ID += 1

class RawConstraint(Constraint):
    def __init__(self, nl_constraint):
        super().__init__(nl_constraint)
        self.children = [] # children 
        self.symbol = 'R' + self.symbol[1:]
        self.decomp_conv = None
        
        # times
        self.time_input = 0
        self.time_initial_decomp = 0
        self.time_decomp_validation = 0
        self.time_redecomp = 0
        self.time_initial_encoding = 0
    
    def activate(self):
        for c in self.children:
            c.activate()
    def deactivate(self):
        for c in self.children:
            c.deactivate()
    def isActivated(self):
        for c in self.children:
            if not c.isActivated():
                return False
        return True
    def isPartiallyActivated(self):
        if not self.isActivated():
            for c in self.children:
                if c.isActivated():
                    return True
        return False
    
    def strChildren(self):
        txt = ""
        for c in self.children:
            txt += "\t" + str(c) + '\n'
            if c.encoding!='':
                print("\t\t" + c.encoding)
                txt += "\t\t" + c.encoding
        return txt
        
    def strWithChildren(self):
        txt = str(self)+'\n'
        for c in self.children:
            txt += "\t" + str(c) + '\n'
            if c.encoding!='':
                txt += "\t\t" + c.encoding + '\n'
        return txt
    def showWithChildren(self):
        print(self.strWithChildren())
        
    def __repr__(self):
        symbol_str = self.symbol 
        if self.isActivated():
            symbol_str = symbol_str
        return f"{symbol_str} - {self.nl_constraint}"
    
class DecomposedConstraint(Constraint):
    def __init__(self, parent, nl_constraint):
        super().__init__(nl_constraint)
        self.parent = parent
        self.symbol = 'D' + self.symbol[1:]
        self.encoding = ''
        self.e2nl = ''
        self._activated = True
        self.encoding_conv = None
        self.nb_retries = 0 # = try -1
        self.nb_e2nl_retries = 0 # = try -1
        
        # times
        self.time_encoding = 0
        self.time_verifier = 0
        self.time_reencoding = 0
        self.time_e2nl = 0
        self.time_e2nl_validation = 0
        self.time_e2nl_reencoding = 0 
        
    def deactivate(self):
        self._activated = False
    def activate(self):
        self._activated = True
    def isActivated(self):
        return self._activated
    def isPartiallyActivated(self):
        return False
    
    def __repr__(self):
        symbol_str = self.symbol 
        if self.isActivated():
            symbol_str = symbol_str
        return f"{symbol_str} - {self.nl_constraint}"

class ConstraintManager:
    def __init__(self, problem_name):
        self.problem_name = problem_name
        self.constraints = {} # symbol: constraint
        self.raw_constraints = {} # symbol: Constraint
        self.decomposed_constraints = {} # symbol: DecomposedConstraint
        
    def createRaw(self, nl_constraint):
        c = RawConstraint(nl_constraint)
        self.constraints[c.symbol] = c
        self.raw_constraints[c.symbol] = c
        return c
        
    def createDecomposed(self, parent, nl_constraint):
        c = DecomposedConstraint(parent, nl_constraint)
        parent.children.append(c)
        self.constraints[c.symbol] = c
        self.decomposed_constraints[c.symbol] = c
        return c
        
    def show(self):
        print("\nConstraint List:")
        if self.constraints=={}:
            print("[No constraint]")
            return None
        
        for key,rc in self.raw_constraints.items():
            rc.showWithChildren()
            
    def deleteConstraints(self, symbols, autoremoveparent=True):
        # if R# remove raw constraint and all decomposed associated
        # if D# remove only decompose from general list and from parent children
        for symbol in symbols:
            if symbol not in self.constraints:
                # already deleted
                continue
        
            if symbol in self.raw_constraints:
                constraint = self.constraints[symbol]
                self.constraints.pop(constraint.symbol)
                self.raw_constraints.pop(constraint.symbol)
                for child in constraint.children:
                    self.constraints.pop(child.symbol)
                    self.decomposed_constraints.pop(child.symbol)
                    del child
                del constraint
                
            elif symbol in self.decomposed_constraints:
                constraint = self.constraints[symbol]
                    
                self.constraints.pop(constraint.symbol)
                self.decomposed_constraints.pop(constraint.symbol)
                constraint.parent.children.remove(constraint)
                
                if autoremoveparent and len(constraint.parent.children)==0:
                    self.constraints.pop(constraint.parent.symbol)
                    self.raw_constraints.pop(constraint.parent.symbol)
                    del constraint.parent
                
                del constraint
                
    def deleteChildren(self, r):
        self.deleteConstraints([c.symbol for c in r.children], autoremoveparent=False)
                
    def clean(self):
        # Look for constraints to delete

        # - raw constraint without decomposition
        to_delete = []
        for id, r in self.raw_constraints.items():
            if r.children == []:
                print(f"Deleted {r.symbol}: no decomposition")
                to_delete.append(r)
        self.deleteConstraints(to_delete)
        
        # - decomposed constraint without encoding
        to_delete = []
        for id, d in self.decomposed_constraints.items():
            if d.encoding == '':
                print(f"Deleted {d.symbol}: no encoding")
                to_delete.append(d)
        self.deleteConstraints(to_delete)
        
    def dump(self, problem_name):
        date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
        with open(f"dumps_CM/{problem_name}_{date}.json", 'w') as f:
            json_string = jsonpickle.encode(self, indent=4)
            f.write(json_string)
        
    def load(self, filename):
        
        with open(filename, 'r') as f:
            txt = f.read()
        
        loaded = jsonpickle.decode(txt)
        
        # Check problem name
        if loaded.problem_name!=self.problem_name:
            mprint("\nERROR: can't load constraints from another problem ... Aborted")
            return None
        
        self.constraints = loaded.constraints
        self.raw_constraints = loaded.raw_constraints
        self.decomposed_constraints = loaded.decomposed_constraints
        
        # init Constraint._ID
        max = -1
        for id in self.constraints:
            n = int(id[1:])
            if n>max:
                max = n
        Constraint._ID = max+1
        
        mprint("\nConstraints loaded")
        