#######################
#### LOAD API KEYS ####
#######################

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


####################
#### PDDL FILES ####
####################
import tools

BASE_PATH = 'PDDL/'
DOMAIN_PATH = BASE_PATH+'zeno_dom.pddl'
PROBLEM_PATH = BASE_PATH+'zeno13.pddl'
PLAN_PATH = BASE_PATH+'zeno13_plan.txt'

with open(DOMAIN_PATH, 'r') as f:
    g_domain = f.read()
with open(PROBLEM_PATH, 'r') as f:
    g_problem = f.read()
with open(PLAN_PATH, 'r') as f:
    g_plan = f.read()

# Try parsing the initial problem
try:
    parsed = tools.parse_pddl3(DOMAIN_PATH, PROBLEM_PATH)
except Exception as e:
    print("ERROR", e)
    raise Exception(f"Unable to parse the initial problem.")

# Check if no initial constraints
if parsed.problem.trajectory_constraints!=[]:
    raise Exception(f"There are already constraints in the initial problem.\n{parsed.problem.trajectory_constraints}")

# Set extracted fluent names (used during verification)
tools.set_fluent_names([f.name for f in parsed.problem.fluents])
typed_objects = {}
objects = []
for o in parsed.problem.all_objects:
    objects.append(o.name)
    if o.type.name in objects:
        typed_objects[o.type.name].append(o.name)
    else:
        typed_objects[o.type.name] = [o.name]
tools.set_all_objects(objects)
tools.set_typed_objects(typed_objects)


######################################
#### STRUCTURED OUTPUTS AND STATE ####
######################################

## TYPES
from typing import Annotated, List
from pydantic import BaseModel, Field
from typing_extensions import Literal

class UserType(BaseModel):
    user_type: Literal["general_question", "constraint", "risk_analysis"] = Field(
        description="Classify the type of user input, used in the routing process."
    )

class Decomposition(BaseModel):
    decomposition: List[str] = Field(
        description="List of decomposed constraints."
    )
    explanation: str = Field(
        description="Explanation of the current decomposition."
    )
    
class DecompositionValidation(BaseModel):
    pddl_constraints: bool = Field(
        False, description="True if some constraints include explicit PDDL parts."
    )
    pddl_constraints_feedback: str = Field(
        "", description="Feedback indicating what PDDL parts were found and should be removed."
    )
    ambiguous_constraints: bool = Field(
        False, description="True if some constraints in the decomposition are still ambiguous."
    )
    ambiguous_constraints_feedback: str = Field(
        "", description="Feedback indicating what ambiguities are left."
    )
    redundant_constraints: bool = Field(
        False, description="True if some constraints in the decomposition are redundant."
    )
    redundant_constraints_feedback: str = Field(
        "", description="Feedback indicating what redundancies there are."
    )
    conflicting_constraints: bool = Field(
        False, description="True if some constraints in the decomposition are conflicting with each other, i.e. if they are not complementary."
    )
    conflicting_constraints_feedback: str = Field(
        "", description="Feedback indicating what conflicts there are."
    )
    mismatching_user_intent: bool = Field(
        False, description="True if the overal decomposition does not properly capture the user intent, due for instance to incomplete constraints. "
    )
    mismatching_user_intent_feedback: str = Field(
        "", description="Feedback indicating what is mismatching with the user intent."
    )
    
class DecompositionUserValidation(BaseModel):
    decomp_user_ok: bool = Field(
        description="True if user is satisfied with the current decomposition after review."
    )
    decomp_user_feedback: str = Field(
        "", description="If not satisfied with the decomposition, stores the user feedback about what's wrong about the decomposition."
    )

class Encoding(BaseModel):
    encoding: str = Field(
        "", description="PDDL3.0 translation of a given natural language constraint."
    )
    
class E2NL(BaseModel):
    e2nl: str = Field(
        "", description="Natural language translation of a given PDDL3.0 constraint."
    )
    
