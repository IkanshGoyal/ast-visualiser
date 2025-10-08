#latest version
from flask import Flask, request, jsonify
import base64
import os
import subprocess
from flask_cors import CORS
from graphviz import Digraph
from lexer import Tokenizer
from parser import Parser
import logging

app = Flask(__name__)
CORS(app, resources={r"/parse": {"origins": "*"}})

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def remove_preprocessor_directives(code):
    lines = code.split('\n')
    filtered_lines = []
    for line in lines:
        stripped_line = line.lstrip()
        if not stripped_line.startswith('#'):
            filtered_lines.append(line)
        else:
            logger.debug(f"Removed preprocessor directive: {stripped_line}")
    filtered_code = '\n'.join(filtered_lines)
    if not filtered_code.strip():
        logger.warning("Code only contains preprocessor directives")
    return filtered_code

def generate_dot(ast):
    dot = Digraph(
        graph_attr={'rankdir': 'TB', 'dpi': '300', 'size': '8,10', 'nodesep': '0.5', 'ranksep': '1.0'},
        node_attr={'shape': 'box', 'style': 'filled', 'fillcolor': 'lightblue', 'fontsize': '14', 'font': 'Helvetica'},
        edge_attr={'color': 'black'}
    )
    def add_node(node, parent_id=None):
        node_id = str(id(node))
        label = node.node_type
        if node.value:
            label += f": {node.value}"
        dot.node(node_id, label)
        if parent_id:
            dot.edge(parent_id, node_id)
        for child in node.children:
            add_node(child, node_id)
    add_node(ast)
    return dot

def ast_to_string(node, depth=0):
    result = "  " * depth + str(node) + "\n"
    for child in node.children:
        result += ast_to_string(child, depth + 1)
    return result

def parse_code(code):
    code = remove_preprocessor_directives(code).strip()
    logger.debug(f"Filtered Code: {repr(code)}")
    if not code:
        logger.error("No valid code provided after filtering")
        return {'error': 'No valid code provided after filtering'}

    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    logger.debug("Tokens:")
    for i, token in enumerate(tokens):
        logger.debug(f"  {i}: {token.type} = '{token.value}' (Line {token.line}, Col {token.column})")

    try:
        parser = Parser(tokens)
        ast = parser.parse()
        logger.debug(f"AST:\n{ast_to_string(ast)}")
        return {
            'tokens': [
                {
                    "index": i,
                    "type": token.type,
                    "value": token.value,
                    "line": token.line,
                    "column": token.column
                }
                for i, token in enumerate(tokens)
            ],
            'ast': ast_to_string(ast).strip(),
            'ast_node': ast
        }
    except Exception as e:
        logger.error(f"Parsing Error: {str(e)}")
        return {'error': f'Parsing failed: {str(e)}'}

@app.route('/parse', methods=['POST'])
def parse():
    try:
        logger.debug("Received request: %s", request.get_data(as_text=True))
        
        data = request.get_json(silent=True)
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        code = data.get('code', '')
        if not code.strip():
            logger.error("No code provided in request")
            return jsonify({'error': 'No code provided'}), 400
        
        logger.debug(f"Received code: {repr(code)}")
        
        result = parse_code(code)
        if 'error' in result:
            return jsonify(result), 400
        
        dot = generate_dot(result['ast_node'])
        logger.debug(f"DOT content:\n{dot.source}")
        
        # Save the DOT file
        dot_path = 'ast.dot'
        with open(dot_path, 'w') as dot_file:
            dot_file.write(dot.source)
        logger.debug("Saved DOT file as ast.dot")

        # Use the dot command to render the PNG
        png_path = 'ast-rendered.png'
        try:
            subprocess.run(['dot', '-Tpng', dot_path, '-o', png_path], check=True)
            logger.debug("Rendered PNG using dot command as ast-rendered.png")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to render PNG with dot command: {e}")
            return jsonify({'error': 'Failed to render AST image'}), 500
        except FileNotFoundError:
            logger.error("dot command not found. Ensure Graphviz is installed and in PATH.")
            return jsonify({'error': 'Graphviz dot command not found'}), 500

        # Read and encode the PNG
        with open(png_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            logger.debug(f"Base64 image length: {len(image_data)}")
        
        return jsonify({
            'tokens': result['tokens'],
            'ast': result['ast'],
            'image': f'data:image/png;base64,{image_data}'
        })
    
    except Exception as e:
        logger.error(f"Parsing or rendering failed: {str(e)}")
        return jsonify({'error': f'Parsing or rendering failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)