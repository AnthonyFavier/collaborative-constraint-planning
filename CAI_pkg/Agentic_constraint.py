import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from langchain_core.messages import HumanMessage

from .Helpers import mprint
from . import ToolsLLM
from . import ChatSubgraph
from . import RiskAnalysisSubgraph
from . import TranslationSubgraph
from . import SuggestionsSubgraph

####################
#### DRAW GRAPH ####
####################
def draw_graphs():
    with open('translation_subgraph.png', 'wb') as png:
        png.write(translation_subgraph.get_graph().draw_mermaid_png())
    with open('encoding_subgraph.png', 'wb') as png:
        png.write(encoding_subgraph.get_graph().draw_mermaid_png())
    with open('new_risk_subgraph.png', 'wb') as png:
        png.write(new_risk_subgraph.get_graph().draw_mermaid_png())
    with open('chat_subgraph.png', 'wb') as png:
        png.write(chat_subgraph.get_graph().draw_mermaid_png())
    with open('suggestions_subgraph.png', 'wb') as png:
        png.write(suggestions_subgraph.get_graph().draw_mermaid_png())


#############
#### RUN ####
#############

def init_agentic():
    """Set up the agentic constraint system with the given PDDL domain, problem and plan."""
    ToolsLLM.set_up_rag()
    
    global translation_subgraph, encoding_subgraph
    translation_subgraph, encoding_subgraph = TranslationSubgraph.build()
    
    global chat_subgraph
    chat_subgraph = ChatSubgraph.build()
    
    global new_risk_subgraph
    new_risk_subgraph = RiskAnalysisSubgraph.build()

    global suggestions_subgraph
    suggestions_subgraph = SuggestionsSubgraph.build()

    # draw_graphs()

def TranslateUserInput(user_input):
    input_state = TranslationSubgraph.DecompositionState({"messages": [HumanMessage(content=user_input)], "user_input": user_input})
    final_state = translation_subgraph.invoke(input_state, {'recursion_limit': 100})
    encodings = final_state['encodingsE2NL']
    if PRINT_RESULTS := False:
        mprint(f"\nUser input:\n {user_input}")
        for e in encodings:
            mprint(f'• {e.constraint}')
            mprint(f'  → {e.e2nl.e2nl}')
            mprint(f'    → {e.encoding.encoding}')

    return encodings

def NewRisk():
    input_state = RiskAnalysisSubgraph.FailureDetectionState(first_loop=True, deeper_analysis=False)
    final_state = new_risk_subgraph.invoke(input_state, {'recursion_limit': 100})

def Chat():
    input_state = ChatSubgraph.ChatState()
    final_state = chat_subgraph.invoke(input_state, {'recursion_limit': 100})

def Suggestions():
    input_state = SuggestionsSubgraph.SuggestionsState()
    final_state = suggestions_subgraph.invoke(input_state, {'recursion_limit': 100})