class EncodingE2NL(BaseModel):
    constraint: str = Field(
        description="constraint to translate in PDDL3.0"
    )
    encoding: Encoding = Field(
        Encoding(), description="PDDL3.0 translation of the constraint"
    )
    e2nl: E2NL = Field(
        E2NL(), description="Back-translation of the PDDL3.0 to natural language"
    )
    
class EncodingValidation(BaseModel):
    encoding_ok: bool = Field(
        False, description="Result of check of encoding with verifier."
    )
    encoding_feedback: str = Field(
        "", description="Feedback of detected issues in encoding from verifier"
    )
    encoding_nb_retry: int = Field(
        0, description="Number of retries when encoding the constraint."
    )

class E2NLValidation(BaseModel):
    e2nl_ok: bool = Field(
        description="Result of automated check if e2nl matches the NL decomposed constraints."
    )
    e2nl_feedback: str = Field(
        "", description="Feedback of detected issues about e2nl."
    )
    
class E2NLUserValidation(BaseModel):
    e2nl_user_ok: bool = Field(
        description="True if user validates the current e2nl after review."
    )
    e2nl_user_feedback: str = Field(
        description="If not validated, stores the user feedback about what's wrong about the e2nl."
    )
    
## STATES
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
import operator
class DecompositionState(TypedDict):
    messages: Annotated[list, add_messages]
    user_input: str # User input
    user_type: UserType # Type of user input: question, constraint, risk
    refined_user_intent: str # Refined user intent, removing ambiguities from initial input
    decomposition: Decomposition # Decomposition of user input
    decomposition_validation: DecompositionValidation # Automated validation of decomposition
    decomposition_user_validation: DecompositionUserValidation # User validation of decomposition
    encodingsE2NL: Annotated[list[EncodingE2NL], operator.add] # List of EncodingE2NL, populated by encoding workers
    
class EncodingState(TypedDict):
    e_messages: Annotated[list, add_messages]
    
    # Input
    user_input_e: str # User input
    refined_user_intent_e: str # Refined user intent, removing ambiguities from initial input
    decomposition_e: Decomposition # Decomposition of user input
    
    encodingE2NL: EncodingE2NL # includes specific constraint from decomposition, PDDL3 encoding, E2NL
    
    # Output
    encoding_validation: EncodingValidation # Automated validation of encoding, with verifier
    e2nl_validation: E2NLValidation # Automated validation of back translation
    e2nl_user_validation: E2NLUserValidation # User validation of back translation
    encodingsE2NL: Annotated[list[EncodingE2NL], operator.add] # List of EncodingE2NL, populated by encoding workers, includes constraint, PDDL3 encoding, and E2NL


###############
#### TOOLS ####
###############

import requests
from langchain_tavily import TavilySearch
from langgraph.types import Send
from langchain_core.tools import tool
import json 

@tool
def ask_clarifying_question(question: str) -> str:
    """Ask the user the clarifying question given as input and returns the user answer."""
    return input(question+'\n> ')

search_tool = TavilySearch(max_results=2)

@tool
def basic_plan_analysis(plan: str) -> str:
    """Receives a plan and computes a few basic caracterics such as number of steps and each action occurence."""
    nb_step = len(plan.splitlines())
    nb_step_text = f"Number of steps = {nb_step}"
    
    actions = set()
    for l in plan.splitlines():
        a = l.split('(')[1].split(' ')[0].strip()
        actions = actions.union([a])
    actions = list(actions)
    actions.sort()
    actions_text = "Action ocurrences:\n"
    for a in actions:
        actions_text += f'- {a}: {plan.count(a)}\n'
    actions_text = actions_text[:-1]
        
    return nb_step_text + "\n" + actions_text
    
@tool
def count_number_step_in_plan(plan: str) -> int:
    """Count the number of steps or actions in a given plan."""
    return len(plan.splitlines())

@tool
def count_action_occurrence(plan: str, action:str) -> int:
    """Count the occurence of a specific action based on its exact name and parameters formatted as '<action_name> <param1> <param2>...'. If only '<action_name>' is provided, all occurrences will be counted, regarless of the different action parameters."""
    n = 0
    for l in plan.splitlines():
        if action in l:
            n+=1
    return n

