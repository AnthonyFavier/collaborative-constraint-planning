import logging
from datetime import datetime
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from pathlib import Path

class PDDLProblems:
    def __init__(self):
        base_problems_path = Path() / 'PDDL_problems'
        zeno_path = base_problems_path / 'NTCORE' / 'ZenoTravel-no-constraint'
        sar_path = base_problems_path / 'ENHSP' / 'handcraft' / 'sar'
        rover_path = base_problems_path / 'NTCORE' / 'Rover-Numeric'

        self.problems = {
            "zeno0":        (zeno_path / "domain.pddl",         zeno_path / "pfile0.pddl"),
            "zeno1":        (zeno_path / "domain.pddl",         zeno_path / "pfile1.pddl"),
            "zeno2":        (zeno_path / "domain.pddl",         zeno_path / "pfile2.pddl"),
            "zeno3":        (zeno_path / "domain.pddl",         zeno_path / "pfile3.pddl"),
            "zeno4":        (zeno_path / "domain.pddl",         zeno_path / "pfile4.pddl"),
            "zeno5":        (zeno_path / "domain.pddl",         zeno_path / "pfile5.pddl"),
            "zeno5_bis":    (zeno_path / "domain.pddl",         zeno_path / "pfile5_bis.pddl"),
            "zeno5_bis_n":  (zeno_path / "domain_with_n.pddl",  zeno_path / "pfile5_bis.pddl"),
            "zeno6":        (zeno_path / "domain.pddl",         zeno_path / "pfile6.pddl"),
            "zeno7":        (zeno_path / "domain.pddl",         zeno_path / "pfile7.pddl"),
            "zeno7_n":      (zeno_path / "domain_with_n.pddl",  zeno_path / "pfile7.pddl"),
            "zeno8":        (zeno_path / "domain.pddl",         zeno_path / "pfile8.pddl"),
            "zeno9":        (zeno_path / "domain.pddl",         zeno_path / "pfile9.pddl"),
            "zeno10":       (zeno_path / "domain.pddl",         zeno_path / "pfile10.pddl"),
            "zeno11":       (zeno_path / "domain.pddl",         zeno_path / "pfile11.pddl"),
            "zeno12":       (zeno_path / "domain.pddl",         zeno_path / "pfile12.pddl"),
            "zeno12_n":     (zeno_path / "domain_with_n.pddl",  zeno_path / "pfile12.pddl"),
            "zeno13":       (zeno_path / "domain.pddl",         zeno_path / "pfile13.pddl"),
            "zeno13_n":     (zeno_path / "domain_with_n.pddl",  zeno_path / "pfile13.pddl"),
            "zenoreal":     (zeno_path / "domain_with_n.pddl",  zeno_path / "zenoreal.pddl"),
            "zeno14":       (zeno_path / "domain.pddl",         zeno_path / "pfile14.pddl"),
            "zeno15":       (zeno_path / "domain.pddl",         zeno_path / "pfile15.pddl"),
            "zeno16":       (zeno_path / "domain.pddl",         zeno_path / "pfile16.pddl"),
            "zeno17":       (zeno_path / "domain.pddl",         zeno_path / "pfile17.pddl"),
            "zeno18":       (zeno_path / "domain.pddl",         zeno_path / "pfile18.pddl"),
            "zeno19":       (zeno_path / "domain.pddl",         zeno_path / "pfile19.pddl"),
            "zeno20":       (zeno_path / "domain.pddl",         zeno_path / "pfile20.pddl"),
            "zeno21":       (zeno_path / "domain.pddl",         zeno_path / "pfile21.pddl"),
            "zeno22":       (zeno_path / "domain.pddl",         zeno_path / "pfile22.pddl"),
            "zeno23":       (zeno_path / "domain.pddl",         zeno_path / "pfile23.pddl"),
            
            "sar1":         (sar_path / "domain.pddl",          sar_path / "pfile1.pddl"),
            
            "rover3":       (rover_path / "domain.pddl",        rover_path / "pfile3.pddl"),
            "rover8_n":     (rover_path / "domain_n.pddl",      rover_path / "pfile8.pddl"),
            "rover8_n_t":   (rover_path / "domain_n_t.pddl",    rover_path / "pfile8_t.pddl"),
            "rover13_n_t":  (rover_path / "domain_n_t.pddl",    rover_path / "pfile13_t.pddl"),
            "rover6_n_t":   (rover_path / "domain_n_t.pddl",    rover_path / "pfile6_t.pddl"),
            "rover4_n_t":   (rover_path / "domain_n_t.pddl",    rover_path / "pfile4_t.pddl"),
            "rover10_n_t":  (rover_path / "domain_n_t.pddl",    rover_path / "pfile10_t.pddl"),
        }

        # Check paths
        for k,(d,p) in self.problems.items():
            if not d.exists(): raise Exception(f"PDDLProblems Init: Path doesn't exist: " + str(d))
            if not p.exists(): raise Exception(f"PDDLProblems Init: Path doesn't exist: " + str(p))

        # Store list of problems as str
        self.known_problems_str = 'PROBLEM_NAME: [' + ', '.join(self.problems) + ']'

    def add_problem(self, problem_name, domain_path, problem_path):
        # Convert str to pathlib if needed
        if type(domain_path)==str:
            domain_path = Path(domain_path)
        if type(problem_path)==str:
            problem_path = Path(problem_path)
            
        # Check path validity
        if not domain_path.exists(): raise Exception(f"PDDLProblems add_problem: Path doesn't exist: " + str(domain_path))
        if not problem_path.exists(): raise Exception(f"PDDLProblems add_problem: Path doesn't exist: " + str(problem_path))

        # Add problem
        self.problems[problem_name] = (domain_path, problem_path)

    def exists(self, problem_name) -> bool:
        return problem_name in self.problems

    def get_paths(self, problem_name):
        d = str(self.problems[problem_name][0].absolute())
        p = str(self.problems[problem_name][1].absolute())
        return d, p

    def get_paths_object(self, problem_name):
        d = self.problems[problem_name][0]
        p = self.problems[problem_name][1]
        return d, p
    
    def get_known_problems(self):
        return self.known_problems_str
    
