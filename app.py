# app.py
from flask import Flask, render_template, request, jsonify
import os
import hddl_to_graph
import CAI_hddl
import tools_hddl
from generate_htn_image import parse_plan, parse_plan_render
import networkx as nx

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC'] = 'static'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC'], exist_ok=True)
# GLOBAL DOMAIN = None
# GLOBAL PROBLEM = None
def nx_to_cytoscape_elements(G: nx.MultiDiGraph):
    # nodes = [{'data': {'id': str(n), 'label': str(n)}} for n in G.nodes()]
    nodes = []
    for n, d in G.nodes(data=True):
            if d['type'] == 'task':
                    color = 'darkblue'
                    shape = 'box'
            elif d['type'] == 'method':
                    color = 'darkgreen'
                    shape = 'ellipse'
            elif d['type'] == 'action':
                    color = 'black'
                    shape = 'box3d'
            elif d['type'] == 'root':
                    color = 'red'
                    shape = 'dot'
            nodes.append({'data': {'id': str(n), 'label': str(n), 'color': color, 'type': d['type'], 'shape': shape}})
    edges = []
    for u, v, key, data in G.edges(keys=True, data=True):
            # edge_id = f"{u}-{v}-{key}"
            if 'priority' in data.keys():
                label = data['priority'] if data['priority'] not in (-1, None) else ""
            else: 
                label = ""
            edge = {
                    'data': {
                            # 'id': edge_id,
                            'source': str(u),
                            'target': str(v),
                            # 'priority': data['priority'],  # default to 0
                            'label': label  # optional: show on edge
                    }
            }
            # # Optionally add attributes like weight, label, etc.
            # edge['data'].update({k: v for k, v in data.items()})
            edges.append(edge)

    return nodes+ edges

def digraph_to_cytoscape_elements(G: nx.DiGraph):
    """
    Converts a directed graph (nx.DiGraph) into Cytoscape-compatible elements.

    Args:
        G (nx.DiGraph): Input directed graph.

    Returns:
        list: Cytoscape-compatible elements (nodes and edges).
    """
    # Process nodes
    nodes = []
    for n, d in G.nodes(data=True):
            if d['type'] == 'task':
                    color = 'darkblue'
                    shape = 'roundrectangle'
            elif d['type'] == 'method':
                    color = 'darkgreen'
                    shape = 'ellipse'
            elif d['type'] == 'action':
                    color = 'black'
                    shape = 'rectangle'
            elif d['type'] == 'root':
                    color = 'red'
                    shape = 'diamond'
            nodes.append({'data': {'id': str(n), 'label': d['label'], 'color': color, 'type': d['type'], 'shape': shape}})
    edges = []
    for u, v, data in G.edges(data=True):
            edge = {
                    'data': {
                            # 'id': edge_id,
                            'source': u,
                            'target': v,
                            # 'priority': data['priority'],  # default to 0
                    }
            }
            # # Optionally add attributes like weight, label, etc.
            # edge['data'].update({k: v for k, v in data.items()})
            edges.append(edge)

    return nodes+ edges

def plan_with_hddl_planner(return_format_version=True):
    """Plan with the HDDL planner"""
    global DOMAIN_PATH, PROBLEM_PATH

    with open(DOMAIN_PATH, "r") as f:
        domain_str = f.read()
    with open(PROBLEM_PATH, "r") as f_prob:
        problem_str = f_prob.read()
    success, info = tools_hddl.verifyMethodEncoding(domain_str, problem_str, new_methods_str="",current_path="./", debug = False, return_format_version=return_format_version)
    if success:
        return info
    else:
        return "Failed to plan:\n" + str(info)

# def run_planner():
#     '''
#     what to do when the user clicks the Plan button
#     '''
#     print("Clicked Plan button --> Perform planning with the system HDDL planner")
#     text = ''
#     digraph_diagram = dict()
#     result = plan_with_hddl_planner(return_format_version=False)
#     if "Failed to plan" in result:
#         text = result
#         return {'text': text, 'elements': []}
#     plan_time_str = result.splitlines()[-1]
#     raw_plan = "\n".join(result.splitlines()[:-1])
#     formated_plan_text = tools_hddl.format_lilotane_plan(raw_plan)
#     text = formated_plan_text+ '\n' + plan_time_str
#     #Generate the plan diagram:
#     digraph_diagram = parse_plan(raw_plan)
#     graph_data = digraph_to_cytoscape_elements(digraph_diagram)