BASE_URL = 'https://api.api-ninjas.com/v1/'
def buildURL(category, params):
    url = BASE_URL + category + '?'
    for param, value in params.items():
        url += f'{param}={value}&'
    return url[:-1]

@tool
def get_current_weather_city(city: str):
    """Get the accurate real time weather of a given city. The weather includes the following: temperature, humidity, wind speed, and wind direction."""
    
    # get city loc
    category = 'city'
    params = {'name': city, 'country': 'US'}
    api_url = buildURL(category, params)
    response = requests.get(api_url, headers={'X-Api-Key': 'CqS0SVW7lQvWu65I+k2ZbA==auC23H2B4w9ij0yq'})
    if response.status_code == requests.codes.ok:
        print("API City Info: "+response.text)
        response = json.loads(response.text)
        if not response:
            return "Unknown city name."
    else:
        print("Error:", response.status_code, response.text)
        
    # get weather at loc
    category = 'weather'
    params = {
        'lat': response[0]['latitude'],
        'lon': response[0]['longitude'],
    }
    api_url = buildURL(category, params)
    response = requests.get(api_url, headers={'X-Api-Key': 'CqS0SVW7lQvWu65I+k2ZbA==auC23H2B4w9ij0yq'})
    if response.status_code == requests.codes.ok:
        print("API loc weather: " + response.text)
        weather = json.loads(response.text)
        weather_text = f"""
Current weather at {city}:
- Temperature: {weather['temp']}°C
- Humidity: {weather['humidity']}%
- Wind speed: {weather['wind_speed']}m/s
- Wind direction: {weather['wind_degrees']}°
"""[1:-1]
    else:
        print("Error:", response.status_code, response.text)
        
    return weather_text


################
#### MODELS ####
################
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages.modifier import RemoveMessage
e2nl_llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14", temperature=0)
g_llm = ChatAnthropic(model="claude-3-5-haiku-latest", max_tokens=4000, temperature=0)
# llm = ChatAnthropic(model='claude-sonnet-4-20250514', max_tokens=4000, thinking={"type": "enabled", "budget_tokens": 2000})


###########################
#### ENCODING SUBGRAPH ####
###########################
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt, Command
PRINT_NODES = True

#NODE
def Encode(state: EncodingState):
    """Translate the given constraint into PDDL3.0"""

    if 'PRINT_NODES'in globals():
        print('Node: Encode')
    
    SYSTEM_PROMPT = (
        "You are a PDDL planning expert. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        
        "Your goal is to translate natural language constraints into PDDL3.0. "
        "Remember that PDDL3.0 constraints are state-based. They can only refer to existing predicates, fluents or objects; not to actions. "
        "Be sure to include temporal logic like operators in your translation. "
    )
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=g_domain, pddl_problem=g_problem))
    
    llm = g_llm.with_structured_output(Encoding)
    
    if state.get('e2nl_user_validation') and not state['e2nl_user_validation'].e2nl_user_ok:
        state['e_messages'] += [HumanMessage(content="The user is not satisfied with the generated PDDL3.0 translation, translate again considering the following user feedback: " + state["encoding_validation"].encoding_feedback)]
    
    # ENCODING NOT OK, FEEDBACK FROM VERIFIER
    elif state.get("encoding_validation") and not state['encoding_validation'].encoding_ok:
        state['e_messages'] += [HumanMessage(content="There is an issue, try to translate again considering the following feedback: " + state["encoding_validation"].encoding_feedback)]
  
    # FIRST ENCODING
    else:
        state['e_messages'] = [sys_msg]
        state['e_messages'] += [HumanMessage(content=state['encodingE2NL'].constraint)]
    
    msg = llm.invoke(state['e_messages'])
    
    encodingE2NL = state["encodingE2NL"]
    encodingE2NL.encoding = msg
    
    ai_msg = AIMessage(content=encodingE2NL.encoding.encoding)
    
    return {'e_messages': [ai_msg], 'encodingE2NL': encodingE2NL}

