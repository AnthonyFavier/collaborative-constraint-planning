#######################
#### LOAD API KEYS ####
#######################

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

####################
#### PDDL FILES ####
####################

# LOAD files
PROBLEM_CHOICE = [
    'zeno',
    # 'rover',
][0]

if PROBLEM_CHOICE=='zeno':
    DOMAIN_PATH = 'zeno_dom.pddl'
    PROBLEM_PATH = 'zeno13.pddl'
    PLAN_PATH = 'zeno13_plan.txt'
elif PROBLEM_CHOICE=='rover':
    DOMAIN_PATH = 'rover_dom.pddl'
    PROBLEM_PATH = 'rover10.pddl'
    PLAN_PATH = 'rover10_plan.txt'
else: raise Exception("problem unknown")

with open(DOMAIN_PATH, 'r') as f:
    g_domain = f.read()
with open(PROBLEM_PATH, 'r') as f:
    g_problem = f.read()
with open(PLAN_PATH, 'r') as f:
    g_plan = f.read()

#############################
#### SETUP DOCUMENTS RAG ####
#############################

## LOAD ##
print('Loading documents ... ', end='', flush=True)
from langchain_community.document_loaders import TextLoader, PyPDFLoader    
from langchain_community.document_loaders import UnstructuredMarkdownLoader
DOCUMENT_PATH = "documents/"
files = [
    # PDDL
    # DOMAIN_PATH,
    # PROBLEM_PATH,
    # PLAN_PATH,
    
    # Fake reports
    {
        "name": "fake_aircraft_plane1.md", 
        "description": "AIRCRAFT TECHNICAL & OPERATIONAL REPORT - Plane1",
    },
    {
        "name": "fake_aircraft_plane2.md", 
        "description": "AIRCRAFT TECHNICAL & OPERATIONAL REPORT - Plane1",
    },
    {
        "name": "fake_doc_airport_atlanta.md", 
        "description": "INTERNAL REPORT: ATLANTA INTERNATIONAL AIRPORT (ATL)",
    },
    {
        "name": "fake_doc_airport_newyork.md", 
        "description": "INTERNAL REPORT: JOHN F. KENNEDY INTERNATIONAL AIRPORT (JFK)",
    },
    {
        "name": "fake_report1.md", 
        "description": "FIELD REPORT - Urban Tree Health Monitoring - Spring Assessment 2025",
    },
]

def DocLoader(filename):
    _,ext = filename.split('.')[1]
    if ext in ['pdf']:
        doc = PyPDFLoader(filename).load()
    else:
        doc = TextLoader(filename).load()
    return doc

docs = []
for f in files:
    doc = DocLoader(DOCUMENT_PATH+f['name'])
    doc[0].metadata['description'] = f['description']
    docs.append(doc)
    
docs_list = [item for sublist in docs for item in sublist]
print('OK')

## SPLITTING
print('Splitting documents ... ', end='', flush=True)
from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=512, chunk_overlap=20
)
doc_splits = text_splitter.split_documents(docs_list)
print('OK')

## INDEXING and RETREIVER
print('Indexing documents ... ', end='', flush=True)
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
vectorstore = InMemoryVectorStore.from_documents(
    documents=doc_splits, embedding=OpenAIEmbeddings()
)
retriever = vectorstore.as_retriever()
print('OK')


###################
#### SETUP LLM ####
###################
print('Setup LLM models ... ', end='', flush=True)

LLM_CHOICE = [
    # 'llama3.1:8b-instruct-fp16',
    # 'llama3.1',
    # 'gpt-4.1',
    'claude-3-5-haiku-latest',
    # 'claude-sonnet-4-20250514',
][0]

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
if LLM_CHOICE=='llama3.1:8b-instruct-fp16':
    llm = ChatOllama(
        model="llama3.1:8b-instruct-fp16",
        temperature=0,
    )
elif LLM_CHOICE=='llama3.1':
    llm = ChatOllama(
        model="llama3.1",
        temperature=0,
    )