#     return {'text': text, 'elements': graph_data}

# Dummy placeholder for domain text display
@app.route('/load_domain', methods=['POST'])
def load_domain():
    global DOMAIN_PATH
    domain_file = request.files.get('domain')

    if domain_file:
        DOMAIN_PATH = os.path.join(app.config['UPLOAD_FOLDER'], domain_file.filename)
        domain_file.save(DOMAIN_PATH)
        with open(DOMAIN_PATH, 'r') as f:
            domain_text = f.read()
    else:
        domain_text = "(No domain file provided)"

    return jsonify({'domain': domain_text})

@app.route('/load_problem', methods=['POST'])
def load_problem():
    global PROBLEM_PATH
    problem_file = request.files.get('problem')

    if problem_file:
        PROBLEM_PATH = os.path.join(app.config['UPLOAD_FOLDER'], problem_file.filename)
        problem_file.save(PROBLEM_PATH)
        with open(PROBLEM_PATH, 'r') as f:
            problem_text = f.read()
    else:
        problem_text = "(No domain file provided)"

    return jsonify({'problem': problem_text})

# Simulate HTN viewer response from LLM and graph
@app.route('/view_htn', methods=['POST'])
def view_htn():
    query = request.json.get('query', '')
    
    # Simulate LLM response
    text_response = f"LLM explanation based on query: \"{query}\""
    
    # Example graph
    graph_data_old = {
        'elements': [
            {'data': {'id': 'MakeDinner', 'label': 'MakeDinner', 'color': 'blue'}},
            {'data': {'id': 'Cook', 'label': 'Cook', 'color': 'green'}},
            {'data': {'id': 'Serve', 'label': 'Serve', 'color': 'green'}},
            {'data': {'source': 'MakeDinner', 'target': 'Cook', 'label': 'part of'}},
            {'data': {'source': 'MakeDinner', 'target': 'Serve', 'label': 'part of'}},
        ]
    }
    parser = hddl_to_graph.HDDLParser(DOMAIN_PATH)
    nxgraph = parser.parse()
    graph_data = nx_to_cytoscape_elements(nxgraph)
    graph_data = {'elements': graph_data}

    return jsonify({'text': text_response, 'graph': graph_data})

# Delete methods:
@app.route('/delete_methods', methods=['POST'])
def delete_methods():
    # global DOMAIN_PATH
    return jsonify({'status': 'Methods deleted'})

# Ask LLM:
@app.route('/ask_llm', methods=['POST'])
def ask_LLM():
    # global DOMAIN_PATH
    return jsonify({'status': 'Methods deleted'})

@app.route('/run_planner', methods=['POST'])
def run_planner():
    '''
    run HDDL Planner and return text and graph data
    '''
    text = ''
    digraph_diagram = dict()
    result = plan_with_hddl_planner(return_format_version=False)
    if "Failed to plan" in result:
        text = result
        return jsonify({'text': text, 'elements': []})
        # return jsonify({'text': text, 'diagram_path': None})

    plan_time_str = result.splitlines()[-1]
    raw_plan = "\n".join(result.splitlines()[:-1])
    formated_plan_text = tools_hddl.format_lilotane_plan(raw_plan)
    text = formated_plan_text+ '\n' + plan_time_str
    #Generate the plan diagram:
    digraph_diagram = parse_plan(raw_plan)
    graph_data = digraph_to_cytoscape_elements(digraph_diagram)
    # Render the diagram and save to file
    # diagram_filepath = os.path.join(app.config['STATIC'],'plan_diagram')
    # digraph_diagram.render(filename=diagram_filepath, format='png', cleanup=True)
    return jsonify({'text': text, 'elements':graph_data})# 'diagram_path': '/static/plan_diagram.png'})
    



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
