import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from .. import Globals as G
from ..Helpers import mprint, minput

import os
import requests
import json 
from langchain_community.document_loaders import TextLoader, PyPDFLoader    
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import *
from unified_planning.plans import ActionInstance, SequentialPlan
    
###################
#### SETUP RAG ####
###################
def DocLoader(filename):
        _,ext = filename.split('.')
        if ext in ['pdf']:
            doc = PyPDFLoader(filename).load()
        else:
            doc = TextLoader(filename).load()
        return doc

retriever = None # Global RAG retriever
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
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512, chunk_overlap=20
    )
    doc_splits = text_splitter.split_documents(docs_list)
    print('OK')

    ## INDEXING and RETREIVER
    print('Indexing documents ... ', end='', flush=True)
    # mprint('Indexing documents ... ', end='')
    vectorstore = InMemoryVectorStore.from_documents(
        documents=doc_splits, embedding=OpenAIEmbeddings()
    )
    global retriever
    retriever = vectorstore.as_retriever()
    print('OK')
    return retriever

###############
#### TOOLS ####
###############
@tool
def ask_clarifying_question(question: str) -> str:
    """Ask the user the clarifying question given as input and 
    returns the user answer."""

    print('    Tool call: ask_clarifying_question')
    logger.info('    Tool call: ask_clarifying_question')
    logger.info('inputs:\n-question: ' + str(question))
    mprint(G.CHAT_SEPARATOR)
    q = minput("AI: "+question+'\n')
    if q.lower() == '':
        q='yes'
    mprint(G.CHAT_SEPARATOR)
    mprint("User: " + q)
    logger.info('output: ' + q)
    return q

#search_tool = TavilySearch(max_results=2)

@tool
def basic_plan_analysis(plan: str) -> str:
    """Receives a plan and computes a few basic caracterics such as 
    number of steps and each action occurence."""

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
    """Count the occurence of a specific action based on its exact name and 
    parameters formatted as '<action_name> <param1> <param2>...'. 
    If only '<action_name>' is provided, all occurrences will be counted, 
    regarless of the different action parameters."""

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
    """Get the accurate real time weather of a given city. The weather 
    includes the following: temperature, humidity, wind speed, and wind 
    direction."""

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
    response = requests.get(api_url, headers={'X-Api-Key': os.environ.get("API_NINJA_API_KEY")})
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
    response = requests.get(api_url, headers={'X-Api-Key': os.environ.get("API-API_NINJA_API_KEY")})
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
