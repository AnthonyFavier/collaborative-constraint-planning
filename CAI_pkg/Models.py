import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import time
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import anthropic
import openai

from .Helpers import mprint

################
#### MODELS ####
################
e2nl_llm = ChatOpenAI(model="gpt-4.1-mini-2025-04-14", temperature=0)
light_llm = ChatAnthropic(model="claude-3-5-haiku-latest", max_tokens=4000, temperature=0)
reasonning_llm = ChatAnthropic(model='claude-sonnet-4-20250514', max_tokens=4000, thinking={"type": "enabled", "budget_tokens": 2000})
bigger_llm = ChatAnthropic(model='claude-sonnet-4-20250514', max_tokens=4000)

main_llm = bigger_llm

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