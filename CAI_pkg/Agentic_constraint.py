import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from . import Globals as G
from .Helpers import mprint, minput
from . import Helpers
from .ConstraintPlanning import PDDLHandler

#######################
#### LOAD API KEYS ####
#######################

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


####################
#### PDDL FILES ####
####################
import time

import threading
USER_INTERACTION_LOCK = threading.Lock()

###################
#### SETUP RAG ####
###################
from langchain_community.document_loaders import TextLoader, PyPDFLoader    
from langchain_community.document_loaders import UnstructuredMarkdownLoader
def DocLoader(filename):
        _,ext = filename.split('.')
        if ext in ['pdf']:
            doc = PyPDFLoader(filename).load()
        else:
            doc = TextLoader(filename).load()
        return doc

def set_up_rag():
    """Set up the RAG retriever and vectorstore."""
    
    ## LOAD ##
    print('Loading documents ... ', end='', flush=True)
    # mprint('Loading documents ... ')

    DOCUMENT_PATH = "RAG_documents/"
    files = [
        # Fake reports
        {
            "path": DOCUMENT_PATH+"fake_aircraft_plane1.md", 
            "description": "AIRCRAFT TECHNICAL & OPERATIONAL REPORT - Plane1",
        },
        {
            "path": DOCUMENT_PATH+"fake_aircraft_plane2.md", 
            "description": "AIRCRAFT TECHNICAL & OPERATIONAL REPORT - Plane2",
            # Suggests that plane2 can't operate at full speed
        },
        {
            "path": DOCUMENT_PATH+"fake_doc_airport_atlanta.md", 
            "description": "INTERNAL REPORT: ATLANTA INTERNATIONAL AIRPORT (ATL)",
        },
        {
            "path": DOCUMENT_PATH+"fake_doc_airport_newyork.md", 
            "description": "INTERNAL REPORT: JOHN F. KENNEDY INTERNATIONAL AIRPORT (JFK)",
        },
        {
            "path": DOCUMENT_PATH+"fake_urban_tree_health.md", 
            "description": "FIELD REPORT - Urban Tree Health Monitoring - Spring Assessment 2025",
        },
        {
            "path": DOCUMENT_PATH+"radioA.md",
            "description": "Transcript of radio transmissions.",
            # Suggests that plane3 shouldn't operate at full speed
        },
        {
            "path": DOCUMENT_PATH+"radioB.md",
            "description": "Transcript of radio transmissions.",
            # Suggests that Los Angeles airport can't refuel planes
        },
    ]

    # PDDL Files
    files += [
        {
            "path": G.DOMAIN_PATH,
            "description": "PDDL domain of the addressed problem. Describe the objects types, state description, and actions.",
        },
        {
            "path": G.PROBLEM_PATH,
            "description": "PDDL problem. Describe the object instances present in this specific problem, the initial state and goal state.",
        },
    ]

    docs = []
    for f in files:
        doc = DocLoader(f['path'])
        doc[0].metadata['description'] = f['description']
        docs.append(doc)
        
    docs_list = [item for sublist in docs for item in sublist]
    print('OK')

    ## SPLITTING
    print('Splitting documents ... ', end='', flush=True)
    # mprint('Splitting documents ... ')
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512, chunk_overlap=20
    )
    doc_splits = text_splitter.split_documents(docs_list)
    print('OK')

    ## INDEXING and RETREIVER
    print('Indexing documents ... ', end='', flush=True)
    # mprint('Indexing documents ... ', end='')
    from langchain_core.vectorstores import InMemoryVectorStore
    from langchain_openai import OpenAIEmbeddings
    vectorstore = InMemoryVectorStore.from_documents(
        documents=doc_splits, embedding=OpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever()
    print('OK')
    return retriever

######################################
#### STRUCTURED OUTPUTS AND STATE ####
######################################
from typing import Annotated, List
from pydantic import BaseModel, Field
from typing_extensions import Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
import operator

## TYPES ##
# Encoding
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
# Decomposition
class UserType(BaseModel):
    user_type: Literal["general_question", "translation", "risk_analysis"] = Field(
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
# Failure Detection
class RAGQuery(BaseModel):
    query: str = Field(
        '', description="RAG query to be used by a RAG retriver to find context data relevant to the query."
    )

## STATES ##
# Encoding
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
# Decomposition
class DecompositionState(TypedDict):
    messages: Annotated[list, add_messages]
    user_input: str # User input
    user_type: UserType # Type of user input: question, constraint, risk
    refined_user_intent: str # Refined user intent, removing ambiguities from initial input
    decomposition: Decomposition # Decomposition of user input
    decomposition_validation: DecompositionValidation # Automated validation of decomposition
    decomposition_user_validation: DecompositionUserValidation # User validation of decomposition
    encodingsE2NL: Annotated[list[EncodingE2NL], operator.add] # List of EncodingE2NL, populated by encoding workers
# Failure Detection
class FailureDetectionState(TypedDict):
    messages: Annotated[list, add_messages]
    rag_query: RAGQuery # RAG query to find relevant context in documents for failure detection
    rag_result: str # Resul of the RAG query
    answer: str # Answer for the failure detection request
    suggestions: str # Concrete suggestions to account the identifies potential risks
    first_loop: bool
    deeper_analysis: bool
    user_question: str
# Open Dialog
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
# Main
class MainState(TypedDict):
    messages: Annotated[list, add_messages]
    user_input: str # User input
    user_type: UserType # Type of user input: question, constraint, risk

    # outputs
    encodingsE2NL: Annotated[list[EncodingE2NL], operator.add] # List of EncodingE2NL, populated by encoding workers
    answer: str # Answer for the failure detection request
    suggestions: str # Concrete suggestions to account the identifies potential risks
    

###############
#### TOOLS ####
###############
import requests
#from langchain_tavily import TavilySearch
from langgraph.types import Send
from langchain_core.tools import tool
import json 

@tool
def ask_clarifying_question(question: str) -> str:
    """Ask the user the clarifying question given as input and returns the user answer."""
    print('    Tool call: ask_clarifying_question')
    logger.info('    Tool call: ask_clarifying_question')
    logger.info('inputs:\n-question: ' + str(question))
    mprint(chat_separator)
    q = minput("AI: "+question+'\n')
    if q.lower() == '':
        q='yes'
    mprint(chat_separator)
    mprint("User: " + q)
    logger.info('output: ' + q)
    return q

#search_tool = TavilySearch(max_results=2)

@tool
def basic_plan_analysis(plan: str) -> str:
    """Receives a plan and computes a few basic caracterics such as number of steps and each action occurence."""
    print('    Tool call: basic_plan_analysis')
    logger.info('    Tool call: basic_plan_analysis')
    logger.info('inputs:\n-plan: ' + str(plan))
    
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
    
    output = nb_step_text + "\n" + actions_text
    logger.info('output: ' + output)
        
    return output
    
@tool
def count_number_step_in_plan(plan: str) -> int:
    """Count the number of steps or actions in a given plan."""
    print('    Tool call: count_number_step_in_plan')
    logger.info('    Tool call: count_number_step_in_plan')
    logger.info('inputs:\n-plan: ' + str(plan))
    output =  len(plan.splitlines())
    logger.info('output: ' + output)
    return output

@tool
def count_action_occurrence(plan: str, action:str) -> int:
    """Count the occurence of a specific action based on its exact name and parameters formatted as '<action_name> <param1> <param2>...'. If only '<action_name>' is provided, all occurrences will be counted, regarless of the different action parameters."""
    print('    Tool call: count_action_occurrence')
    logger.info('    Tool call: count_action_occurrence')
    logger.info('inputs:\n-plan: ' + str(plan) + '\n-action: ' + str(action))
    n = 0
    for l in plan.splitlines():
        if action in l:
            n+=1
    logger.info('output: ' + n)
    return n

BASE_URL = 'https://api.api-ninjas.com/v1/'
def buildURL(category, params):
    url = BASE_URL + category + '?'
    for param, value in params.items():
        url += f'{param}={value}&'
    return url[:-1]

FAKE_WEATHER = False
@tool
def get_current_weather_city(city: str):
    """Get the accurate real time weather of a given city. The weather includes the following: temperature, humidity, wind speed, and wind direction."""
    print('    Tool call: get_current_weather_city - city: ' + city)
    logger.info('    Tool call: get_current_weather_city - city: ' + city)
    logger.info('inputs:\n-city: ' + str(city))
    
    # FAKE weather
    faked_weather_cities = ['Boston']
    if FAKE_WEATHER and city in faked_weather_cities:
        weather_text = fake_weather(city)
        logger.info('output: ' + weather_text)
        return weather_text
    
    # get city loc
    category = 'city'
    params = {'name': city, 'country': 'US'}
    api_url = buildURL(category, params)
    response = requests.get(api_url, headers={'X-Api-Key': 'CqS0SVW7lQvWu65I+k2ZbA==auC23H2B4w9ij0yq'})
    if response.status_code == requests.codes.ok:
        # mprint("API City Info: "+response.text)
        response = json.loads(response.text)
        if not response:
            return "Unknown city name."
    else:
        mprint("Error:", response.status_code, response.text)
        
    # get weather at loc
    category = 'weather'
    params = {
        'lat': response[0]['latitude'],
        'lon': response[0]['longitude'],
    }
    api_url = buildURL(category, params)
    response = requests.get(api_url, headers={'X-Api-Key': 'CqS0SVW7lQvWu65I+k2ZbA==auC23H2B4w9ij0yq'})
    if response.status_code == requests.codes.ok:
        # mprint("API loc weather: " + response.text)
        weather = json.loads(response.text)
        weather_text = f"""
Current weather at {city}:
- Temperature: {weather['temp']}°C
- Humidity: {weather['humidity']}%
- Wind speed: {weather['wind_speed']}m/s
- Wind direction: {weather['wind_degrees']}°
"""[1:-1]
    else:
        mprint("Error:", response.status_code, response.text)
        weather_text = "Failed to retrieve weather."
        
    logger.info('output: ' + weather_text)
    return weather_text

def fake_weather(city):
    logger.info('fake weather')
    weather = {}
    if True or city=='Boston':
        weather['temp'] = 35
        weather['humidity'] = 85
        weather['wind_speed'] = 65 # Hurrican wind speed
        weather['wind_degrees'] = 270
    
    weather_text = f"""
Current weather at {city}:
- Temperature: {weather['temp']}°C
- Humidity: {weather['humidity']}%
- Wind speed: {weather['wind_speed']}m/s
- Wind direction: {weather['wind_degrees']}°
"""[1:-1]

    return weather_text

def activateFakeWeather():
    global FAKE_WEATHER
    FAKE_WEATHER = True
def deactivateFakeWeather():
    global FAKE_WEATHER
    FAKE_WEATHER = False

# OWN RETRIEVAL TOOL WITH METADATA
@tool
def retrieve_with_metadata(query: str) -> str:
    """Retriever tool able to extract content from available documents that is relevant to the given query."""
    print('    Tool call: RAG - query: ' + query)
    logger.info('    Tool call: RAG')
    logger.info('inputs:\n-query: ' + str(query))
    
    results = retriever.invoke(query)
    formatted_chunks = []

    for i, doc in enumerate(results):
        formatted_chunks.append(
            f"<chunk_{i+1}>\n"
            f"Source: {doc.metadata.get('source', 'Unknown')}\n"
            f"Description: {doc.metadata.get('description', '')}\n"
            f"Content: {doc.page_content}\n"
            f"</chunk_{i+1}>\n"
        )
    output = "\n".join(formatted_chunks)
    logger.info('output: ' + output)
    return output

from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.shortcuts import *
from unified_planning.plans import ActionInstance, SequentialPlan
    
def simulatePlan(domain_path, problem_path, txt_plan, metric_name):
    txt = ''
    reader = PDDLReader()
    problem = reader.parse_problem(domain_path, problem_path)
    
    # convert plan
    txt_plan = txt_plan.split('\n')
    actions = []
    for l in txt_plan:
        if ''.join(l.split())=='':
            continue
        l = l[l.find("(")+1 : l.find(")") ]
        l = ' '.join(l.split('_'))
        l = l.split(' ')
        name = l[0]
        params = l[1:]
        actions.append( (name, *params) )
    up_plan = []
    for a in actions:
        name, *params = a
        up_action = problem.action(name)
        up_params = [problem.object(p.lower()) for p in params]
        up_plan.append(ActionInstance(up_action, up_params))
    up_plan = SequentialPlan(up_plan)
    
    # Simulate
    with SequentialSimulator(problem) as simulator:
        metric = FluentExp(problem.fluent(metric_name))
        state = simulator.get_initial_state()
        for ai in up_plan.actions:
            new_state = simulator.apply(state, ai)
            if new_state==None:
                break
            state = new_state
            
        if new_state==None:
            txt += 'Plan is invalid.\n'
            txt += f"Action {ai} isn't applicable.\n"
        elif not simulator.is_goal(state):
            txt += 'Plan is invalid.\n'
            txt += "The final state doesn't satisfy the goal.\n"
        else:
            txt += 'Plan is valid.\n'
        txt += f"Initial value {metric_name} = {simulator.get_initial_state().get_value(metric)}\n"
        txt += f"Final value {metric_name} = {state.get_value(metric)}\n"
        
    return txt
@tool
def simulatePlanTool(plan: str, metric: str) -> str:
    """Simulate the given plan execution, checking its validity and computing its cost given the name of the metric of measure."""
    print('    Tool call: simulatePlanTool')
    logger.info('    Tool call: simulatePlanTool')
    logger.info('inputs:\n-plan: ' + str(plan) + '\n-metric: ' + str(metric))
    feedback = simulatePlan(G.DOMAIN_PATH, G.PROBLEM_PATH, plan, metric)
    logger.info('output: ' + feedback)
    return feedback

################
#### MODELS ####
################
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages.modifier import RemoveMessage
e2nl_llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14", temperature=0)
light_llm = ChatAnthropic(model="claude-3-5-haiku-latest", max_tokens=4000, temperature=0)
reasonning_llm = ChatAnthropic(model='claude-sonnet-4-20250514', max_tokens=4000, thinking={"type": "enabled", "budget_tokens": 2000})
bigger_llm = ChatAnthropic(model='claude-sonnet-4-20250514', max_tokens=4000)

g_llm = bigger_llm

def extractAITextAnswer(msg):
    """
    LLM call can return various format of answer. The three main ones are: 
        - 'str' -> for direct answer
        - list[{text_message}, {'type':'tool_use'}] -> Tool use
        - list[{'type':'thinking'}, {text_message}] -> Thinkin/Reasoning activated
    This function account for these various formats and returns the text_message included.
    """
    
    text_answer = ""
    if isinstance(msg.content, str):
        text_answer = msg.content
    elif isinstance(msg.content, list):
        for m in msg.content:
            if m['type']=='text':
                text_answer = m['text']
                break
    else:
        raise Exception("extractAITextAnswer: Type of msg.content unsupported")

    return text_answer

import anthropic
import openai
def call(model, input):
    MAX_NB_TRY = 5
    RETRY_DELAY = 5
    n=0
    while n<MAX_NB_TRY:
        try:
            return model.invoke(input)
        except anthropic._exceptions.OverloadedError as err:
            mprint(f'Server down or overloaded, retrying in {RETRY_DELAY} seconds...')
            time.sleep(RETRY_DELAY)
        except openai._exceptions.InternalServerError as err:
            mprint(f'Server down or overloaded, retrying in {RETRY_DELAY} seconds...')
            time.sleep(RETRY_DELAY)
        except Exception as err:
            raise err
    raise err
        
##########################
#### GRAPH COMPONENTS ####
##########################
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
PRINT_NODES = True

####################################
#### FAILURE DETECTION SUBGRAPH ####
####################################
#NODE
def GenerateRAGQuery(state: FailureDetectionState):

    if 'PRINT_NODES'in globals():
        print('Node: GenerateRAGQuery')
        logger.info('Node: GenerateRAGQuery')
        
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        "<current_solution_plan>\n"
        "{pddl_plan}\n"
        "</current_solution_plan>\n"
    )
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL, pddl_plan=G.current_plan))
        
    RAG_QUERY_GENERATION_PROMPT = (
        "Generate a RAG query to look for potential risk of failure of the given PDDL plan. "
        "It should includes keywords such as 'restriction', 'failure', 'risk', 'danger', 'limitation'. "
        "The query should also include any relevant keyword regarding the current problem being solve. "
    )
    h_msg = HumanMessage(content= RAG_QUERY_GENERATION_PROMPT.format())
    
    state['messages'] += [sys_msg, h_msg]
    
    llm = light_llm.with_structured_output(RAGQuery)
    query = call(llm, [sys_msg] + state["messages"])
    
    return {'rag_query': query}