#NODE
def Verifier(state: EncodingState):
    if 'PRINT_NODES'in globals():
        print('Node: Verifier')
    
    encoding = state["encodingE2NL"].encoding.encoding
    updatedProblem = tools.updateProblem(g_problem, [encoding])
    result = tools.verifyEncoding(updatedProblem, g_domain, encoding)
    
    encodingOK = result=='OK'
    
    if state.get("encoding_validation"):
        encodingValidation = state['encoding_validation']
        encodingValidation.encoding_nb_retry += 1
        if encodingValidation.encoding_nb_retry > 5:
            print("WARNING: Exceeding 5 encoding attempts")
    else:
        encodingValidation = EncodingValidation()

    encodingValidation.encoding_ok = encodingOK
    encodingValidation.encoding_feedback = result

    return {"encoding_validation": encodingValidation}

#CondEdge
def RoutingVerifier(state: EncodingState):
    """Routes based on verifier feedback"""
    if state['encoding_validation'].encoding_ok:
        return "OK"
    else:
        return "Retry"
    
#NODE
def BackTranslation(state: EncodingState):
    if 'PRINT_NODES'in globals():
        print('Node: BackTranslation')
    
    SYSTEM_PROMPT = (
        "You are a PDDL planning expert. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        
        "Your goal is to translate PDDL3.0 constraints into natural language. "
        "Your translation should closely match the PDDL3.0 input, without additional deductions or reasoning. "
        "So, your answer should be concise with just a straight translation. "
    )
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=g_domain, pddl_problem=g_problem))
    
    
    llm = e2nl_llm.with_structured_output(E2NL)
    
    messages = [
        sys_msg,
        HumanMessage(content=state["encodingE2NL"].encoding.encoding),
    ]
        
    msg = llm.invoke(messages)

    encodingE2NL = state['encodingE2NL']
    encodingE2NL.e2nl = msg
    
    ai_msg = AIMessage(content="Back translation from PDDL3.0 to Natural Language:\n" + encodingE2NL.e2nl.e2nl)

    return {'e_messages': [ai_msg], "encodingE2NL": encodingE2NL}

#NODE
def UserReviewE2NL(state: EncodingState):
    if 'PRINT_NODES'in globals():
        print('Node: UserReviewE2NL')
  
    
    # Show Data: constraint and back-translation
    txt = 'Constraint: ' + state['encodingE2NL'].constraint + '\n\t⇓\nE2NL: ' + state['encodingE2NL'].e2nl.e2nl
    
    # Ask user for review
    user_review = input(txt+'\n\nAre you satisfied with the back translation? If not, provide any desired feedback for me to consider.\n> ')
    # user_review = interrupt(txt+'\n\nAre you satisfied with the back translation? If not, provide any desired feedback for me to consider.\n> ')
    
    # If trivial positive answer move skip LLM call
    if user_review.lower() in ['yes', 'y', '']:
        return {"e2nl_user_validation": E2NLUserValidation(e2nl_user_ok=True, e2nl_user_feedback="")}
    
    # Evaluate user input: ok or not (structued output)
    llm = g_llm.with_structured_output(E2NLUserValidation)
    
    SYSTEM_PROMPT = (
        "You are a PDDL planning expert. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        
        "The user provided a natural language constraint that has been translated into PDDL3.0. "
        "Since the user isn't familiar with PDDL3, a back-translation into natural language has been generated for human review. "
        "Your goal is to analyze the user answer that will be given to evaluate if they are satisfied with the decomposition. "
        "If not, you must extract their feedback about what's wrong. "
        "The user will usually be very clear if satified by answering: yes, y, ok, I'm satisfied. "
        "So any answer that is longer than the previous examples probably means non-satisfaction, describing the issue. "
        "The extracted feedback will be used to generate a new PDDL3.0 translation. "
    )
      
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=g_domain, pddl_problem=g_problem))
        
    messages = [
        sys_msg,
        HumanMessage(content=user_review),
    ]
        
    msg = llm.invoke(messages)
    return {"e2nl_user_validation": msg}

