import subprocess
import os
import anthropic
from defs import *
import tools_hddl
import time

client = anthropic.Anthropic(
    api_key=None
)
MAX_TOKEN=2000
TEMPERATURE=0.0
# MODEL="claude-3-5-haiku-20241022"
MODEL="claude-3-5-sonnet-20241022"

with open("./HDDL_method_description.txt", "r") as f:
    hddl_method_description = f.read()

g_message_history = []
def clear_message_history():
    global g_message_history
    g_message_history = []

def encodePrefs(domain, problem, preferences):
    global g_message_history
    
    # Setup request
    systemMsg="You are a HDDL planning expert. Your purpose is to translate natural language human preferences (preferred strategy) in how to perform a task into a new HDDL method to be used in a classical HDDL planner. Respond to the requested translations only with consise and accurate HDDL language."
    messages=[
            {"role": "user", "content": "I will share with you a text describing how HDDL method works. After I will share a HDDL domain followed by a corresponding HDDL problem. After that I will start to share human preferred strategy to translate."},
            {"role": "user", "content": hddl_method_description},
            
        #     {"role": "user", "content": "When translating natural language inputs into PDDL3.0 constraints, only use the following keywords: 'and','or','not','=','<','<=','>','>=','+','-','*','/','forall','exists','always','sometime','within','at-most-once','sometime-after','sometime-before','always-within','holding-during','hold-after','at-end'. After, I will share a PDDL domain followed by a corresponding PDDL problem. After that, I will share human preferences to translate."},
        
            {"role": "assistant", "content": "Got it now share with me the HDDL domain and problem."},
            {"role": "user", "content": domain + '\n' + problem},   
            {"role": "assistant", "content": "Got it now share with me the human preferences to translate. Note that if the preferred strategy is similar to an existing method, I will return the name of the method."},
            {"role": "user", "content": preferences},
            # {"role": "user", "content":  "First, reformule and rephrase the preferences in two different manners to better understand it and remove ambiguities. After, give me the encoding for the given preferences."},
        ]
    
    # Call LLM
    message = client.messages.create( model=MODEL, max_tokens=MAX_TOKEN, temperature=TEMPERATURE, system=systemMsg, messages= messages)
    
    # Update history with request and LLM answer
    g_message_history += messages + [{"role": "assistant", "content": message.content[0].text}]
    
    print('LLM:', message.content[0].text, "[END LLM]")
    
    return message.content[0].text

def reencodePrefs(feedback):
    global g_message_history
    
    # Setup request
    system="You are a HDDL planning expert. Your purpose is to translate natural language human preferences into HDDL method to be used in a classical HDDL planner. Respond to the requested translations only with consise and accurate HDDL language."
    messages=[
            {"role": "user", "content": "Your last translation is incorrect. Carefully generate a new correct translation considering the following feedback: "+feedback},
        ]
    
    # Call LLM
    message = client.messages.create( model=MODEL, max_tokens=MAX_TOKEN, temperature=TEMPERATURE, system=system, messages=g_message_history + messages)
    
    # Update history with request and LLM answer
    g_message_history += messages + [{"role": "assistant", "content": message.content[0].text},]
    print('LLM:', message.content[0].text, "[END LLM]")
    
    return message.content[0].text


if __name__ == '__main__':
    DOMAIN_PATH = './HDDL_env/zeno_domain.hddl'
    PROBLEM_PATH = "./HDDL_env/zeno_problem_5.hddl"

    # DOMAIN_PATH, PROBLEM_PATH = "NumericTCORE/benchmark/ZenoTravel-no-constraint/domain.pddl","NumericTCORE/benchmark/ZenoTravel-no-constraint/pfile5.pddl"
    start_time = time.time()
    output = subprocess.run(["./lilotane",'-v=0',DOMAIN_PATH, PROBLEM_PATH], capture_output=True, text=True, check=True)
    end_time = time.time()
    output_str = output.stdout
    # print(output_str)
    start_marker = "==>"
    end_marker = "<=="

    start = output_str.find(start_marker)
    end = output_str.find(end_marker, start)

    if start != -1 and end != -1:
        # Adjust to slice the content between markers
        extracted = output_str[start + len(start_marker):end].strip()
        print("Plan:\n", extracted)
        extracted = tools_hddl.format_lilotane_plan(extracted)
        print("Plan:\n", extracted)
        print(f"\n Planning time: {end_time-start_time:.6f}(sec)")
    else:
        print("Markers not found!")

    with open(DOMAIN_PATH,'r') as f_d:
        domain=f_d.read()
    with open(PROBLEM_PATH,'r') as f_p:
        problem = f_p.read()

    while True:
        #  Input of user Strategy to test
        print(color.BOLD + "Enter your preferences:\n" + color.END)
        pref = input()
        if pref=="exit":
            exit()
        keep_trying = True
        count = 0
        encodedPref = encodePrefs(domain, problem, pref)
        feedback=input("Does the answer match your preferences? (if yes, answer 'yes', if no, please provide feedback.)")
        while keep_trying or count > 5:
            count +=1
            if feedback.lower() == 'yes':
                # add method to domain and save it as an updated domain:
                new_domain = tools_hddl.updateDomain(domain, encodedPref)
                encodedOK, verify_result = tools_hddl.verifyMethodEncoding(new_domain, problem, encodedPref)
                if encodedOK:
                    print("Plan result with new domain:\n", verify_result[1])
                    keep_trying = False
                else:
                    re_encoded_choice = input("There is error with updated domain with new methods. The error is \n {} \n*** Do you want to re-encode your preference again? (answer 'no' if don't want, answer 'yes' with more feedback if needed)".format(verify_result))
                    if re_encoded_choice.lower() == "no":
                        keep_trying=False
                    else:
                        keep_trying = True
                        feedback = "There is error with updated domain with new methods. The error is \n {} \n*** Do you want to re-encode your preference again?".format(verify_result) + re_encoded_choice
            if keep_trying:
                print("Re-encode the preference...")
                encodedPref = reencodePrefs(feedback=feedback)
                feedback=input("Does the answer match your preferences? (if yes, answer 'yes', if no, please provide feedback.)")
        

# Preference: To transport a person,  if the plane and the person are in different cities, then fly the plane to the person, pick them up, take them to the destination, and drop them off.