#NODE
def Retrieval(state: FailureDetectionState):

    if 'PRINT_NODES'in globals():
        print('Node: Retrieval')
        logger.info('Node: Retrieval')
        
        
    # For now directly call retriever tool
    # Future: bind tool to LLM and do an LLM call?
    # Can allow to adjust query? Ask clarifying question?
    
    result = retrieve_with_metadata.invoke({'query': state['rag_query'].query})
    
    txt = 'RAG Query:\n' + state["rag_query"].query + '\n\nRAG Result:\n' + result
    ai_msg = AIMessage(content=txt)
    
    return {'messages': [ai_msg], 'rag_result': result, 'first_loop': True}

#NODE
def AdditionalRetrieval(state: FailureDetectionState):

    if 'PRINT_NODES'in globals():
        print('Node: AdditionalRetrieval')
        logger.info('Node: AdditionalRetrieval')
        
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        "<current_solution_plan>\n"
        "{pddl_plan}\n"
        "</current_solution_plan>\n"
    )
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL, pddl_plan=G.current_plan))
    
    ADD_RETRIEVAL_PROMPT = (
        "You are conducting an analysis of risk of failure for the addressed problem. "
        # "Some potentially relevant information regarding possible failure has already been retrieved. "
        "Your goal is to retrieve additional context and information to better prepare the analysis of risk of failure of the plan. "
        "Use the avalaible tools to conduct such information retrieval relevant to 'restriction', 'failure', 'risk', 'danger', 'limitation'. "
        "The actual analysis of risk will be conducted in the following steps, focus on retrieving relevant context for it. "
        "Your answer should focus on risks that can be accounted with the current PDDL formalism. "
    )
    h_msg = HumanMessage(content=ADD_RETRIEVAL_PROMPT.format())
    
    if state['first_loop']:
        state['messages'] += [sys_msg, h_msg]
    
    llm = g_llm.bind_tools(failure_detection_tools)
    msg = call(llm, state['messages'])
    
    answer = extractAITextAnswer(msg)
    if answer:
        mprint(chat_separator)
        mprint("AI: " + answer) 
    
    return {'messages': [msg], 'first_loop': False}
  
