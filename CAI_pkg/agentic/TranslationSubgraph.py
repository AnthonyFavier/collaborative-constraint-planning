import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from typing import Annotated, List
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
import operator
from langgraph.types import Send
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages.modifier import RemoveMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from .. import Globals as G
from ..Helpers import mprint, minput
from .. import Helpers
from .. import constraint_planning
from . import ToolsLLM
from . import Models

######################################
#### STRUCTURED OUTPUTS AND STATE ####
######################################

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

## STATES ##
# Encoding
class EncodingState(TypedDict):
    e_messages: Annotated[list, add_messages]
    
    # Input
    user_input_e: str # User input
    refined_user_intent_e: str # Refined user intent, removing ambiguities from initial input
    decomposition_e: Decomposition # Decomposition of user input # WHYYYY???
    
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
    refined_user_intent: str # Refined user intent, removing ambiguities from initial input
    decomposition: Decomposition # Decomposition of user input
    decomposition_validation: DecompositionValidation # Automated validation of decomposition
    decomposition_user_validation: DecompositionUserValidation # User validation of decomposition
    encodingsE2NL: Annotated[list[EncodingE2NL], operator.add] # List of EncodingE2NL, populated by encoding workers

###########################
#### ENCODING SUBGRAPH ####
###########################

#NODE
def Encode(state: EncodingState):
    """Translate the given constraint into PDDL3.0"""

    if G.PRINT_AGENTIC_NODES:
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
    
    # llm = Models.reasonning_llm.with_structured_output(Encoding)
    llm = Models.reasonning_llm
    msg = Models.call(llm, state['e_messages'])
    answer = Models.extractAITextAnswer(msg)
    logger.info(answer)
    try:
        encoding = Helpers.extractTag('pddl', answer)
        encoding = constraint_planning.initialEncodingFixes(encoding)
    except Exception as err:
        encoding = err.args[0]
    
    encodingE2NL = state["encodingE2NL"]
    encodingE2NL.encoding = Encoding(encoding=encoding)
    
    ai_msg = AIMessage(content=encodingE2NL.encoding.encoding)
    
    return {'e_messages': [ai_msg], 'encodingE2NL': encodingE2NL}

#NODE
def Verifier(state: EncodingState):
    if G.PRINT_AGENTIC_NODES:
        print('Node: Verifier')
        logger.info('Node: Verifier')
    
    encoding = state["encodingE2NL"].encoding.encoding
    result = constraint_planning.checkEncoding(encoding)
    
    encodingOK = result=='OK'
    
    if state.get("encoding_validation"):
        encodingValidation = state['encoding_validation']
        encodingValidation.encoding_nb_retry += 1
        if encodingValidation.encoding_nb_retry > 5:
            print("WARNING: Exceeding 5 encoding attempts")
            raise Exception("Stopped ....") # TODO: catch this error..
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
    if G.PRINT_AGENTIC_NODES:
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
    
    
    llm = Models.e2nl_llm.with_structured_output(E2NL)
    
    messages = [
        sys_msg,
        HumanMessage(content=state["encodingE2NL"].encoding.encoding),
    ]
        
    msg = Models.call(llm, messages)

    encodingE2NL = state['encodingE2NL']
    encodingE2NL.e2nl = msg
    
    ai_msg = AIMessage(content="Back translation from PDDL3.0 to Natural Language:\n" + encodingE2NL.e2nl.e2nl)

    return {'e_messages': [ai_msg], "encodingE2NL": encodingE2NL}

#NODE
def UserReviewE2NL(state: EncodingState):
    if G.PRINT_AGENTIC_NODES:
        print('Node: UserReviewE2NL')
        logger.info('Node: UserReviewE2NL')
  
    
    # Show Data: constraint and back-translation
    txt = '\nConstraint: ' + state['encodingE2NL'].constraint + '\n\t⇓\nE2NL: ' + state['encodingE2NL'].e2nl.e2nl
    
    # Ask user for review
    G.AGENTIC_USER_INTERACTION_LOCK.acquire()
    user_review = ''
    if G.REVIEW_E2NL:
        user_review = minput(txt+'\n\nAre you satisfied with the back translation? If not, provide any desired feedback for me to consider.\n')
        if user_review.lower()=='':
            mprint("User: yes")
        else:
            mprint("User: " + user_review)
    G.AGENTIC_USER_INTERACTION_LOCK.release()
    # user_review = interrupt(txt+'\n\nAre you satisfied with the back translation? If not, provide any desired feedback for me to consider.\n> ')
    
    # If trivial positive answer move skip LLM call
    if user_review.lower() in ['yes', 'y', '']:
        return {"e2nl_user_validation": E2NLUserValidation(e2nl_user_ok=True, e2nl_user_feedback="")}
    
    # Evaluate user input: ok or not (structued output)
    llm = Models.light_llm.with_structured_output(E2NLUserValidation)
    
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
        
    msg = Models.call(llm, messages)
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
    if G.PRINT_AGENTIC_NODES:
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