elif LLM_CHOICE=='claude-3-5-haiku-latest':
    llm = ChatAnthropic(model="claude-3-5-haiku-latest", max_tokens=4000, temperature=0)
elif LLM_CHOICE=='claude-sonnet-4-20250514':
    llm = ChatAnthropic(model='claude-sonnet-4-20250514', max_tokens=4000, thinking={"type": "enabled", "budget_tokens": 2000})
else: raise Exception('LLM_CHOICE not supported')

print('OK')

######################
#### SETUP TOOLS #####
######################
print('Setup tools ... ', end='', flush=True)
from langchain.tools.retriever import create_retriever_tool
from langchain.tools import Tool

## Create tools
tools = []

retriever_tool = create_retriever_tool(
    retriever,
    "retriever",
    "Retriever tool able to extract content from available documents that is relevant to the given query.",
)
tools.append(retriever_tool)

# def retrieve_with_metadata(query: str) -> str:
#     # results = retriever.get_relevant_documents(query)
#     results = retriever.invoke(query)
#     formatted_chunks = []

#     for i, doc in enumerate(results):
#         formatted_chunks.append(
#             f"<chunk_{i+1}>\n"
#             f"Source: {doc.metadata.get('source', 'Unknown')}\n"
#             f"Description: {doc.metadata.get('description', '')}\n"
#             f"Content: {doc.page_content}\n"
#             f"</chunk_{i+1}>\n"
#         )
#     return "\n".join(formatted_chunks)
# retriever_tool = Tool(
#     name="retriever",
#     func=retrieve_with_metadata,
#     description="Use this tool to retrieve relevant documents with context and metadata for a given question."
# )
# tools.append(retriever_tool)

from langchain_tavily import TavilySearch
search_tool = TavilySearch(max_results=3)
tools.append(search_tool)

from langchain_core.tools import tool
from manual_plan_generation import simulatePlan
@tool
def simulatePlanTool(plan: str, metric: str) -> str:
    """Simulate the given plan execution, checking its validity and computing its cost given the name of the metric of measure."""
    feedback = simulatePlan(DOMAIN_PATH, PROBLEM_PATH, plan, metric, separator_plan=' ', is_numered=False)
    return feedback
tools.append(simulatePlanTool)

# FailureDetection
@tool
def failure_detection():
    """Using the  """
    result = retriever_tool.invoke({'query':
        "restrictions, failure, danger"
    })
    
## Bind LLM and tools
llm_with_tools = llm.bind_tools(tools)

print('OK')

from langchain_community.tools import HumanInputRun

##########################
#### GRAPH COMPONENTS ####
##########################

print('Defining graph components ... ', end='', flush=True)

from langgraph.graph import StateGraph, START, END
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

## Chat Model
# Equivalent to MessageState
class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    response = (llm_with_tools.invoke(state['messages']))
    return {'messages': [response]}

## Grader
from pydantic import BaseModel, Field
from typing import Literal

GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question. \n "
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
)

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

grader_model = ChatAnthropic(model="claude-3-5-haiku-latest", max_tokens=4000, temperature=0)

def grade_documents(
    state: State,
) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""
    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)
    response = (
        grader_model
        .with_structured_output(GradeDocuments).invoke(
            [{"role": "user", "content": prompt}]
        )
    )
    score = response.binary_score

    if score == "yes":
        print("GRADER: is relevant")
        return "generate_answer"
    else:
        print("GRADER: not relevant")
        return "rewrite_question"

## Rewrite query
REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Formulate an improved question:"
)
def rewrite_question(state: State):
    """Rewrite the original user question."""
    messages = state["messages"]
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [{"role": "user", "content": response.content}]}

## Generate answer
GENERATE_PROMPT = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer the question. "
    "If you don't know the answer, just say that you don't know. "
    "Use three sentences maximum and keep the answer concise.\n"
    "Question: {question} \n"
    "Context: {context}"
)
def generate_answer(state: State):
    """Generate an answer."""
    question = state["messages"][0].content
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = llm.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}

def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return [tool_call['name'] for tool_call in ai_message.tool_calls]
    return END

print('OK')