#NODE
def GenerateAnswer(state: FailureDetectionState):
    if 'PRINT_NODES'in globals():
        print('Node: GenerateAnswer')
        logger.info('Node: GenerateAnswer')
        
    GENERATE_ANSWER_PROMPT = (
        "Use the previous pieces of retrieved context to identify possible risk of failure of the plan. "
        # "The context is splitted in different chunks, each encapsulated in <chunk_i> tags. "
        "If you don't know the answer, just say that you don't know. "
        "Focus on practical risks that may directly change or affect the given plan. "
        "Your answer should only be concise buttlet list, focused on the most relevant risks to the plan. "
    )
    state["messages"] += [HumanMessage(content= GENERATE_ANSWER_PROMPT.format())]
    
    msg = call(g_llm, state['messages'])
    answer = extractAITextAnswer(msg)
    if answer:
        mprint(chat_separator)
        mprint("AI: " + answer) 
    
    return {'messages': [msg], 'answer': answer}

#NODE
def MakeSuggestions(state: FailureDetectionState):
    if 'PRINT_NODES'in globals():
        print('Node: MakeSuggestions')
        logger.info('Node: MakeSuggestions')
        
    SUGGESTION_PROMPT = (
        "Based on your last answer about the risks of failure, reason and give me concrete temporal constraints applicable to the PDDL problem. "
        "Your answer should focus on risks that can be accounted with the current PDDL formalism. "
        "Don't consider the ones concerning elements not represented in the PDDL domain and problem. "
    )
    state['messages'] += [HumanMessage(content= SUGGESTION_PROMPT.format())]
    
    msg = call(g_llm, state['messages'])
    answer = extractAITextAnswer(msg)
    if answer:
        mprint(chat_separator)
        mprint("AI: " + answer) 
    
    return {'messages': [msg], 'suggestions': answer}

