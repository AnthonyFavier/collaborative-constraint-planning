import logging
from datetime import datetime
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PROBLEMS = {
    "zeno0":        ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile0.pddl"),
    "zeno1":        ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile1.pddl"),
    "zeno2":        ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile2.pddl"),
    "zeno3":        ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile3.pddl"),
    "zeno4":        ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile4.pddl"),
    "zeno5":        ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile5.pddl"),
    "zeno5_bis":    ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile5_bis.pddl"),
    "zeno5_bis_n":  ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain_with_n.pddl",  "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile5_bis.pddl"),
    "zeno6":        ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile6.pddl"),
    "zeno7":        ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile7.pddl"),
    "zeno7_n":      ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain_with_n.pddl",  "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile7.pddl"),
    "zeno8":        ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile8.pddl"),
    "zeno9":        ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile9.pddl"),
    "zeno10":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile10.pddl"),
    "zeno11":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile11.pddl"),
    "zeno12":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile12.pddl"),
    "zeno12_n":     ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain_with_n.pddl",  "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile12.pddl"),
    "zeno13":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile13.pddl"),
    "zeno13_n":     ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain_with_n.pddl",  "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile13.pddl"),
    "zenoreal":     ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain_with_n.pddl",  "PDDL/zenoreal.pddl"),
    "zeno14":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile14.pddl"),
    "zeno15":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile15.pddl"),
    "zeno16":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile16.pddl"),
    "zeno17":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile17.pddl"),
    "zeno18":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile18.pddl"),
    "zeno19":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile19.pddl"),
    "zeno20":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile20.pddl"),
    "zeno21":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile21.pddl"),
    "zeno22":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile22.pddl"),
    "zeno23":       ("NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl",         "NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile23.pddl"),
    
    # "sar1":         ("ENHSP-Public/sar/handcraft/domain.pddl",                              "ENHSP-Public/handcraft/pfile1.pddl"),
    
    "rover3":       ("NumericTCORE/benchmark/Rover-Numeric/domain.pddl",                    "NumericTCORE/benchmark/Rover-Numeric/pfile3.pddl"),
    "rover8_n":     ("NumericTCORE/benchmark/Rover-Numeric/domain_n.pddl",                  "NumericTCORE/benchmark/Rover-Numeric/pfile8.pddl"),
    "rover8_n_t":   ("NumericTCORE/benchmark/Rover-Numeric/domain_n_t.pddl",                "NumericTCORE/benchmark/Rover-Numeric/pfile8_t.pddl"),
    "rover13_n_t":  ("NumericTCORE/benchmark/Rover-Numeric/domain_n_t.pddl",                "NumericTCORE/benchmark/Rover-Numeric/pfile13_t.pddl"),
    "rover6_n_t":  ("NumericTCORE/benchmark/Rover-Numeric/domain_n_t.pddl",                "NumericTCORE/benchmark/Rover-Numeric/pfile6_t.pddl"),
    "rover4_n_t":  ("NumericTCORE/benchmark/Rover-Numeric/domain_n_t.pddl",                "NumericTCORE/benchmark/Rover-Numeric/pfile4_t.pddl"),
    "rover10_n_t":  ("NumericTCORE/benchmark/Rover-Numeric/domain_n_t.pddl",                "NumericTCORE/benchmark/Rover-Numeric/pfile10_t.pddl"),
}
KNOWN_PROBLEMS_STR = 'PROBLEM_NAME: [' + ', '.join(PROBLEMS) + ']'

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

COMPILED_DOMAIN_PATH = "tmp/compiled_dom.pddl"
COMPILED_PROBLEM_PATH = "tmp/compiled_prob.pddl"
UPDATED_PROBLEM_PATH = "tmp/updatedProblem.pddl"

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
def mprint(txt, end="\n"):
    if SHELL_PRINTS:
        print(txt, end=end)
    if GUI_PROMPT:
        logger.info(txt)
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
    filename = f'logs/log__{date}.log' 
    
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