from flask import Flask, request, jsonify
from pycparser import c_parser, c_ast
from flask_cors import CORS
import subprocess
import tempfile
import pycparser
import os
import graphviz
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend requests

class ASTConverter:
    def to_dot(self, node, dot, parent_id=None):
        """Convert a pycparser AST node to Graphviz DOT format."""
        if not isinstance(node, c_ast.Node):
            return
        if isinstance(node, c_ast.Typedef):  # Skip Typedef nodes
            return

        # Generate a unique ID for the node
        node_id = f"n{hash(str(node)) % 1000000}"  # Unique ID based on hash

        # Label for the node (type and relevant attributes)
        label = node.__class__.__name__
        if hasattr(node, 'name') and node.name:
            label += f": {node.name}"
        elif hasattr(node, 'value') and node.value:  # Fixed: Changed 'value' to 'node.value'
            label += f": {node.value}"
        elif hasattr(node, 'op') and node.op:
            label += f": {node.op}"

        # Add the node to the graph
        dot.node(node_id, label)

        # Connect to parent if exists
        if parent_id:
            dot.edge(parent_id, node_id)

        # Recursively process children
        if isinstance(node, c_ast.FileAST):
            for child in node.ext:
                self.to_dot(child, dot, node_id)
        elif isinstance(node, c_ast.FuncDef):
            self.to_dot(node.decl, dot, node_id)
            self.to_dot(node.body, dot, node_id)
            for param in node.param_decls or []:
                self.to_dot(param, dot, node_id)
        elif isinstance(node, c_ast.Compound):
            for item in node.block_items or []:
                self.to_dot(item, dot, node_id)
        elif isinstance(node, c_ast.If):
            self.to_dot(node.cond, dot, node_id)
            self.to_dot(node.iftrue, dot, node_id)
            if node.iffalse:
                self.to_dot(node.iffalse, dot, node_id)
        else:
            for child_name, child in node.children():
                if isinstance(child, list):
                    for c in child:
                        self.to_dot(c, dot, node_id)
                elif child is not None:
                    self.to_dot(child, dot, node_id)

    def filter_and_convert(self, node):
        """Filter typedefs and convert to DOT."""
        dot = graphviz.Digraph(comment='AST Visualization', format='png')
        if isinstance(node, c_ast.FileAST):
            for child in node.ext:
                if isinstance(child, c_ast.FuncDef):  # Only include FuncDef
                    self.to_dot(child, dot)
        return dot

def preprocess_code(code):
    """Preprocess C code using clang -E with pycparser's fake headers."""
    try:
        fake_include_path = os.path.join(os.path.dirname(pycparser.__file__), 'fake_libc_include')
        if not os.path.exists(fake_include_path):
            raise FileNotFoundError(f"fake_libc_include not found at {fake_include_path}")
    except FileNotFoundError as e:
        return None, str(e)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        result = subprocess.run(
            ['clang', '-E', '-P', '-nostdinc', '-I', fake_include_path, temp_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        preprocessed_code = result.stdout
        error = None
    except subprocess.CalledProcessError as e:
        preprocessed_code = None
        error = f"Preprocessing failed: {e.stderr}"
    finally:
        os.unlink(temp_file_path)

    return preprocessed_code, error

def parse_code(code):
    """Parse preprocessed C code into an AST and convert to Graphviz image."""
    preprocessed_code, preprocess_error = preprocess_code(code)
    if preprocess_error:
        return {'error': preprocess_error}

    try:
        parser = c_parser.CParser()
        ast = parser.parse(preprocessed_code, filename='<none>')
        converter = ASTConverter()
        dot = converter.filter_and_convert(ast)

        # Debug: Print the DOT source to verify
        print("DOT Source:")
        print(dot.source)

        # Save DOT file to a temporary location
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as temp_dot:
            temp_dot.write(dot.source)
            dot_path = temp_dot.name

        # Render DOT to PNG
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_image:
            image_path = temp_image.name
            # Use subprocess to call dot directly for better control
            result = subprocess.run(['dot', '-Tpng', dot_path, '-o', image_path], check=True, capture_output=True, text=True)
            print("Dot command output:", result.stdout)  # Debug: Log dot command output
            print("Dot command errors:", result.stderr)  # Debug: Log any errors
            # Read the PNG file
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            # Clean up files
            os.unlink(dot_path)
            os.unlink(image_path)

        return {'image': f'data:image/png;base64,{image_data}'}
    except Exception as e:
        return {'error': f"Parsing or rendering failed: {str(e)}"}

@app.route('/parse', methods=['POST'])
def parse():
    """API endpoint to parse C code and return its Graphviz image."""
    data = request.get_json()
    code = data.get('code', '')
    if not code.strip():
        return jsonify({'error': 'No code provided'})
    result = parse_code(code)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='127.0.0.1')