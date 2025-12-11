import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from . import Globals as G

def startWith(s1, s2):
    return s1[:len(s2)]==s2

myprint = lambda x: None
def mprint(txt, end="\n", logonly=False):
    if G.SHELL_PRINTS:
        print(txt, end=end)
    if G.GUI_PROMPT:
        logger.info(txt)
        if not logonly:
            myprint(txt, end=end)
def setPrintFunction(print_function):
    global myprint
    myprint = print_function

myreplaceprint = lambda x: None
def mrprint(txt, end='\n'):
    if G.SHELL_PRINTS:
        print('\r' + txt, end)
    if G.GUI_PROMPT:
        myreplaceprint(txt, end=end)
def setReplacePrintFunction(replace_print_function):
    global myreplaceprint
    myreplaceprint = replace_print_function
    
myinput = lambda x: None
def minput(txt=""):
    if G.GUI_PROMPT:
        logger.info(txt)
        return myinput(txt=txt)
    elif G.SHELL_PRINTS:
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