## PHASE 1: Refining User Input ##
#NODE
def RefineUserIntent(state: DecompositionState):
    """Refines user input to remove ambiguity and properly capture the user intent. Can ask clarifying questions."""
    
    if G.PRINT_AGENTIC_NODES:
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
    llm = Models.main_llm.bind_tools([ToolsLLM.ask_clarifying_question])
    messages = [SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL))] + state['messages']
    msg = Models.call(llm, messages)
    return {"messages": [msg]}
    
#NODE
def SaveUserIntentClearMessages(state: DecompositionState):
    if G.PRINT_AGENTIC_NODES:
        print("Node: SaveUserIntentClearMessages")
        logger.info("Node: SaveUserIntentClearMessages")
        
    refined_user_intent = state['messages'][-1].content
    
    mprint(G.CHAT_SEPARATOR)
    mprint('AI: Refined user intent Below\n')
    mprint(refined_user_intent)
    
    messages_to_remove = state["messages"]
    remove_instructions = [RemoveMessage(id=m.id) for m in messages_to_remove]
    return {'refined_user_intent': refined_user_intent, "messages": remove_instructions} # Return as part of a state update

#NODE
def Decompose(state: DecompositionState):
    """Decompose the user input into a proper set of constraints"""
    
    mprint(G.CHAT_SEPARATOR)
    mprint("Decomposing ... \n")
    
    if G.PRINT_AGENTIC_NODES:
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
        
    llm = Models.main_llm.with_structured_output(Decomposition)
    msg = Models.call(llm, state['messages'])
    
    txt = ''
    txt+='Decomposition:\n'
    for d in msg.decomposition:
        txt+=f'- {d}\n'
    txt+='Explanation:\n'
    txt+=f'{msg.explanation}'
    ai_msg = AIMessage(content=txt)
    
    return {"messages": [ai_msg], "decomposition": msg}

################### NOT USED ###################
# For now VerifyDecomposition is not used as it is 
# empirically more disturbing than useful.
# But could be adapted and integrated back.
###################### \/ ######################
#NODE
def VerifyDecomposition(state: DecompositionState):
    """Ask a series of question to evaluate if decomposition looks good"""
    
    if G.PRINT_AGENTIC_NODES:
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
    
    llm = Models.light_llm.with_structured_output(DecompositionValidation)
    
    
    decomposition_str = ""
    for d in state['decomposition'].decomposition:
        decomposition_str += '- ' + d + '\n'
    decomposition_str += "Decomposition explanation:\n" + state["decomposition"].explanation
        
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(pddl_domain=G.DOMAIN_PDDL, pddl_problem=G.PROBLEM_PDDL)),
        HumanMessage(content=USER_PROMPT.format(user_input=state['user_input'], user_intent=state['refined_user_intent'], decomposition=decomposition_str)),
    ]
    msg = Models.call(llm, messages)
    
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
###################### /\ ######################

#NODE
def UserReviewDecomposition(state: DecompositionState):
    """Ask user for review of the decomposition"""
    
    # TODO: Find a way to add the clarifying question tool here. Currently conflicting with the structured output. 
    # Use two calls/nodes? 
    # A first one gathering user feedback and asking questions about it if needed?
    # A second one formatting the user feedback into the current structured output?
    
    if G.PRINT_AGENTIC_NODES:
        print("Node: UserReviewDecomposition")
        logger.info("Node: UserReviewDecomposition")
    
    # Format and Show decomposition
    decomposition_str = "\nDecomposition:\n"
    for d in state['decomposition'].decomposition:
        decomposition_str += '- ' + d + '\n'
    
    # Ask user for review
    G.AGENTIC_USER_INTERACTION_LOCK.acquire()
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
        
    G.AGENTIC_USER_INTERACTION_LOCK.release()
    # user_review = interrupt(decomposition_str+'\n\nAre you satisfied with the current decomposition? If not, provide any desired feedback for me to consider.\n> ')
    
    # If trivial positive answer move skip LLM call
    if user_review.lower() in ['yes', 'y', '']:
        return {'decomposition_user_validation': DecompositionUserValidation(decomp_user_ok=True, decomp_user_feedback='')}
    
    # Evaluate user input: ok or not (structued output)
    llm = Models.light_llm.with_structured_output(DecompositionUserValidation)
    
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
    msg = Models.call(llm, messages)
    return {'decomposition_user_validation': msg}

#CondEdge
def RoutingUserReviewDecomposition(state: DecompositionState):
    """Routes based on user review"""
    if state['decomposition_user_validation'].decomp_user_ok:
        return "OK"
    else:
        return "Retry"

## PHASE 2: Encoding ##
#NODE
def Orchestrator(state: DecompositionState):
    if G.PRINT_AGENTIC_NODES:
        print("Node: Orchestrator")
        logger.info("Node: Orchestrator")
    mprint(G.CHAT_SEPARATOR)
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
    if G.PRINT_AGENTIC_NODES:
        print("Node: Merge")
        logger.info("Node: Merge")
    return {}

#### BUILD ####
def build():
    encoding_subgraph = build_encoding_subgraph()

    translation_subgraph_builder = StateGraph(DecompositionState)
    # Add nodes
    translation_subgraph_builder.add_node("RefineUserIntent", RefineUserIntent)
    translation_subgraph_builder.add_node("ask_clarifying_question", ToolNode(tools=[ToolsLLM.ask_clarifying_question]))
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
    return translation_subgraph, encoding_subgraph
