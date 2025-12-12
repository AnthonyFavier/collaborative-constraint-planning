import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from . import Globals as G
from .Helpers import mprint, minput
from . import Models
from . import ToolsLLM

######################################
#### STRUCTURED OUTPUTS AND STATE ####
######################################

## STATES ##
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]

##################
#### SUBGRAPH ####
##################

#NODE
def ChatGetUserInput(state: ChatState):
    if G.PRINT_AGENTIC_NODES:
        print("Node: ChatGetUserInput")
        logger.info("Node: ChatGetUserInput")
    
    G.AGENTIC_USER_INTERACTION_LOCK.acquire()
    mprint("\n[ Ask anything or type 'exit' ]\n" + G.CHAT_SEPARATOR + '\n')
    mprint("User: ", end='')
    question = minput()
    mprint(question)
    G.AGENTIC_USER_INTERACTION_LOCK.release()

    return {"messages": [HumanMessage(content=question)]}

#CondEdge
def ChatCondEnd(state: ChatState):
    if state['messages'][-1].content.lower() in ['exit', 'q']:
        return END
    return 'OK'

#NODE
def ChatAnswer(state: ChatState):
    if G.PRINT_AGENTIC_NODES:
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
    
    llm = Models.main_llm.bind_tools(chat_tools)
    messages = [SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL, pddl_plan=G.current_plan))] + state['messages']
    
    msg = Models.call(llm, messages)
    answer = Models.extractAITextAnswer(msg)
    logger.info(answer)
    if answer:
        mprint('\n' + G.CHAT_SEPARATOR + '\n')
        mprint("AI: ", end='')
        mprint(answer, no_log=True)

    return {"messages": [msg]}


#### BUILD ####
def build():
    global chat_tools
    chat_tools = [
        ToolsLLM.ask_clarifying_question, 
        ToolsLLM.retrieve_with_metadata, 
        ToolsLLM.get_current_weather_city,
        ToolsLLM.basic_plan_analysis,
        ToolsLLM.count_number_step_in_plan,
        ToolsLLM.count_action_occurrence,
        ToolsLLM.simulatePlanTool,
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
