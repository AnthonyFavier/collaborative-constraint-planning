from flask import Flask, jsonify, request, send_file, render_template
import os
# from hddl_to_graph import CAI_hddl
import CAI_hddl

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index_hddl.html')
@app.route('/get_operators', methods=['GET'])
def get_operators():
    try:
        # Retrieve the list of operators (mocked for now)
        operators = CAI_hddl.get_all_operators()  # Assuming this returns a list of operator names
        return jsonify(operators)
    except Exception as e:
        return str(e), 500

@app.route('/get_operator_graph', methods=['GET'])
def get_operator_graph():
    try:
        operator = request.args.get('operator')
        if not operator:
            return "Operator not specified.", 400

        # Get the graph image path for the operator
        graph_path = CAI_hddl.get_operator_graph_image_saved_wrapper(operator)
        if not os.path.exists(graph_path):
            return f"Graph image for operator '{operator}' not found.", 404

        return send_file(graph_path, mimetype='image/png')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)