#### BUILD ####    
def build_failure_detection_subgraph():
    global failure_detection_tools
    failure_detection_tools = [retrieve_with_metadata, get_current_weather_city]
    
    failure_detection_subgraph_builder = StateGraph(FailureDetectionState)
    # Add nodes
    failure_detection_subgraph_builder.add_node("GenerateRAGQuery", GenerateRAGQuery)
    failure_detection_subgraph_builder.add_node("Retrieval", Retrieval)
    failure_detection_subgraph_builder.add_node("AdditionalRetrieval", AdditionalRetrieval)
    failure_detection_subgraph_builder.add_node("GenerateAnswer", GenerateAnswer)
    failure_detection_subgraph_builder.add_node("FailureDetectionTools", ToolNode(failure_detection_tools))
    failure_detection_subgraph_builder.add_node("MakeSuggestions", MakeSuggestions)
    # Add edge
    failure_detection_subgraph_builder.add_edge(START, "AdditionalRetrieval")
    # failure_detection_subgraph_builder.add_edge("GenerateRAGQuery", "AdditionalRetrieval")
    # failure_detection_subgraph_builder.add_edge("Retrieval", "AdditionalRetrieval")
    failure_detection_subgraph_builder.add_conditional_edges(
        "AdditionalRetrieval",
        tools_condition, 
        {
            "tools": "FailureDetectionTools",
            END: "GenerateAnswer",
        }
    )
    failure_detection_subgraph_builder.add_edge("FailureDetectionTools", "AdditionalRetrieval")
    failure_detection_subgraph_builder.add_edge("GenerateAnswer", "MakeSuggestions")
    failure_detection_subgraph_builder.add_edge("MakeSuggestions", END)
    # Compile
    failure_detection_subgraph = failure_detection_subgraph_builder.compile()
    return failure_detection_subgraph


##################
#### NEW RISK ####
##################

#NODE
def RiskRetrieval(state: FailureDetectionState):
    
    if 'PRINT_NODES'in globals():
        print('Node: RiskRetrieval')
        logger.info('Node: RiskRetrieval')
        
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        "<current_solution_plan>\n"
        "{pddl_plan}\n"
        "</current_solution_plan>\n"
    )
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL, pddl_plan=G.current_plan))
    
    ADD_RETRIEVAL_PROMPT = (
        "What are the most important constraint/risks to the current problem and plan based on external data? "
        "Focus on facts that directly imply modifications in the plan. "
    )
    h_msg = HumanMessage(content=ADD_RETRIEVAL_PROMPT.format())
    
    if state['first_loop']:
        state['messages'] += [sys_msg, h_msg]
    
    llm = g_llm.bind_tools(new_risk_tools)
    msg = call(llm, state['messages'])
    
    answer = extractAITextAnswer(msg)
    if answer:
        mprint(chat_separator)
        mprint("AI: " + answer) 
    
    return {'messages': [msg], 'first_loop': False}

#NODE
def RiskAskDeeper(state: FailureDetectionState):
    global USER_INTERACTION_LOCK
    
    if 'PRINT_NODES'in globals():
        print('Node: RiskAskDeeper')
        logger.info('Node: RiskAskDeeper')
    
    USER_INTERACTION_LOCK.acquire()
    
    mprint("\nDo you want to proceed with a deeper risk analysis? (Y/N)\n You can also ask me any question.")
    deeper_analysis = None
    user_question = None
    while True:
        user_answer = minput()
        if user_answer=='':
            mprint('User: no')
            deeper_analysis = False
            break
        else:
            mprint(f"User: {user_answer}")
            if user_answer.lower() in ['y', 'yes']:
                deeper_analysis = True
                break   
            elif user_answer.lower() in ['n', 'no']:
                deeper_analysis = False
                break
            else:
                deeper_analysis = False
                user_question = user_answer
                break
        # mprint("Sorry I didn't understand your answer. Proceed with a deeper analysis? (Y/N)\n")
    USER_INTERACTION_LOCK.release()
    
    return {'deeper_analysis': deeper_analysis, 'user_question':user_question, 'first_loop': True}

#CondEdge
def RiskCondEdgeDeeper(state: FailureDetectionState):
    if state['deeper_analysis']:
        return "CONTINUE"
    elif state['user_question']!=None:
        return "QUESTION"
    else:
        return END

#NODE
def RiskQuestion(state: FailureDetectionState):
    global USER_INTERACTION_LOCK
    
    if 'PRINT_NODES'in globals():
        print('Node: RiskQuestion')
        logger.info('Node: RiskQuestion')
    
    h_msg = HumanMessage(content=state['user_question'])
    if state['first_loop']:
        state['messages'] += [h_msg]
    
    llm = g_llm.bind_tools(new_risk_tools)
    msg = call(llm, state['messages'])
    
    answer = extractAITextAnswer(msg)
    if answer:
        mprint(chat_separator)
        mprint("AI: " + answer) 
    
    return {'messages': [msg], 'first_loop': False}
    
