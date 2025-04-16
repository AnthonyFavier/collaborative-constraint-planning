### HELPER FUNCTIONS FOR HDDL
import subprocess
def extract_blocks(text, keyword="(:method"):
    blocks = []
    start = 0
    while True:
        start = text.find(f"{keyword}", start)
        if start == -1:
            break
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '(':
                depth += 1
            elif text[i] == ')':
                depth -= 1
            if depth == 0:
                blocks.append(text[start:i+1])
                start = i + 1
                break
    return blocks
def updateDomain(domain_str, new_method):
    ''' This function add new method into the domain file, and saved it in a different file with label -modifed-
    inputs:
    - domain_str: a string of domain
    - new_method: a string of (:method name...)
    outputs:
    new_domain_str: a string of updated domain with new_method
    '''
    updatedDomain = None 
    # extract method blocks: blocks that start with (:method:
    new_method_blocks_list = extract_blocks(new_method,keyword="(:method")
    # Find position to insert 
    ## find action block, add new_method right before the first action block
    i_metric = domain_str.find("(:action")
    if i_metric!=-1:
        i_insert = i_metric
    ## Else, insert before last parenthesis
    else:
        i_insert=len(domain_str)-1
        while domain_str[i_insert]!=')':
            i_insert-=1
    
    # Insert constraints into problem
    updatedDomain = domain_str[:i_insert] + "\n"+ "\n".join(new_method_blocks_list) + "\n" + domain_str[i_insert:]
    
    return updatedDomain

def verifyMethodEncoding(updated_domain, problem, new_methods_str,current_path="./"):
    '''
    inputs:
    - updated_domain: string of updated domain with new methods
    - problem: string of problem in hddl
    - new_methods_str: string of new methods 
    - current_path: current path to save files
    outputs:
    - boolean if the updated domain is valid
    - feedback_str: string of feedback if it is not valid, return plan if it is valid
    '''
    # save updated_domain to a hddl file
    updated_domain_file_path = current_path + "temp_domain.hddl"
    problem_file_path = current_path + "temp_problem.hddl"
    with open(updated_domain_file_path, "w") as updated_domain_file:
        updated_domain_file.write(updated_domain)
    with open(problem_file_path, "w") as problem_file:
        problem_file.write(problem)
    
    # run lilotane:
    try:
        output = subprocess.run(["./lilotane",updated_domain_file_path, problem_file_path], capture_output=True, text=True, check=True)
        output_str = output.stdout
        start_marker = "==>"
        end_marker = "<=="

        start = output_str.find(start_marker)
        end = output_str.find(end_marker, start)

        if start != -1 and end != -1:
            # Adjust to slice the content between markers
            extracted = output_str[start + len(start_marker):end].strip()
            print("Plan:\n", extracted)
            return True, extracted
        else:
            print("Plan not found!")
            return False, "Couldn't find a valid plan, although there is no error."
    except subprocess.CalledProcessError as e:
        error = "Program failed with new method! New method added: \n{}".format(new_methods_str)+"\n--- Exit code: "+ str(e.returncode) + "\nError output:"+ str(e.stderr)
        return False, error