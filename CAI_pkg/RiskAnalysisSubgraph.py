import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from typing import Annotated
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from . import Globals as G
from .Helpers import mprint, minput
from . import ToolsLLM
from . import Models

######################################
#### STRUCTURED OUTPUTS AND STATE ####
######################################

## TYPES ##
class RAGQuery(BaseModel):
    query: str = Field(
        '', description="RAG query to be used by a RAG retriver to find context data relevant to the query."
    )

## STATES ##
class FailureDetectionState(TypedDict):
    messages: Annotated[list, add_messages]
    rag_query: RAGQuery # RAG query to find relevant context in documents for failure detection
    rag_result: str # Resul of the RAG query
    answer: str # Answer for the failure detection request
    suggestions: str # Concrete suggestions to account the identifies potential risks
    first_loop: bool
    deeper_analysis: bool
    user_question: str

##################
#### SUBGRAPH ####
##################

#NODE
def RiskRetrieval(state: FailureDetectionState):
    
    if G.PRINT_AGENTIC_NODES:
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
    
    llm = Models.main_llm.bind_tools(new_risk_tools)
    msg = Models.call(llm, state['messages'])
    
    answer = Models.extractAITextAnswer(msg)
    logger.info(answer)
    if answer:
        mprint(G.CHAT_SEPARATOR)
        mprint("AI: " + answer) 
    
    return {'messages': [msg], 'first_loop': False}

#NODE
def RiskAskDeeper(state: FailureDetectionState):
    if G.PRINT_AGENTIC_NODES:
        print('Node: RiskAskDeeper')
        logger.info('Node: RiskAskDeeper')
    
    G.AGENTIC_USER_INTERACTION_LOCK.acquire()
    
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
    G.AGENTIC_USER_INTERACTION_LOCK.release()
    
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
    if G.PRINT_AGENTIC_NODES:
        print('Node: RiskQuestion')
        logger.info('Node: RiskQuestion')
    
    h_msg = HumanMessage(content=state['user_question'])
    if state['first_loop']:
        state['messages'] += [h_msg]
    
    llm = Models.main_llm.bind_tools(new_risk_tools)
    msg = Models.call(llm, state['messages'])
    
    answer = Models.extractAITextAnswer(msg)
    logger.info(answer)
    if answer:
        mprint(G.CHAT_SEPARATOR)
        mprint("AI: " + answer) 
    
    return {'messages': [msg], 'first_loop': False}
    
#NODE
def RiskDeeperAnalysis(state: FailureDetectionState):
    
    if G.PRINT_AGENTIC_NODES:
        print('Node: RiskDeeperAnalysis')
        logger.info('Node: RiskDeeperAnalysis')
        
    ADD_RETRIEVAL_PROMPT = (
        "Conduct a deeper and wider risk analysis based on the external data available. "
    )
    h_msg = HumanMessage(content=ADD_RETRIEVAL_PROMPT.format())
    
    if state['first_loop']:
        state['messages'] += [h_msg]
    
    llm = Models.main_llm.bind_tools(new_risk_tools)
    msg = Models.call(llm, state['messages'])
    
    answer = Models.extractAITextAnswer(msg)
    logger.info(answer)
    if answer:
        mprint(G.CHAT_SEPARATOR)
        mprint("AI: " + answer) 
    
    return {'messages': [msg], 'first_loop': False}

#### BUILD ####  
def build():
    global new_risk_tools
    new_risk_tools = [ToolsLLM.retrieve_with_metadata, ToolsLLM.get_current_weather_city]
    
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
    