#NODE
def RiskDeeperAnalysis(state: FailureDetectionState):
    
    if 'PRINT_NODES'in globals():
        print('Node: RiskDeeperAnalysis')
        logger.info('Node: RiskDeeperAnalysis')
        
    ADD_RETRIEVAL_PROMPT = (
        "Conduct a deeper and wider risk analysis based on the external data available. "
    )
    h_msg = HumanMessage(content=ADD_RETRIEVAL_PROMPT.format())
    
    if state['first_loop']:
        state['messages'] += [h_msg]
    
    llm = g_llm.bind_tools(new_risk_tools)
    msg = call(llm, state['messages'])
    
    answer = extractAITextAnswer(msg)
    if answer:
        mprint(chat_separator)
        mprint("AI: " + answer) 
    
    return {'messages': [msg], 'first_loop': False}

#### BUILD ####  
def build_new_risk_subgraph():
    global new_risk_tools
    new_risk_tools = [retrieve_with_metadata, get_current_weather_city]
    
    new_risk_subgraph_builder = StateGraph(FailureDetectionState)
    # Add nodes
    new_risk_subgraph_builder.add_node("RiskRetrieval", RiskRetrieval)
    new_risk_subgraph_builder.add_node("RiskRetrievalTools", ToolNode(new_risk_tools))
    new_risk_subgraph_builder.add_node("RiskAskDeeper", RiskAskDeeper)
    new_risk_subgraph_builder.add_node("RiskAskDeeperTools", ToolNode(new_risk_tools))
    new_risk_subgraph_builder.add_node("RiskDeeperAnalysis", RiskDeeperAnalysis)
    new_risk_subgraph_builder.add_node("RiskQuestion", RiskQuestion)
    new_risk_subgraph_builder.add_node("RiskQuestionTools", ToolNode(new_risk_tools))
    # Add edges
    new_risk_subgraph_builder.add_edge(START, "RiskRetrieval")
    new_risk_subgraph_builder.add_conditional_edges(
        "RiskRetrieval",
        tools_condition,
        {
            "tools": "RiskRetrievalTools",
            END: "RiskAskDeeper",
        }
    )
    new_risk_subgraph_builder.add_edge("RiskRetrievalTools", "RiskRetrieval")
    new_risk_subgraph_builder.add_conditional_edges(
        "RiskAskDeeper",
        RiskCondEdgeDeeper,
        {
            "CONTINUE": "RiskDeeperAnalysis",
            "QUESTION": "RiskQuestion",
            END: END,
        }
    )
    new_risk_subgraph_builder.add_conditional_edges(
        "RiskDeeperAnalysis",
        tools_condition,
        {
            "tools": "RiskAskDeeperTools",
            END: "RiskAskDeeper",
        }
    )
    new_risk_subgraph_builder.add_edge("RiskAskDeeperTools", "RiskDeeperAnalysis")
    new_risk_subgraph_builder.add_conditional_edges(
        "RiskQuestion",
        tools_condition,
        {
            "tools": "RiskQuestionTools",
            END: "RiskAskDeeper",
        }
    )
    new_risk_subgraph_builder.add_edge("RiskQuestionTools", "RiskQuestion")
    # Compile
    new_risk_subgraph = new_risk_subgraph_builder.compile()
    return new_risk_subgraph
    

###########################
#### ENCODING SUBGRAPH ####
###########################
#NODE
def Encode(state: EncodingState):
    """Translate the given constraint into PDDL3.0"""

    if 'PRINT_NODES'in globals():
        print('Node: Encode')
        logger.info('Node: Encode')
    
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        
        "Your goal is to translate natural language constraints into PDDL3.0. "
        "Remember that PDDL3.0 constraints are state-based. They can only refer to existing predicates, fluents or objects; not to actions. "
        "Your PDDL3.0 answer must be given between the tags <pddl> and </pddl>. "
    )
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL))
    
    
    if state.get('e2nl_user_validation') and not state['e2nl_user_validation'].e2nl_user_ok:
        state['e_messages'] += [HumanMessage(content="The user is not satisfied with the generated PDDL3.0 translation, translate again considering the following user feedback: " + state["encoding_validation"].encoding_feedback)]
    
    # ENCODING NOT OK, FEEDBACK FROM VERIFIER
    elif state.get("encoding_validation") and not state['encoding_validation'].encoding_ok:
        state['e_messages'] += [HumanMessage(content="There is an issue, try to translate again considering the following feedback: " + state["encoding_validation"].encoding_feedback)]
  
    # FIRST ENCODING
    else:
        state['e_messages'] = [sys_msg]
        state['e_messages'] += [HumanMessage(content=state['encodingE2NL'].constraint)]
    
    # llm = reasonning_llm.with_structured_output(Encoding)
    llm = reasonning_llm
    msg = call(llm, state['e_messages'])
    answer = extractAITextAnswer(msg)
    try:
        encoding = Helpers.extractTag('pddl', answer)
        encoding = PDDLHandler.verifier.initialEncodingFixes(encoding)
    except Exception as err:
        encoding = err.args[0]
    
    encodingE2NL = state["encodingE2NL"]
    encodingE2NL.encoding = Encoding(encoding=encoding)
    
    ai_msg = AIMessage(content=encodingE2NL.encoding.encoding)
    
    return {'e_messages': [ai_msg], 'encodingE2NL': encodingE2NL}

#NODE
def Verifier(state: EncodingState):
    if 'PRINT_NODES'in globals():
        print('Node: Verifier')
        logger.info('Node: Verifier')
    
    encoding = state["encodingE2NL"].encoding.encoding
    result = PDDLHandler.verifier.checkEncoding(encoding)
    
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
        logger.info('Node: BackTranslation')
    
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
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
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL))
    
    
    llm = e2nl_llm.with_structured_output(E2NL)
    
    messages = [
        sys_msg,
        HumanMessage(content=state["encodingE2NL"].encoding.encoding),
    ]
        
    msg = call(llm, messages)

    encodingE2NL = state['encodingE2NL']
    encodingE2NL.e2nl = msg
    
    ai_msg = AIMessage(content="Back translation from PDDL3.0 to Natural Language:\n" + encodingE2NL.e2nl.e2nl)

    return {'e_messages': [ai_msg], "encodingE2NL": encodingE2NL}