#####################
#### BUILD GRAPH ####
#####################
from langgraph.prebuilt import ToolNode, tools_condition

print('Building graph ... ', end='', flush=True)
workflow = StateGraph(State)

workflow.add_node(chatbot)
# workflow.add_node(ToolNode(tools=tools))
workflow.add_node("retrieve", ToolNode([retriever_tool]))
workflow.add_node("web_search", ToolNode([search_tool]))
workflow.add_node("plan_simulation", ToolNode([simulatePlanTool]))
workflow.add_node(rewrite_question)
workflow.add_node(generate_answer)

workflow.add_edge(START, "chatbot")
workflow.add_conditional_edges(
    'chatbot',
    route_tools,
    {
        # "tools": "tools",
        "retriever": "retrieve",
        "tavily_search": "web_search",
        "plan_simulation": "plan_simulation",
        END: END,
    }
)
workflow.add_edge('web_search', 'chatbot')
workflow.add_edge('plan_simulation', 'chatbot')
workflow.add_conditional_edges(
    'retrieve',
    grade_documents,
    {
        "generate_answer": "generate_answer",
        "rewrite_question": "rewrite_question",
    }
)
workflow.add_edge('generate_answer', END)
workflow.add_edge('rewrite_question', 'chatbot')

from langgraph.checkpoint.memory import InMemorySaver
memory = InMemorySaver()
graph = workflow.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}

print('OK')

from IPython.display import Image, display
with open('graph.png', 'wb') as png:
    png.write(graph.get_graph().draw_mermaid_png())



###################
#### RUN GRAPH ####
###################

init_prompt = f"""
Here is below the PDDL domain, problem, and plan for the ZenoTravel13 problem from the ZenoTravel domain.
[DOMAIN]
{g_domain}

[PROBLEM]
{g_problem}

[PLAN]
{g_plan}
"""[1:-1]

#####################

RAG_QUERY_GENREATION_PROMPT = (
    "You are a helpful assistant to generate specific RAG requests to retrieve relevant context. "
    "Our focus is on the following PDDL domain and problem, with the following plan as current solution:\n"
    "[DOMAIN]\n"
    "{domain}\n"
    "[PROBLEM]\n"
    "{problem}\n"
    "[PLAN]\n"
    "{plan}\n"
    "Generate a RAG query to look for potential risk of failure of the given PDDL plan. "
    "It should includes keywords such as 'restriction', 'failure', 'risk', 'danger', 'limitation'. "
    "The query should also include any relevant keyword regarding the current problem being solve. "
    "Format your answer such that the query is between the tags <query> and </query>"
)
messages = [
    {"role": "user", "content": RAG_QUERY_GENREATION_PROMPT.format(domain=g_domain, problem=g_problem, plan=g_plan)},
]
result = llm.invoke(messages)
query = result.content.split('<query>')[1].split('</query>')[0]
print(query)

result = retriever_tool.invoke({'query':
    query
})
print(result)

GENERATE_ANSWER_PROMPT = (
    "You are an assistant for solving PDDL planning problems. "
    "Use the following pieces of retrieved context to identify possible risk of failure of the following plan. "
    "The given context is splitted in different chunks, each encapsulated in <chunk_i> tags. "
    "If you don't know the answer, just say that you don't know. "
    "Focus on practical risks that may directly change or affect the given plan. "
    "Your answer should only be three sentences maximum, so focus on the most relevant risks to the plan.\n"
    "Plan: {plan} \n"
    "Context: {context}"
)
messages = [{"role": "user", "content": GENERATE_ANSWER_PROMPT.format(plan=g_plan, context=result)}]
result = llm.invoke(messages)
print(result.content)

exit()

#####################

def stream_graph_updates(user_input: str):
    messages = [{"role": "user", "content": user_input}]
    events = graph.stream(
        {"messages": messages},
        config, 
        stream_mode="values",               
    )
    for event in events:
        print(' ')
        event['messages'][-1].pretty_print()

while True:
    user_input = input("\nUser: ")
    # user_input = "What do you know about LangGraph?"
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    stream_graph_updates(user_input)