# app.py
from flask import Flask, render_template, request, jsonify
import os
import hddl_to_graph
import CAI_hddl
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# GLOBAL DOMAIN = None
# GLOBAL PROBLEM = None

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
    graph_data = hddl_to_graph.nx_to_cytoscape_elements(nxgraph)
    graph_data = {'elements': graph_data}

    return jsonify({'text': text_response, 'graph': graph_data})

# Delete methods:
@app.route('/delete_methods', methods=['POST'])
def delete_methods():
    # global DOMAIN_PATH
    return jsonify({'status': 'Methods deleted'})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
