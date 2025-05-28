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
    
    def call(self, systemMsg, messages, max_token=None, temperature=None, thinking=False):
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
                        extra_headers={"anthropic-beta": "extended-cache-ttl-2025-04-11"}
                    )
                
                # Prints blocks
                for m in result.content:
                    if m.type=='thinking':
                        print(m.thinking)
                    elif m.type=='text':
                        print(m.text)
                        
                answer = result.content[-1].text
                print(answer)
                return answer
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
        return answer
clients = {'ANTHROPIC': ANTHROPICClient('claude-sonnet-4-20250514'), 'OPENAI': OPENAIClient('o4-mini-2025-04-16')}

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

# Initialize the conversation history
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
def setSystemMessage(domain, problem):
    global system_message
    system_message = [{
            "type": "text",
            "text": "You are a PDDL planning expert. Your role is to reason about a PDDL problem and translate between natural language and PDDL. Here is the PDDL domain and problem that you will work with:" + "\n" + "<file_contents>\n" + domain + "\n</file_contents>" + "\n" + "<file_contents>\n" + problem + "\n</file_contents>",
            "cache_control": {"type": "ephemeral", "ttl":"1h"}
        }]

# DECOMPOSE
def decompose(constraint):
    conversation_history.add_turn_user("Your role is to decompose a natural language constraint into lower-level constraints in order to later apply them to a given PDDL problem. You must reason about the input constraint, make it match a state-based Linear Temporal Logic form in natural language. That is, you may rephrase and decompose the initial constraint into as many constraints as necessary to fully capture the meaning of the initial constraint and where each decomposed constraint is a trajectory hard constraint for the plan referring to the predicates and fluents of the problem. Due to their state-based nature, the constraints cannot directly affect actions, so reason accordingly. The decomposed constraints should also be in natural language without any explicit PDDL language.")
    conversation_history.add_turn_assistant("Got it now share with me the constraints to decompose. I will format my answer in a clear and concise numbered list. There should be no subitems, only a list of the decomposed constraints without additional explanations or descriptions. I should also not use any PDDL code, e.g., no explicit referring to PDDL predicate names or actions.")
    conversation_history.add_turn_user(constraint)
    
    # Call 
    assistant_reply = clients["ANTHROPIC"].call(system_message, conversation_history.get_turns(), thinking=True)
    conversation_history.add_turn_assistant(assistant_reply)

    # Remove format 
    assistant_reply_without_formating = removeFormating(assistant_reply)
    return assistant_reply_without_formating
def redecompose(feedback):
    conversation_history.add_turn_user(feedback)
    
    # Call
    assistant_reply = clients["ANTHROPIC"].call(system_message, conversation_history.get_turns(), thinking=True)
    conversation_history.add_turn_assistant(assistant_reply)
    
    # Remove format 
    assistant_reply_without_formating = removeFormating(assistant_reply)
    return assistant_reply_without_formating

# ENCODE
def encodePrefs(constraint):
    conversation_history.add_turn_user("Your purpose is to the given translate natural language constraint into PDDL3.0 constraints to be used in a classical PDDL planner. Respond to the requested translations only with concise and accurate PDDL language. PDDL3.0 constraints are state-based and should only concern predicates and fluents, they cannot refer directly to actions.")
    conversation_history.add_turn_assistant("Got it now share with me the natural language constraint to translate into PDDL3.0.")
    conversation_history.add_turn_user(constraint)
    
    # Call
    assistant_reply = clients["ANTHROPIC"].call(system_message, conversation_history.get_turns(), thinking=True)
    conversation_history.add_turn_assistant(assistant_reply)
    
    return assistant_reply
def reencodePrefs(feedback):
    conversation_history.add_turn_user(feedback)
    
    assistant_reply = clients["ANTHROPIC"].call(system_message, conversation_history.get_turns(), thinking=True)
    conversation_history.add_turn_assistant(assistant_reply)
    
    return assistant_reply

# E2NL
def E2NL(constraint):
    conversation_history.add_turn_user("Your purpose is to translate PDDL3.0 constraints to natural language in order to give to a human a good sense of what the PDDL3.0 constraint means and is doing.")
    conversation_history.add_turn_assistant("Got it, now share with me the PDDL3.0 constraint to translate to natural language. I will make sure that the translation is intuitive, concisem and easy to undestand, without explicit PDDL elements.")
    conversation_history.add_turn_user(constraint)
    
    # Call LLM
    assistant_reply = clients["OPENAI"].call(system_message, conversation_history.get_turns(), thinking=True)
    conversation_history.add_turn_assistant(assistant_reply)
    
    return assistant_reply

# MAIN
if __name__=='__main__':
    pass