#CondEdge
def RoutingUserReviewBackTranslation(state: EncodingState):
    """Routes based on user review"""
    if state['e2nl_user_validation'].e2nl_user_ok:
        return "OK"
    else:
        return "Retry"
    
#NODE
def SaveEncoding(state: EncodingState):
    if 'PRINT_NODES'in globals():
        print('Node: SaveEncoding')
    
    return {'encodingsE2NL': [state["encodingE2NL"]]}
    
#### BUILD ####    
encoding_subgraph_builder = StateGraph(EncodingState)
# Add nodes
encoding_subgraph_builder.add_node("Encode", Encode)
encoding_subgraph_builder.add_node("Verifier", Verifier)
encoding_subgraph_builder.add_node("BackTranslation", BackTranslation)
encoding_subgraph_builder.add_node("UserReviewE2NL", UserReviewE2NL)
encoding_subgraph_builder.add_node("SaveEncoding", SaveEncoding)
# Add edges
encoding_subgraph_builder.add_edge(START, "Encode")
encoding_subgraph_builder.add_edge("Encode", "Verifier")
encoding_subgraph_builder.add_conditional_edges(
    "Verifier",
    RoutingVerifier,
    {
        "OK": "BackTranslation",
        "Retry": 'Encode'
    }
)
encoding_subgraph_builder.add_edge("BackTranslation", "UserReviewE2NL")
encoding_subgraph_builder.add_conditional_edges(
    "UserReviewE2NL",
    RoutingUserReviewBackTranslation,
    {
        "OK": "SaveEncoding",
        "Retry": 'Encode'
    }
)
encoding_subgraph_builder.add_edge("SaveEncoding", END)
# Compile
encoding_subgraph = encoding_subgraph_builder.compile(checkpointer=True)


####################
#### MAIN GRAPH ####
####################
from langgraph.checkpoint.memory import InMemorySaver

#NODE
def RefineUserIntent(state: DecompositionState):
    """Refines user input to remove ambiguity and properly capture the user intent. Can ask clarifying questions."""
    
    if 'PRINT_NODES'in globals():
        print("Node: RefineUserIntent")
        
    SYSTEM_PROMPT = (
        "You are a PDDL planning expert. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        "You will receive a user input constraint. "
        "The user input will eventually be translated into a PDDL3 hard trajectory constraint. "
        "Such representation is state-based and follows temporal logic based on the PDDL objects and fluents. "
        "However, before translating, the user input must be refined to remove potential ambiguities. "
        "Your goal is to do this refinement: identify ambiguities and rephase the user input to clearly capture their actual intent. "
        "If needed, you can use available tools to ask clarifying questions to the user.\n"
    )
    
    # structured_llm = llm.with_structured_output(UserIntent)
    llm = g_llm.bind_tools([ask_clarifying_question])
    messages = [SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=g_domain, pddl_problem=g_problem))] + state['messages']
    msg = llm.invoke(messages)
    return {"messages": [msg]}
    
#NODE
def SaveUserIntentClearMessages(state: DecompositionState):
    if 'PRINT_NODES'in globals():
        print("Node: SaveUserIntentClearMessages")
    messages_to_remove = state["messages"]
    remove_instructions = [RemoveMessage(id=m.id) for m in messages_to_remove]
    return {'refined_user_intent': state['messages'][-1].content, "messages": remove_instructions} # Return as part of a state update

