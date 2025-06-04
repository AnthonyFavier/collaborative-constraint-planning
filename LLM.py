import time
from defs import *
import os                                                                                                                                                                                                          
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
try:
    load_dotenv(find_dotenv())
except:
    load_dotenv(Path("my/path/.env"))

MAX_TRY_OVERLOAD = 3
   
# CLIENTS
import anthropic
class ANTHROPICClient:
    def __init__(self, model, max_token=16000, temperature=0.0):
        self.model = model
        self.max_token = max_token
        self.temperature = temperature
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def call(self, systemMsg, messages, max_token=None, temperature=None, thinking=False, stop_sequences=[]):
        if max_token==None:max_token=self.max_token
        if temperature==None: temperature = self.temperature
        thinking_param = {'type': 'enabled', 'budget_tokens':10000} if thinking else {'type': 'disabled'}
        if thinking: temperature = 1.0
            
        for i in range(MAX_TRY_OVERLOAD):
            try:
                result = self.client.messages.create(
                        model=self.model, 
                        max_tokens=max_token, 
                        temperature=temperature, 
                        system=systemMsg, 
                        messages=messages, 
                        thinking=thinking_param, 
                        stop_sequences=stop_sequences,
                        extra_headers={"anthropic-beta": "extended-cache-ttl-2025-04-11"}
                    )
                
                # blocks
                answers = []
                for m in result.content:
                    if m.type=='thinking':
                        print("[THINKING]\n" + m.thinking)
                        answers.append(m.thinking)
                    elif m.type=='text':
                        if result.stop_reason == 'stop_sequence':
                            m.text += result.stop_sequence
                        print("[TEXT]\n" + m.text)
                        answers.append(m.text)
                return answers
            except Exception as err:
                if err.args[0].find("not resolve authentication method"):
                    raise err
                if err.args[0].find("overloaded_error"):
                    if i<MAX_TRY_OVERLOAD-1:
                        mprint("API Overloaded, trying again in 2 seconds...")
                        time.sleep(2)
                    else:
                        raise err
from openai import OpenAI
class OPENAIClient:
    def __init__(self, model, max_token=10000, temperature=0.0):
        self.model = model
        self.max_token = max_token
        self.temperature = temperature
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def call(self, systemMsg, messages, max_token=None, temperature=None, thinking=False):
        if max_token==None:max_token=self.max_token
        if temperature==None: temperature = self.temperature
        reasoning = {'effort': 'medium'} if thinking else None
        # if thinking: temperature = 1.0
        
        # Convertions for OpenAI
        for m in messages:
            if m['content'][0]['type']=='text':
                if m['role']=='user':
                    m['content'][0]['type']='input_text'
                elif m['role']=='assistant':
                    m['content'][0]['type']='output_text'
                    
            if 'cache_control' in m['content'][0]:
                m['content'][0].pop('cache_control')
                
        if not isinstance(systemMsg, str):
            systemMsg = systemMsg[0]['text']
        
        result = self.client.responses.create(input=messages, model=self.model, instructions=systemMsg, max_output_tokens=self.max_token, reasoning=reasoning)
        answer = result.output_text
        return [answer]
clients = {'ANTHROPIC': ANTHROPICClient('claude-sonnet-4-20250514'), 'OPENAI': OPENAIClient('o4-mini-2025-04-16')}

# CONVERSATION HISTORY
class ConversationHistory:
    def __init__(self):
        # Initialize an empty list to store conversation turns
        self.turns = []

    def add_turn_assistant(self, content):
        # Add an assistant's turn to the conversation history
        self.turns.append({
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": content
                }
            ]
        })

    def add_turn_user(self, content):
        # Add a user's turn to the conversation history
        self.turns.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": content
                }
            ]
        })

    def get_turns(self):
        # Retrieve conversation turns with specific formatting
        result = []
        user_turns_processed = 0
        # Iterate through turns in reverse order
        for turn in reversed(self.turns):
            if turn["role"] == "user" and user_turns_processed < 1:
                # Add the last user turn with ephemeral cache control
                result.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": turn["content"][0]["text"],
                            "cache_control": {"type": "ephemeral"}
                        }
                    ]
                })
                user_turns_processed += 1
            else:
                # Add other turns as they are
                result.append(turn)
        # Return the turns in the original order
        return list(reversed(result))
    
    def reset(self):
        self.turns = []
