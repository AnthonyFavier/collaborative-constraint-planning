import time
from collab_planning.defs import *
import os                                                                                                                                                                                                          
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
try:
    load_dotenv(find_dotenv())
except:
    load_dotenv(Path("my/path/.env"))
import anthropic
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
MAX_TOKEN=5000
TEMPERATURE=0.0
MODEL="claude-3-7-sonnet-20250219"
MAX_TRY_OVERLOAD = 3

g_message_history = []
def clear_message_history():
    global g_message_history
    g_message_history = []


def call_llm(systemMsg, messages):
    for i in range(MAX_TRY_OVERLOAD):
        try:
            message = client.messages.create( model=MODEL, max_tokens=MAX_TOKEN, temperature=TEMPERATURE, system=systemMsg, messages= messages)
            return message
        except Exception as err:
            if err.args[0].find("not resolve authentication method"):
                raise err
            if err.args[0].find("overloaded_error"):
                if i<MAX_TRY_OVERLOAD-1:
                    print("API Overloaded, trying again in 2 seconds...")
                    time.sleep(2)
                else:
                    raise err
                
systemMsg="Your role is to act exactly as a PDDL automated planner. You will be given planning problems to solve, described in a traditionnal PDDL domain + problem format. Then, you will output a plan, a sequence of actions, reaching the goal given and optimizing any given quality metric."
def solving(domain, problem):
    messages=[
            {"role": "user", "content": f"Solve the following problem given the domain and problem PDDL descriptions:\n{domain}\n{problem}"},
        ]
    
    # Call LLM
    message = call_llm(systemMsg, messages)
    
    return message.content[0].text


if __name__=="__main__":
    
    for i in range(16):
        
        print(f"zeno{i}")
        d, p = PROBLEMS.get_paths(f"zeno{i}")
        with open(d) as f:
            domain = f.read()
        with open(p) as f:
            problem = f.read()
        
        t_1 = time.time()
        r = solving(domain, problem)
        r = r + f"Planning time: {time.time()-t_1}"
        print(r)
        
        with open(f"bench_LLM_zeno{i}_{time.time()}.txt", 'w') as f:
            f.write(r)