#NODE
def Decompose(state: DecompositionState):
    """Decompose the user input into a proper set of constraints"""
    
    if 'PRINT_NODES'in globals():
        print("Node: Decompose")
    
    SYSTEM_PROMPT = (
        "You are a PDDL planning expert. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        "Your goal is to generate a clear, non ambiguous, list of constraints properly capturing the user intent. "
        "For trivial constraint the list may be composed of only one element. "
        "Each of the constraint in the list will be translated into PDDL3 so the affected objects and fluents from the PDDL problem must be clear. "
        "However, the user is not familiar with PDDL! So the constraint should only be in natural language, no PDDL! "
        "For this purpose, you can rephrase the user input, divide constraint into simpler sub-constraints. "
        "All constraints in the list must be complementary and not redundant. "
        "You must also generate a short explanation describing the motivations behind the proposed decomposition to help the user identify if it captures their intent. "
    )
    INPUT_PROMPT = (
        "## Initial user input\n"
        "{user_input}\n\n"
        "## Refined user intent\n"
        "{user_intent}"
    )
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=g_domain, pddl_problem=g_problem))
    
    llm = g_llm.with_structured_output(Decomposition)
    
    
    # REDECOMPOSE WITH USER FEEDBACK
    if state.get("decomposition_user_validation"):
        state['messages'] += [HumanMessage(content=f"Modify the list taking into account the feedback: {state['decomposition_user_validation'].decomp_user_feedback}")]
    
    # REDECOMPOSE WITH AUTOMATED FEEDBACK
    elif state.get("decomposition_validation"):
        feedbacks = [
            state["decomposition_validation"].pddl_constraints_feedback,
            state["decomposition_validation"].ambiguous_constraints_feedback,
            state["decomposition_validation"].redundant_constraints_feedback,
            state["decomposition_validation"].conflicting_constraints_feedback,
            state["decomposition_validation"].mismatching_user_intent_feedback,
        ]
        feedback = "\n".join(feedbacks)
        state['messages'] += [HumanMessage(content=f"Modify the decomposition list taking into account the feedback: {feedback}")]
    
    # FIRST DECOMPOSITION
    else:
        state['messages'] += [sys_msg]
        state['messages'] += [HumanMessage(content=INPUT_PROMPT.format(user_input=state['user_input'], user_intent=state['refined_user_intent']))]
        
    msg = llm.invoke(state['messages'])
    
    txt = ''
    txt+='Decomposition:\n'
    for d in msg.decomposition:
        txt+=f'- {d}\n'
    txt+='Explanation:\n'
    txt+=f'{msg.explanation}'
    ai_msg = AIMessage(content=txt)
    
    return {"messages": [ai_msg], "decomposition": msg}
    
#NODE
def VerifyDecomposition(state: DecompositionState):
    """Ask a series of question to evaluate if decomposition looks good"""
    
    if 'PRINT_NODES'in globals():
        print("Node: VerifyDecomposition")
    
    # MOCK no verification
    if 'PRINT_NODES'in globals():
        print('MOCKED')
    return {'decomposition_validation': DecompositionValidation()}
    
    SYSTEM_PROMPT = (
        "You are a PDDL planning expert. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        "The user provided a constraint that has been decomposed into a list of sub-constraints to properly capture their intent. "
        "Your goal is to answer a series of question regarding the provided decomposition. "
    )
    USER_PROMPT = (
        "Here is the user input and clarified intent:\n"
        "- User input: {user_input}\n"
        "- User clarified intent: {user_intent}\n"
        "Here is the current decomposition:\n"
        "{decomposition}\n"
        "Now answer the following questions:"
        "- Is there explicit PDDL language? The user is not familiar with it so it should only be in natural language.\n"
        "- Are the decomposed constraints still ambiguous? Is must be clear what PDDL objects or fluents it is referring to.\n"
        "- Are the decomposed constraints redundant? Each decomposed constraint should bring a new element, and not be a redundant rephrasing of another.\n"
        "- Are the decomposed constraint conflicting? They will be combined with AND operators and should be complementary."
        "- Is there a mismatch between the overal decomposition and the user intent? All combined decomposed constraints should properly capture the user intent, and not omit any part of it."
    )
    
    llm = g_llm.with_structured_output(DecompositionValidation)
    
    
    decomposition_str = ""
    for d in state['decomposition'].decomposition:
        decomposition_str += '- ' + d + '\n'
    decomposition_str += "Decomposition explanation:\n" + state["decomposition"].explanation
        
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=g_domain, pddl_problem=g_problem)),
        HumanMessage(content=USER_PROMPT.format(user_input=state['user_input'], user_intent=state['refined_user_intent'], decomposition=decomposition_str)),
    ]
    # FAKE CALL
    msg = llm.invoke(messages)
    # msg = DecompositionValidation()
    
    
    feedback = ''
    if msg.pddl_constraints:
        print('\tDetected: pddl_constraints')
        feedback += msg.pddl_constraints_feedback + '\n'
    if msg.ambiguous_constraints:
        print('\tDetected: ambiguous_constraints')
        feedback += msg.ambiguous_constraints_feedback + '\n'
    if msg.redundant_constraints:
        print('\tDetected: redundant_constraints')
        feedback += msg.redundant_constraints_feedback + '\n'
    if msg.conflicting_constraints:
        print('\tDetected: conflicting_constraints')
        feedback += msg.conflicting_constraints_feedback + '\n'
    if msg.mismatching_user_intent:
        print('\tDetected: mismatching_user_intent')
        feedback += msg.mismatching_user_intent_feedback + '\n'
    if feedback:
        print(feedback)
        
    return {'decomposition_validation': msg}