#NODE
REVIEW_E2NL = True
def UserReviewE2NL(state: EncodingState):
    global USER_INTERACTION_LOCK
    if 'PRINT_NODES'in globals():
        print('Node: UserReviewE2NL')
        logger.info('Node: UserReviewE2NL')
  
    
    # Show Data: constraint and back-translation
    txt = '\nConstraint: ' + state['encodingE2NL'].constraint + '\n\t⇓\nE2NL: ' + state['encodingE2NL'].e2nl.e2nl
    
    # Ask user for review
    USER_INTERACTION_LOCK.acquire()
    user_review = ''
    if REVIEW_E2NL:
        user_review = minput(txt+'\n\nAre you satisfied with the back translation? If not, provide any desired feedback for me to consider.\n')
        if user_review.lower()=='':
            mprint("User: yes")
        else:
            mprint("User: " + user_review)
    USER_INTERACTION_LOCK.release()
    # user_review = interrupt(txt+'\n\nAre you satisfied with the back translation? If not, provide any desired feedback for me to consider.\n> ')
    
    # If trivial positive answer move skip LLM call
    if user_review.lower() in ['yes', 'y', '']:
        return {"e2nl_user_validation": E2NLUserValidation(e2nl_user_ok=True, e2nl_user_feedback="")}
    
    # Evaluate user input: ok or not (structued output)
    llm = light_llm.with_structured_output(E2NLUserValidation)
    
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
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
      
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL))
        
    messages = [
        sys_msg,
        HumanMessage(content=user_review),
    ]
        
    msg = call(llm, messages)
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
        logger.info('Node: SaveEncoding')
    
    return {'encodingsE2NL': [state["encodingE2NL"]]}
    
#### BUILD ####  
def build_encoding_subgraph():  
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
    encoding_subgraph = encoding_subgraph_builder.compile()
    return encoding_subgraph


##############################
#### TRANSLATION SUBGRAPH ####
##############################
#NODE
def RefineUserIntent(state: DecompositionState):
    """Refines user input to remove ambiguity and properly capture the user intent. Can ask clarifying questions."""
    
    if 'PRINT_NODES'in globals():
        print("Node: RefineUserIntent")
        logger.info("Node: RefineUserIntent")
        
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
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
    messages = [SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL))] + state['messages']
    msg = call(llm, messages)
    return {"messages": [msg]}
    
#NODE
def SaveUserIntentClearMessages(state: DecompositionState):
    if 'PRINT_NODES'in globals():
        print("Node: SaveUserIntentClearMessages")
        logger.info("Node: SaveUserIntentClearMessages")
        
    refined_user_intent = state['messages'][-1].content
    
    mprint(chat_separator)
    mprint('AI: Refined user intent Below\n')
    mprint(refined_user_intent)
    
    messages_to_remove = state["messages"]
    remove_instructions = [RemoveMessage(id=m.id) for m in messages_to_remove]
    return {'refined_user_intent': refined_user_intent, "messages": remove_instructions} # Return as part of a state update

#NODE
def Decompose(state: DecompositionState):
    """Decompose the user input into a proper set of constraints"""
    
    mprint(chat_separator)
    mprint("Decomposing ... \n")
    
    if 'PRINT_NODES'in globals():
        print("Node: Decompose")
        logger.info("Node: Decompose")
    
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
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
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL))
    
    
    
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
        
    llm = g_llm.with_structured_output(Decomposition)
    msg = call(llm, state['messages'])
    
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
        logger.info("Node: VerifyDecomposition")
    
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
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
    
    llm = light_llm.with_structured_output(DecompositionValidation)
    
    
    decomposition_str = ""
    for d in state['decomposition'].decomposition:
        decomposition_str += '- ' + d + '\n'
    decomposition_str += "Decomposition explanation:\n" + state["decomposition"].explanation
        
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL)),
        HumanMessage(content=USER_PROMPT.format(user_input=state['user_input'], user_intent=state['refined_user_intent'], decomposition=decomposition_str)),
    ]
    msg = call(llm, messages)
    
    feedback = ''
    if msg.pddl_constraints:
        mprint('\tDetected: pddl_constraints')
        feedback += msg.pddl_constraints_feedback + '\n'
    if msg.ambiguous_constraints:
        mprint('\tDetected: ambiguous_constraints')
        feedback += msg.ambiguous_constraints_feedback + '\n'
    if msg.redundant_constraints:
        mprint('\tDetected: redundant_constraints')
        feedback += msg.redundant_constraints_feedback + '\n'
    if msg.conflicting_constraints:
        mprint('\tDetected: conflicting_constraints')
        feedback += msg.conflicting_constraints_feedback + '\n'
    if msg.mismatching_user_intent:
        mprint('\tDetected: mismatching_user_intent')
        feedback += msg.mismatching_user_intent_feedback + '\n'
    if feedback:
        mprint(feedback)
        
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
    global USER_INTERACTION_LOCK
    
    # TODO: Find a way to add the clarifying question tool here. Currently conflicting with the structured output. 
    # Use two calls/nodes? 
    # A first one gathering user feedback and asking questions about it if needed?
    # A second one formatting the user feedback into the current structured output?
    
    if 'PRINT_NODES'in globals():
        print("Node: UserReviewDecomposition")
        logger.info("Node: UserReviewDecomposition")
    
    # Format and Show decomposition
    decomposition_str = "\nDecomposition:\n"
    for d in state['decomposition'].decomposition:
        decomposition_str += '- ' + d + '\n'
    
    # Ask user for review
    USER_INTERACTION_LOCK.acquire()
    user_review = minput(decomposition_str+"\n\nAre you satisfied with the decomposition? If not, provide any desired feedback or type 'explain'.\n")
    if user_review.lower()=='':
        mprint(f"User: yes")
    else:
        mprint(f"User: {user_review}")
    
    if user_review.lower() == 'explain':
        # mprint('\nExplanation of decomposition:\n' + state['decomposition'].explanation)
        mprint('\n' + state['decomposition'].explanation)
        user_review = minput("\nAre you satisfied with the decomposition? If not, provide any desired feedback.\n")
        if user_review.lower()=='':
            mprint(f"User: yes")
        else:
            mprint(f"User: {user_review}")
        
    USER_INTERACTION_LOCK.release()
    # user_review = interrupt(decomposition_str+'\n\nAre you satisfied with the current decomposition? If not, provide any desired feedback for me to consider.\n> ')
    
    # If trivial positive answer move skip LLM call
    if user_review.lower() in ['yes', 'y', '']:
        return {'decomposition_user_validation': DecompositionUserValidation(decomp_user_ok=True, decomp_user_feedback='')}
    
    # Evaluate user input: ok or not (structued output)
    llm = light_llm.with_structured_output(DecompositionUserValidation)
    
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
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
        SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL)),
        HumanMessage(content=user_review)
    ]
    msg = call(llm, messages)
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
        logger.info("Node: Orchestrator")
    mprint(chat_separator)
    mprint("Encoding ... \n")
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
        logger.info("Node: Merge")
    return {}

