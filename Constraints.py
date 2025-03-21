#!/usr/bin/env python3.10
from defs import *

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
    
    def activate(self):
        for c in self.children:
            c.activate()
    def deactivate(self):
        for c in self.children:
            c.deactivate()
    def isActivated(self):
        for c in self.children:
            if not c._activated:
                return False
        return True
        
    def strWithChildren(self):
        txt = str(self)+'\n'
        for c in self.children:
            txt += "\t" + str(c) + '\n'
            if c.encoding!='':
                print("\t\t" + c.encoding)
                txt += "\t\t" + c.encoding
        return txt
    def showWithChildren(self):
        print(self.strWithChildren())
        
    def __repr__(self):
        symbol_str = self.symbol 
        if self.isActivated():
            symbol_str = color.BOLD + symbol_str + color.END
        return f"{symbol_str} - {self.nl_constraint}"
        
class DecomposedConstraint(Constraint):
    def __init__(self, parent, nl_constraint):
        super().__init__(nl_constraint)
        self.parent = parent
        self.symbol = 'D' + self.symbol[1:]
        self.encoding = ''
        self._activated = True
        
    def deactivate(self):
        self._activated = False
    def activate(self):
        self._activated = True
    def isActivated(self):
        return self._activated
    
    def __repr__(self):
        symbol_str = self.symbol 
        if self.isActivated():
            symbol_str = color.BOLD + symbol_str + color.END
        return f"{symbol_str} - {self.nl_constraint}"

class ConstraintManager:
    def __init__(self):
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
        print(color.BOLD + "\nConstraint List:" + color.END)
        if self.constraints=={}:
            print("[No constraint]")
            return None
        
        for key,rc in self.raw_constraints.items():
            rc.showWithChildren()
        