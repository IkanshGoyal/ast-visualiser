from flask import Flask, request, jsonify
import base64
import os
import tempfile
from flask_cors import CORS
from graphviz import Digraph
from lexer import tokenize
from parser import parse_root

app = Flask(__name__)
CORS(app)

def remove_preprocessor_directives(code):
    lines = code.split('\n')
    filtered_lines = [line for line in lines if not line.lstrip().startswith('#')]
    return '\n'.join(filtered_lines)

def generate_dot(ast):
    dot = Digraph()
    def add_node(node, parent_id=None):
        node_id = str(id(node))
        label = node[0] if isinstance(node, tuple) else str(node)
        dot.node(node_id, label)
        if parent_id:
            dot.edge(parent_id, node_id)
        if isinstance(node, tuple) and len(node) > 1:
            for child in node[1:]:
                add_node(child, node_id)
    add_node(ast)
    return dot

def parse_code(code):
    # Remove preprocessor directives and strip whitespace
    code = remove_preprocessor_directives(code).strip()
    print(f"Filtered Code: {repr(code)}")
    if not code:
        return {'error': 'No valid code provided after filtering'}

    # Tokenize and display tokens
    tokens = list(tokenize(code))
    print("Tokens:")
    for i, token in enumerate(tokens):
        print(f"  {i}: {token.value} (Line {token.line}, Pos {token.pos})")

    # Parse and catch errors
    try:
        ast, remaining_tokens = parse_root(tokens)
        print(f"AST: {ast}")
        if remaining_tokens:
            print(f"Remaining Tokens: {[t.value for t in remaining_tokens]}")
            return {'error': f'Parsing incomplete: {remaining_tokens}'}
        return ast
    except Exception as e:
        print(f"Parsing Error: {str(e)}")
        return {'error': f'Parsing failed: {str(e)}'}

@app.route('/parse', methods=['POST'])
def parse():
    data = request.get_json()
    code = data.get('code', '')
    if not code.strip():
        return jsonify({'error': 'No code provided'})
    try:
        result = parse_code(code)
        if isinstance(result, dict) and 'error' in result:
            return jsonify(result)
        dot = generate_dot(result)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_image:
            temp_image_path = temp_image.name
            dot.render(temp_image_path, format='png', view=False)
            with open(temp_image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            os.unlink(temp_image_path)
        return jsonify({'image': f'data:image/png;base64,{image_data}'})
    except Exception as e:
        return jsonify({'error': f'Parsing or rendering failed: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)