#### BUILD ####
def build_translation_subgraph():
    encoding_subgraph = build_encoding_subgraph()

    translation_subgraph_builder = StateGraph(DecompositionState)
    # Add nodes
    translation_subgraph_builder.add_node("RefineUserIntent", RefineUserIntent)
    translation_subgraph_builder.add_node("ask_clarifying_question", ToolNode(tools=[ask_clarifying_question]))
    translation_subgraph_builder.add_node("SaveUserIntentClearMessages", SaveUserIntentClearMessages)
    translation_subgraph_builder.add_node("Decompose", Decompose)
    translation_subgraph_builder.add_node("VerifyDecomposition", VerifyDecomposition)
    translation_subgraph_builder.add_node("UserReviewDecomposition", UserReviewDecomposition)
    translation_subgraph_builder.add_node("Orchestrator", Orchestrator)
    translation_subgraph_builder.add_node("EncodingSubgraph", encoding_subgraph)
    translation_subgraph_builder.add_node("Merge", Merge)
    # Add edges
    translation_subgraph_builder.add_edge(START, "RefineUserIntent")
    translation_subgraph_builder.add_conditional_edges(
        "RefineUserIntent",
        tools_condition,
        {
            "tools": "ask_clarifying_question",
            END: 'SaveUserIntentClearMessages'
        }
    )
    translation_subgraph_builder.add_edge("ask_clarifying_question", "RefineUserIntent")
    translation_subgraph_builder.add_edge("SaveUserIntentClearMessages", "Decompose")
    ## Without verification node
    translation_subgraph_builder.add_edge("Decompose", "UserReviewDecomposition")
    ## With verification node
    # translation_subgraph_builder.add_edge("Decompose", "VerifyDecomposition")
    # translation_subgraph_builder.add_conditional_edges(
    #     "VerifyDecomposition",
    #     RoutingVerifyDecomposition,
    #     {
    #         "OK": 'UserReviewDecomposition',
    #         "Retry": 'Decompose'
    #     }
    # )
    ## End
    translation_subgraph_builder.add_conditional_edges(
        "UserReviewDecomposition",
        RoutingUserReviewDecomposition,
        {
            "OK": "Orchestrator",
            "Retry": 'Decompose'
        }
    )
    translation_subgraph_builder.add_conditional_edges(
        "Orchestrator",
        assign_encoding_workers,
        ['EncodingSubgraph']
    )
    translation_subgraph_builder.add_edge("EncodingSubgraph", "Merge")
    translation_subgraph_builder.add_edge("Merge", END)
    # Compile
    translation_subgraph = translation_subgraph_builder.compile()
    return translation_subgraph


##############################
#### OPEN DIALOG SUBGRAPH ####
##############################
#NODE
chat_separator = "-----------------------------"
def ChatGetUserInput(state: ChatState):
    if 'PRINT_NODES'in globals():
        print("Node: ChatGetUserInput")
        logger.info("Node: ChatGetUserInput")
        
    mprint("\n[ Ask anything or type 'exit' ]\n" + chat_separator + '\n')
    mprint("User: ", end='')
    question = minput()
    mprint(question)
    return {"messages": [HumanMessage(content=question)]}

#CondEdge
def ChatCondEnd(state: ChatState):
    if state['messages'][-1].content.lower() in ['exit', 'q']:
        return END
    return 'OK'

#NODE
def ChatAnswer(state: ChatState):
    if 'PRINT_NODES'in globals():
        print("Node: Chat")
        logger.info("Node: Chat")
        
    SYSTEM_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        "<current_solution_plan>\n"
        "{pddl_plan}\n"
        "</current_solution_plan>\n"
        
        "The user will ask you various questions related to the problem. "
        "Your goal is to answer the user's questions with helpful responses. "
        "Some relevant information may be present in external documents.  "
    )
    
    llm = g_llm.bind_tools(chat_tools)
    messages = [SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL, pddl_plan=G.current_plan))] + state['messages']
    
    mprint('\n' + chat_separator + '\n')
    mprint("AI: ", end='')
    msg = call(llm, messages)
    answer = extractAITextAnswer(msg)
    if answer:
        mprint(answer)

    return {"messages": [msg]}

#### BUILD ####
def build_chat_subgraph():
    global chat_tools
    chat_tools = [
        ask_clarifying_question, 
        retrieve_with_metadata, 
        get_current_weather_city,
        basic_plan_analysis,
        count_number_step_in_plan,
        count_action_occurrence,
        simulatePlanTool,
    ]
    
    chat_subgraph_builder = StateGraph(ChatState)
    
    # Add nodes
    chat_subgraph_builder.add_node("ChatGetUserInput", ChatGetUserInput)
    chat_subgraph_builder.add_node("ChatAnswer", ChatAnswer)
    chat_subgraph_builder.add_node('ChatTools', ToolNode(chat_tools))
    # Add edges
    chat_subgraph_builder.add_edge(START, "ChatGetUserInput")
    chat_subgraph_builder.add_conditional_edges(
        "ChatGetUserInput", 
        ChatCondEnd,
        {
            END: END,
            'OK': "ChatAnswer",
        }
    )
    chat_subgraph_builder.add_conditional_edges(
        "ChatAnswer", 
        tools_condition,
        {
            'tools': 'ChatTools',
            END: 'ChatGetUserInput',
        }
    )
    chat_subgraph_builder.add_edge('ChatTools', 'ChatAnswer')
    # Compile
    chat_subgraph = chat_subgraph_builder.compile()
    return chat_subgraph

####################
#### MAIN GRAPH ####
####################
#NODE
def TopNode(state: MainState):
    return {}

#CondEdge
def RoutingMain(state: MainState):
    return state['user_type'].user_type

#### BUILD ####
def build_main_graph():
    translation_subgraph = build_translation_subgraph()
    failure_detection_subgraph = build_failure_detection_subgraph()
    
    main_graph_builder = StateGraph(MainState)
    # Add nodes
    main_graph_builder.add_node("TopNode", TopNode)
    main_graph_builder.add_node("Translation", translation_subgraph)
    main_graph_builder.add_node("FailureDetection", failure_detection_subgraph)
    # Add edges
    main_graph_builder.add_edge(START, "TopNode")
    main_graph_builder.add_conditional_edges(
        "TopNode",
        RoutingMain,
        {
            "general_question": END,
            "translation": "Translation",
            "risk_analysis": "FailureDetection",
        }
    )
    main_graph_builder.add_edge("Translation", END)
    main_graph_builder.add_edge("FailureDetection", END)
    # Compile
    main_graph = main_graph_builder.compile()
    return main_graph