conversation_history = ConversationHistory()

# HELPERS
def clear_message_history():
    conversation_history.reset()
def removeFormating(text):
    
    # Remove initial white spaces and empty lines
    newtext = ""
    for l in text.splitlines():
        if l=='':
            continue
        i = 0
        while i<len(l) and l[i]==' ':
            i+=1
        l = l[i:]
        newtext += l + '\n'
        
        
    # Get main items
    main_items = []
    for l in newtext.splitlines():
        try:
            int(l[0])
            main_items.append(l)
        except:
            continue
    
    symbols = [
        '#',
        '*',
        '=',
        '-',
    ]
    
    newtext = ""
    for l in main_items:
        for s in symbols:
            l = l.replace(s, '')
        i = 0
        while not l[i].isalpha():
            i+=1
        l = l[i:]
        newtext += l + '\n'
    newtext = newtext[:-1]
        
    return newtext

# SYSTEM MESSAGE 
system_message = None
g_domain = None
g_problem = None
def setSystemMessage(domain, problem):
    global system_message, g_domain, g_problem
    g_domain = domain
    g_problem = problem
    system_message = [{
            "type": "text",
            "text": "You are a PDDL planning expert and your role is to work with given PDDL problems and follow the user requests and instructions.",
            "cache_control": {"type": "ephemeral", "ttl":"1h"}
        }]

# INITIAL SUGGESTIONS
def suggestions():
    
    conversation_history.add_turn_user(f"""
<documents>
<pddl_domain>
{g_domain}
</pddl_domain>
<pddl_problem>
{g_problem}
</pddl_problem>
</documents> 

<instructions> 
- Analyze the key elements of the given problem.
- Identify trajectory constraints as promising strategies to solve the problem.
- The constraints should help and guide toward efficient solutions or alternatives. They can also prevent from searching toward inefficient solutions. For example, 'A costly ressource should never be used'.
- Format your answer such as a concise numbered list with no subitems. The list must be between the tags <suggestions> and </suggestions>.
</instructions>
"""[1:-1])
    
    # Call 
    assistant_replies = clients["ANTHROPIC"].call(system_message, conversation_history.get_turns(), thinking=True, stop_sequences=["</suggestions>"])
    for r in assistant_replies:
        conversation_history.add_turn_assistant(r)

    answer = assistant_replies[-1]
    return answer

# DECOMPOSE
def decompose(constraint):
    conversation_history.add_turn_user(f"""
<documents>
<pddl_domain>
{g_domain}
</pddl_domain>
<pddl_problem>
{g_problem}
</pddl_problem>
</documents> 

<information>
The user will give as input a constraint in natural language. This constraint must be used as a transjectory hard constraint for the solution plan of the given the PDDL problem. 
</information>

<instructions> 
- Refine the user constraint to make it applicable to the given PDDL problem.
- You can rephrase and decompose the initial constraint into several other contraints.
- You may ask clarifying question if you face a strong ambiguity in the user input.
- Constraints must be state-based and follow a Linear Temporal Logic. So constraints can't directly refer to actions.
- Avoid explicit PDDL language in your answer, the user can't understand PDDL.
- The set of all refined constraints must capture the meaning of the initial user constraint. 
- Format your answer as a clear and concise numbered list between the tags <constraints> and </constraints>. There should be no subitems, only a list of the refined constraints. Here is an example:
    <constraints>
    1. [natural_language_constraint_1]
    2. [natural_language_constraint_2]
    ...
    </constraints>
</instructions>

<user_input>
{constraint}
</user_input>
"""[1:-1])
    
    # conversation_history.add_turn_assistant("Here is the list of refined constraints:")
    
    # Call 
    assistant_replies = clients["ANTHROPIC"].call(system_message, conversation_history.get_turns(), thinking=True, stop_sequences=["</constraints>"])
    for r in assistant_replies:
        conversation_history.add_turn_assistant(r)

    # Remove format 
    assistant_reply_without_formating = removeFormating(assistant_replies[-1])
    return assistant_reply_without_formating
