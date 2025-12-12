import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from . import Globals as G
from .Helpers import mprint 
from . import ToolsLLM
from . import Models

######################################
#### STRUCTURED OUTPUTS AND STATE ####
######################################

## STATES ##
class SuggestionsState(TypedDict):
    messages: Annotated[list, add_messages]

##################
#### SUBGRAPH ####
##################

# NODE
def GenerateSuggestions(state: SuggestionsState):
    if 'PRINT_NODES' in globals():
        print("Node: GenerateSuggestions")
        logger.info("Node: GenerateSuggestions")

    mprint('\n' + G.CHAT_SEPARATOR + '\n')
    mprint("AI: ", end='')
    mprint("Generating suggestions to solve the problem...")

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
        
        "Analyze the key elements of the given problem. "
        "Identify trajectory constraints as promising strategies to solve the problem. "
        "The constraints should help and guide toward efficient solutions or alternatives. "
        "They can also prevent from searching toward inefficient solutions. "
        "For example, 'Resource X is costly, so it should never be used'. "
        "Format your answer such as a concise numbered list with no subitems. "
    )
    
    llm = Models.main_llm.bind_tools(suggestions_tools)
    messages = [SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL, pddl_plan=G.current_plan))] + state['messages']
    

    msg = Models.call(llm, messages)
    answer = Models.extractAITextAnswer(msg)
    logger.info(answer)
    if answer:
        mprint(answer)

    return {"messages": [msg]}

#### BUILD ####
def build():
    global suggestions_tools
    suggestions_tools = [
        ToolsLLM.ask_clarifying_question, 
        ToolsLLM.retrieve_with_metadata, 
        ToolsLLM.get_current_weather_city,
        ToolsLLM.basic_plan_analysis,
        ToolsLLM.count_number_step_in_plan,
        ToolsLLM.count_action_occurrence,
        ToolsLLM.simulatePlanTool,
    ]
    
    suggestions_subgraph_builder = StateGraph(SuggestionsState)
    
    # Add nodes
    suggestions_subgraph_builder.add_node("GenerateSuggestions", GenerateSuggestions)
    suggestions_subgraph_builder.add_node('SuggestionsTools', ToolNode(suggestions_tools))
    # Add edges
    suggestions_subgraph_builder.add_edge(START, "GenerateSuggestions")
    suggestions_subgraph_builder.add_conditional_edges(
        "GenerateSuggestions", 
        tools_condition,
        {
            'tools': 'SuggestionsTools',
            END: END,
        }
    )
    suggestions_subgraph_builder.add_edge('SuggestionsTools', 'GenerateSuggestions')
    # Compile
    suggestions_subgraph = suggestions_subgraph_builder.compile()
    return suggestions_subgraph
