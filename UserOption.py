from defs import *

class Option:
    def __init__(self, abvr, text):
        self.abvr = abvr
        self.text = text
        
class UserOption:
    """
    Allow to easily create an option list for the user to choose from 
    """
    def __init__(self):
        self.options = {} # {i, Option}
        
    def addOption(self, abvr, text):
        self.options[len(self.options)+1] = Option(abvr, text)
        
    def ask(self):
        ok = False
        while not ok:
            
            print(' ')
            
            for k,o in self.options.items():
                print(f"{k}- {o.text}")
                
            x = input(color.BOLD + "Select an option: " + color.END)
            print(' ')
            try:
                x = int(x)
                self.options[x]
                ok = True
            except:
                print("\nWrong input\n")
                pass
            
        return self.options[x].abvr
            
            