#CondEdge
def RoutingVerifyDecomposition(state: DecompositionState):
    """Evaluate if automated check of decomposition is ok"""
    decomp_ok = not(
        state['decomposition_validation'].pddl_constraints
        or state['decomposition_validation'].ambiguous_constraints
        or state['decomposition_validation'].redundant_constraints
        or state['decomposition_validation'].conflicting_constraints
        or state['decomposition_validation'].mismatching_user_intent
    )
    
    if decomp_ok:
        return "OK"
    else:
        return "Retry"
    
#NODE
def UserReviewDecomposition(state: DecompositionState):
    """Ask user for review of the decomposition"""
    # TODO: Find a way to add the clarifying question tool here. Currently conflicting with the structured output. 
    # Use two calls/nodes? 
    # A first one gathering user feedback and asking questions about it if needed?
    # A second one formatting the user feedback into the current structured output?
    
    if 'PRINT_NODES'in globals():
        print("Node: UserReviewDecomposition")
    
    # Format and Show decomposition
    decomposition_str = "Decomposition:\n"
    for d in state['decomposition'].decomposition:
        decomposition_str += '- ' + d + '\n'
    decomposition_str += 'Explanation:\n' + state['decomposition'].explanation
    
    # Ask user for review
    user_review = input(decomposition_str+'\n\nAre you satisfied with the current decomposition? If not, provide any desired feedback for me to consider.\n> ')
    # user_review = interrupt(decomposition_str+'\n\nAre you satisfied with the current decomposition? If not, provide any desired feedback for me to consider.\n> ')
    
    # If trivial positive answer move skip LLM call
    if user_review.lower() in ['yes', 'y', '']:
        return {'decomposition_user_validation': DecompositionUserValidation(decomp_user_ok=True, decomp_user_feedback='')}
    
    # Evaluate user input: ok or not (structued output)
    llm = g_llm.with_structured_output(DecompositionUserValidation)
    
    SYSTEM_PROMPT = (
        "You are a PDDL planning expert. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        
        "The user provided a constraint that has been decomposed into a list of sub-constraints to properly capture their intent. "
        "The decomposition has been shown to the user for review while asking if they were satisfied with it. "
        "Your goal is to analyze the user answer that you will be given to evaluate if they are satisfied with the decomposition. "
        "If not, you must extract their feedback about what's wrong. "
        "The user will usually be very clear if satified by answering: yes, y, ok, I'm satisfied. "
        "So any answer that is longer than the previous examples probably means non-satisfaction, describing the issue. "
        "The extracted feedback will be used to generate a new decomposition. "
    )
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=g_domain, pddl_problem=g_problem)),
        HumanMessage(content=user_review)
    ]
    msg = llm.invoke(messages)
    return {'decomposition_user_validation': msg}

#CondEdge
def RoutingUserReviewDecomposition(state: DecompositionState):
    """Routes based on user review"""
    if state['decomposition_user_validation'].decomp_user_ok:
        return "OK"
    else:
        return "Retry"