PROBLEMS = PDDLProblems()

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

COMPILED_DOMAIN_PATH = "tmp/pddl_files/compiled_dom.pddl"
COMPILED_PROBLEM_PATH = "tmp/pddl_files/compiled_prob.pddl"
UPDATED_PROBLEM_PATH = "tmp/pddl_files/updatedProblem.pddl"

class PlanFiles:
    ORIGINAL = 'original'
    COMPILED = 'compiled'
    PATH = 'path'

class PlanMode:
    OPTIMAL = 'opt-hmax'
    SATISFICING = 'sat-hmrph'
    ANYTIME = 'anytime'
    ANYTIMEAUTO = 'anytimeAuto'
    DEFAULT = 'def'
    CUSTOM = 'custom'

class NtcoreStrategy:
    NAIVE = 'naive'
    REGRESSION = 'regression'
    DELTA = 'delta'
    
    
def startWith(s1, s2):
    return s1[:len(s2)]==s2
    
SHELL_PRINTS = False
GUI_PROMPT = True

myprint = lambda x: None
def mprint(txt, end="\n", logonly=False):
    if SHELL_PRINTS:
        print(txt, end=end)
    if GUI_PROMPT:
        logger.info(txt)
        if not logonly:
            myprint(txt, end=end)
def setPrintFunction(print_function):
    global myprint
    myprint = print_function

myreplaceprint = lambda x: None
def mrprint(txt, end='\n'):
    if SHELL_PRINTS:
        print('\r' + txt, end)
    if GUI_PROMPT:
        myreplaceprint(txt, end=end)
def setReplacePrintFunction(replace_print_function):
    global myreplaceprint
    myreplaceprint = replace_print_function
    
myinput = lambda x: None
def minput(txt=""):
    if GUI_PROMPT:
        logger.info(txt)
        return myinput(txt=txt)
    elif SHELL_PRINTS:
        return input(txt)
def setInputFunction(input_function):
    global myinput
    myinput = input_function

mstartTimer = None
def setStartTimer(f):
    global mstartTimer
    mstartTimer = f
def startTimer():
    mstartTimer()

mstopTimer = None
def setStopTimer(f):
    global mstopTimer
    mstopTimer = f
def stopTimer():
    mstopTimer()

class ModuleFilter(logging.Filter):
    def __init__(self, allowed_modules):
        super().__init__()
        self.allowed = allowed_modules

    def filter(self, record):
        return record.name in self.allowed
    
def setupLogger():
    # log filename
    date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    filename = f'tmp/logs/log__{date}.log' 
    
    # Only log agentic_constraint, tools and defs modules
    allowed_modules = ["agentic_constraint", "tools", "defs"]
    handler = logging.FileHandler(filename, encoding='utf-8')
    handler.setLevel(logging.INFO)
    handler.addFilter(ModuleFilter(allowed_modules))

    # Remove other handlers if present
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)