def redecompose(feedback):
    conversation_history.add_turn_user(feedback)
    
    # Call
    assistant_replies = clients["ANTHROPIC"].call(system_message, conversation_history.get_turns(), thinking=True, stop_sequences=["</constraints>"])
    for r in assistant_replies:
        conversation_history.add_turn_assistant(r)
    
    # Remove format 
    assistant_reply_without_formating = removeFormating(assistant_replies[-1])
    return assistant_reply_without_formating

# MODICIFICATION
def needModifications():
    
    conversation_history.add_turn_user("Based on your previous reasonning to refine the constraint, evaluate if modifying the PDDL problem would significantly help to better refine it. That is, is the current refinement correctly capturing the initial constraint meaning and would it be worth it to, for instance, add new fluents or parameters to better capture the initial constraint. Answer with a clear Yes or No. If Yes, then give me clear suggestions on what updates to make.")
    
    # Call
    assistant_replies = clients["ANTHROPIC"].call(system_message, conversation_history.get_turns(), thinking=True)
    for r in assistant_replies:
        conversation_history.add_turn_assistant(r)
    
    return assistant_replies[-1]

# ENCODE
def encodePrefs(constraint):
    
    
    conversation_history.add_turn_user(f"""
<documents>
<pddl_domain>
{g_domain}
</pddl_domain>
<pddl_problem>
{g_problem}
</pddl_problem>
</documents> 

<information>
The user will give as input a natural language constraint that must be translated into PDDL3.0. The translation will be used by a PDDL planner.
</information>

<instructions> 
- Translate the input constraint into correct PDDL3.0.
- The resulting PDDL3.0 constraint must capture the same meaning as the initial input constraint.
- Remember that PDDL3.0 constraints are state-based. They can only refer to existing precates and fluents, thus, not to actions.
- Format your answer such as there is no preambule and such that the PDDL translation is between the tags <pddl> and </pddl>.
</instructions>

<user_input>
{constraint}
</user_input>
"""[1:-1])
    
    # Call
    assistant_replies = clients["ANTHROPIC"].call(system_message, conversation_history.get_turns(), thinking=True, stop_sequences=["</pddl>"])
    for r in assistant_replies:
        conversation_history.add_turn_assistant(r)
    
    return assistant_replies[-1]
def reencodePrefs(feedback):
    conversation_history.add_turn_user(feedback)
    
    assistant_replies = clients["ANTHROPIC"].call(system_message, conversation_history.get_turns(), thinking=True)
    for r in assistant_replies:
        conversation_history.add_turn_assistant(r)
    
    return assistant_replies[-1]

# E2NL
def E2NL(constraint):
    
    
    conversation_history.add_turn_user(f"""
<documents>
<pddl_domain>
{g_domain}
</pddl_domain>
<pddl_problem>
{g_problem}
</pddl_problem>
</documents> 

<information>
The user will give as input PDDL3.0 constraints.
</information>

<instructions> 
- Translate the user input into natural language to give them a good sense of what the PDDL3.0 constraint means and is doing.
- Your answer should be concise and not exceed 4 sentences.
- Your translation should not contain any explicit PDDL element, the user can't understand PDDL.
- Format your answer such as your translation is between the tags <E2NL> and </E2NL>.
</instructions>

<user_input>
{constraint}
</user_input>
"""[1:-1])
    
    # Call LLM
    assistant_replies = clients["OPENAI"].call(system_message, conversation_history.get_turns(), thinking=True)
    for r in assistant_replies:
        conversation_history.add_turn_assistant(r)
    
    return assistant_replies[-1]

# MAIN
if __name__=='__main__':
    pass