#NODE
def Orchestrator(state: DecompositionState):
    if 'PRINT_NODES'in globals():
        print("Node: Orchestrator")
    return {}
    
#CondEdge
def assign_encoding_workers(state: DecompositionState):
    workers = []
    for d in state['decomposition'].decomposition:
        worker_state = EncodingState(
            user_input_e = state['user_input'],
            refined_user_intent_e = state['refined_user_intent'],
            decomposition_e = state['decomposition'],
            encodingE2NL = EncodingE2NL(constraint=d),
        )
        workers.append(Send("EncodingSubgraph", worker_state))
    return workers

#NODE
def Merge(state: DecompositionState):
    if 'PRINT_NODES'in globals():
        print("Node: Merge")
    return {}

#### BUILD ####
agent_builder = StateGraph(DecompositionState)
# Add nodes
agent_builder.add_node("RefineUserIntent", RefineUserIntent)
agent_builder.add_node("ask_clarifying_question", ToolNode(tools=[ask_clarifying_question]))
agent_builder.add_node("SaveUserIntentClearMessages", SaveUserIntentClearMessages)
agent_builder.add_node("Decompose", Decompose)
agent_builder.add_node("VerifyDecomposition", VerifyDecomposition)
agent_builder.add_node("UserReviewDecomposition", UserReviewDecomposition)
agent_builder.add_node("Orchestrator", Orchestrator)
agent_builder.add_node("EncodingSubgraph", encoding_subgraph)
agent_builder.add_node("Merge", Merge)
# Add edges
agent_builder.add_edge(START, "RefineUserIntent")
agent_builder.add_conditional_edges(
    "RefineUserIntent",
    tools_condition,
    {
        "tools": "ask_clarifying_question",
        END: 'SaveUserIntentClearMessages'
    }
)
agent_builder.add_edge("ask_clarifying_question", "RefineUserIntent")
agent_builder.add_edge("SaveUserIntentClearMessages", "Decompose")
agent_builder.add_edge("Decompose", "VerifyDecomposition")
agent_builder.add_conditional_edges(
    "VerifyDecomposition",
    RoutingVerifyDecomposition,
    {
        "OK": 'UserReviewDecomposition',
        "Retry": 'Decompose'
    }
)
agent_builder.add_conditional_edges(
    "UserReviewDecomposition",
    RoutingUserReviewDecomposition,
    {
        "OK": "Orchestrator",
        "Retry": 'Decompose'
    }
)
agent_builder.add_conditional_edges(
    "Orchestrator",
    assign_encoding_workers,
    ['EncodingSubgraph']
)
agent_builder.add_edge("EncodingSubgraph", "Merge")
agent_builder.add_edge("Merge", END)
# Compile
graph = agent_builder.compile()


####################
#### DRAW GRAPH ####
####################
DRAW_GRAPH = True
if 'DRAW_GRAPH'in globals():
    with open('graph.png', 'wb') as png:
        png.write(graph.get_graph().draw_mermaid_png())
    with open('subgraph.png', 'wb') as png:
        png.write(encoding_subgraph.get_graph().draw_mermaid_png())


#############
#### RUN ####
#############
def TranslateUserInput(user_input):
    input_state = DecompositionState({"messages": [HumanMessage(content=user_input)], "user_input": user_input})
    final_state = graph.invoke(input_state)
    return final_state['encodingsE2NL']

if __name__=='__main__':
    # user_input = "Only plane1 should be used."
    user_input = "Person7 should always be located at boston and plane2 should always be located at washington."
    # user_input = "Person7 should never move."
    # user_input = "Person7 should always be located in their initial city."
    encodings = TranslateUserInput(user_input) # type: list[EncodingE2NL]
    
    print("\nUser input:\n", user_input)
    for e in encodings:
        print(f'• {e.constraint}')
        print(f'  → {e.encoding.encoding}')
        print(f'    → {e.e2nl.e2nl}')
        
