# Custom C Code AST Visualizer

This project provides a web-based tool for visualizing the Abstract Syntax Tree (AST) of C code. It features a Flask backend that parses C source code, generates its AST, and renders a visual representation using Graphviz. The tool is designed for educational purposes, debugging, and understanding C code structure.

## Features

- **C Code Parsing:** Parses C code using a custom lexer and parser.
- **AST Generation:** Builds an AST from the parsed tokens.
- **AST Visualization:** Renders the AST as a PNG image using Graphviz.
- **REST API:** Exposes a `/parse` endpoint for submitting C code and receiving tokens, AST text, and a visual image.
- **Preprocessor Filtering:** Removes C preprocessor directives before parsing.
- **Cross-Origin Support:** Uses CORS for frontend-backend integration.

## How It Works

1. **Submit C Code:** Send a POST request to `/parse` with your C code in the JSON payload.
2. **Processing:** The backend filters preprocessor directives, tokenizes the code, parses it into an AST, and generates a DOT graph.
3. **Rendering:** The DOT graph is converted to a PNG image using Graphviz.
4. **Response:** The API returns the tokens, AST as text, and a base64-encoded PNG image.

## API Usage

**Endpoint:** `POST /parse`

**Payload:**
```json
{
  "code": "int main() { return 0; }"
}
```

**Response:**
```json
{
  "tokens": [...],
  "ast": "...",
  "image": "data:image/png;base64,..."
}
```

## Setup

1. **Install Dependencies:**
   - Python 3.x
   - Flask
   - Flask-CORS
   - Graphviz (system package and Python library)
2. **Run the Backend:**
   ```sh
   python Backend/main2.py
   ```
3. **Send Requests:** Use curl, Postman, or your frontend to interact with the API.

## Example

```sh
curl -X POST http://localhost:5050/parse \
     -H "Content-Type: application/json" \
     -d '{"code": "int main() { return 0; }"}'
```

## Project Structure

- `Backend/main2.py`: Flask backend with parsing and visualization logic.
- `lexer.py`, `parser.py`: Custom lexer and parser for C code.
- `ast.dot`, `ast-rendered.png`: Generated files for AST visualization.

## Notes

- Ensure Graphviz is installed and available in your system PATH.
- The backend removes preprocessor directives for simplicity.
- The AST visualizer is customizable for different C grammars.

## Author

Ikansh Goyal