####################
#### DRAW GRAPH ####
####################
def draw_graph():
    with open('subgraph_translation.png', 'wb') as png:
        png.write(translation_subgraph.get_graph().draw_mermaid_png())
    with open('subgraph_encoding.png', 'wb') as png:
        png.write(encoding_subgraph.get_graph().draw_mermaid_png())
    with open('subgraph_failure_detection.png', 'wb') as png:
        png.write(failure_detection_subgraph.get_graph().draw_mermaid_png())
    with open('subgraph_new_risk.png', 'wb') as png:
        png.write(new_risk_subgraph.get_graph().draw_mermaid_png())
    with open('subgraph_chat.png', 'wb') as png:
        png.write(chat_subgraph.get_graph().draw_mermaid_png())
    with open('main_graph.png', 'wb') as png:
        png.write(main_graph.get_graph().draw_mermaid_png())


#############
#### RUN ####
#############
def init_agentic():
    """Set up the agentic constraint system with the given PDDL domain, problem and plan."""
    global retriever
    global translation_subgraph, encoding_subgraph, failure_detection_subgraph, chat_subgraph, new_risk_subgraph, main_graph
    retriever = set_up_rag()
    translation_subgraph = build_translation_subgraph()
    encoding_subgraph = build_encoding_subgraph()
    failure_detection_subgraph = build_failure_detection_subgraph()
    chat_subgraph = build_chat_subgraph()
    new_risk_subgraph = build_new_risk_subgraph()
    main_graph = build_main_graph()
    # draw_graph()
    

def TranslateUserInput(user_input):
    input_state = DecompositionState({"messages": [HumanMessage(content=user_input)], "user_input": user_input})
    final_state = translation_subgraph.invoke(input_state, {'recursion_limit': 100})
    encodings = final_state['encodingsE2NL']
    if PRINT_RESULTS := False:
        mprint(f"\nUser input:\n {user_input}")
        for e in encodings:
            mprint(f'• {e.constraint}')
            mprint(f'  → {e.e2nl.e2nl}')
            mprint(f'    → {e.encoding.encoding}')

    return encodings

def testTranslation():
    # user_input = "Only plane1 should be used."
    user_input = "Person7 should always be located at boston and plane2 should always be located at washington."
    # user_input = "Person7 should never move."
    # user_input = "Person7 should always be located in their initial city."
    TranslateUserInput(user_input) 

def testRAG():
    messages = []
    
    RAG_QUERY_GENREATION_PROMPT = (
        "You are a helpful PDDL planning expert and assistant. "
        "The problem currently being solved is described with a PDDL domain and problem, given below.\n"
        "<pddl_domain>\n"
        "{pddl_domain}\n"
        "</pddl_domain>\n"
        "<pddl_problem>\n"
        "{pddl_problem}\n"
        "</pddl_problem>\n"
        "<current_solution_plan>\n"
        "{pddl_plan}\n"
        "</current_solution_plan>\n"
        
        "Generate a RAG query to look for potential risk of failure of the given PDDL plan. "
        "It should includes keywords such as 'restriction', 'failure', 'risk', 'danger', 'limitation'. "
        "The query should also include any relevant keyword regarding the current problem being solve. "
    )
    messages += [HumanMessage(content= RAG_QUERY_GENREATION_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL, pddl_plan=G.current_plan))]
    
    RAG_query = 'ZenoTravel domain plan risk analysis fuel limitations aircraft capacity restrictions potential failure points in multi-aircraft passenger transportation plan with distance and fuel consumption constraints'    
    result = retrieve_with_metadata.invoke({'query': RAG_query})
    
    txt = 'RAG Query:\n' + RAG_query + '\n\nRAG Result:\n' + result
    print(txt)

def RiskAnalysis():
    final_state = failure_detection_subgraph.invoke(FailureDetectionState(first_loop=True), {'recursion_limit': 100})
    answer = final_state['answer']
    suggestions = final_state['suggestions']
    return answer, suggestions

def NewRisk():
    new_risk_subgraph.invoke(FailureDetectionState(first_loop=True, deeper_analysis=False), {'recursion_limit': 100})

def Chat():
    chat_subgraph.invoke(ChatState(),  {'recursion_limit': 100})

def testTopNode(mode="general_question"):
    
    ## TRANSLATION ##
    user_type = UserType(user_type="translation")
    # user_input = "Only plane1 should be used."
    user_input = "Person7 should always be located at boston and plane2 should always be located at washington."
    # user_input = "Person7 should never move."
    # user_input = "Person7 should always be located in their initial city."
    
    
    ## GENERAL QUESTION ##
    if mode == "general_question":
        # user_type = UserType(user_type="general_question")
    
        final_state = main_graph.invoke(MainState(messages=[HumanMessage(content=user_input)], user_input=user_input, user_type=user_type))
        encodings = final_state['encodingsE2NL']
        print("\nUser input:\n", user_input)
        for e in encodings:
            print(f'• {e.constraint}')
            print(f'  → {e.encoding.encoding}')
            print(f'    → {e.e2nl.e2nl}')

    ## FAILURE DETECTION ##
    elif mode == "risk_analysis":
        user_type = UserType(user_type="risk_analysis")
        final_state = main_graph.invoke(MainState(user_input=user_input, user_type=user_type))
    
        print('ANSWER:\n', final_state['answer'])
        print('\nSUGGESTIONS:\n', final_state['suggestions'])

if __name__=='__main__':
    SHELL_PRINTS = True
    GUI_PROMPT = False
    DRAW_GRAPH = True
    init_agentic()
    # retriever = set_up_rag()
    # translation_subgraph = build_translation_subgraph()
    # encoding_subgraph = build_encoding_subgraph()
    # failure_detection_subgraph = build_failure_detection_subgraph()
    # main_graph = build_main_graph()
    if DRAW_GRAPH:
        draw_graph(translation_subgraph, encoding_subgraph, failure_detection_subgraph, main_graph)
    # testTranslation(translation_subgraph)
    # testFailure(failure_detection_subgraph)
    # testRAG()    
    # testTopNode(main_graph,mode="translation")    
    testTopNode(mode="general_question")