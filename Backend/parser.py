from lexer import Token

class ASTNode:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []

    def __str__(self):
        return f"{self.node_type}: {self.value}" if self.value else self.node_type

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        root = ASTNode("Program")
        while self._peek().type != 'EOF':
            node = self._parse_top_level()
            if node:
                root.children.append(node)
        return root

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else Token('EOF', '', 0, 0)

    def _consume(self, expected_type=None, expected_value=None):
        token = self._peek()
        if expected_type and token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type} at line {token.line}")
        if expected_value and token.value != expected_value:
            raise ValueError(f"Expected '{expected_value}', got '{token.value}' at line {token.line}")
        self.pos += 1
        return token

    def _parse_top_level(self):
        token = self._peek()
        if token.type == 'KEYWORD' and token.value in {'int', 'char', 'float', 'double', 'void'}:
            if (self.pos + 2 < len(self.tokens) and 
                self.tokens[self.pos + 1].type == 'IDENTIFIER' and 
                self.tokens[self.pos + 2].value == '('):
                return self._parse_function()
            else:
                return self._parse_declaration()
        self.pos += 1
        return None

    def _parse_function(self):
        return_type = self._consume('KEYWORD').value
        name = self._consume('IDENTIFIER').value
        self._consume('PUNCTUATION', '(')
        params = []
        if self._peek().value == 'void':
            self._consume('KEYWORD', 'void')
        elif self._peek().value != ')':
            while True:
                param_type = self._consume('KEYWORD').value
                param_name = self._consume('IDENTIFIER').value
                params.append(ASTNode("Parameter", value=f"{param_type} {param_name}"))
                if self._peek().value == ')':
                    break
                self._consume('PUNCTUATION', ',')
        self._consume('PUNCTUATION', ')')
        body = self._parse_block()
        return ASTNode("Function", value=f"{return_type} {name}", children=params + [body])

    def _parse_declaration(self):
        type_token = self._consume('KEYWORD')
        name = self._consume('IDENTIFIER').value
        if self._peek().value == '=':
            self._consume('OPERATOR', '=')
            value = self._parse_expression()
            self._consume('PUNCTUATION', ';')
            return ASTNode("Declaration", value=f"{type_token.value} {name}", children=[value])
        self._consume('PUNCTUATION', ';')
        return ASTNode("Declaration", value=f"{type_token.value} {name}")

    def _parse_block(self):
        self._consume('PUNCTUATION', '{')
        block = ASTNode("Block")
        while self._peek().value != '}':
            stmt = self._parse_statement()
            if stmt:
                block.children.append(stmt)
        self._consume('PUNCTUATION', '}')
        return block

    def _parse_statement(self):
        token = self._peek()
        if token.type == 'KEYWORD':
            if token.value == 'if':
                return self._parse_if()
            elif token.value == 'while':
                return self._parse_while()
            elif token.value == 'for':
                return self._parse_for()
            elif token.value == 'return':
                return self._parse_return()
            elif token.value in {'int', 'char', 'float', 'double', 'void'}:
                return self._parse_declaration()
        elif token.type == 'PUNCTUATION' and token.value == '{':
            return self._parse_block()
        elif token.type == 'IDENTIFIER':
            return self._parse_expression_statement()
        self.pos += 1
        return None

    def _parse_if(self):
        self._consume('KEYWORD', 'if')
        self._consume('PUNCTUATION', '(')
        condition = self._parse_expression()
        self._consume('PUNCTUATION', ')')
        then_branch = self._parse_statement()
        else_branch = None
        if self._peek().value == 'else':
            self._consume('KEYWORD', 'else')
            else_branch = self._parse_statement()
        node = ASTNode("If", children=[condition, then_branch])
        if else_branch:
            node.children.append(else_branch)
        return node

    def _parse_while(self):
        self._consume('KEYWORD', 'while')
        self._consume('PUNCTUATION', '(')
        condition = self._parse_expression()
        self._consume('PUNCTUATION', ')')
        body = self._parse_statement()
        return ASTNode("While", children=[condition, body])

    def _parse_for(self):
        self._consume('KEYWORD', 'for')
        self._consume('PUNCTUATION', '(')
        init = self._parse_expression_statement()
        condition = self._parse_expression()
        self._consume('PUNCTUATION', ';')
        update = self._parse_expression()
        self._consume('PUNCTUATION', ')')
        body = self._parse_statement()
        return ASTNode("For", children=[init, condition, update, body])

    def _parse_return(self):
        self._consume('KEYWORD', 'return')
        expr = self._parse_expression() if self._peek().value != ';' else None
        self._consume('PUNCTUATION', ';')
        return ASTNode("Return", children=[expr] if expr else [])

    def _parse_expression_statement(self):
        expr = self._parse_expression()
        self._consume('PUNCTUATION', ';')
        return ASTNode("ExpressionStatement", children=[expr])

    def _parse_expression(self):
        token = self._peek()
        if token.type == 'IDENTIFIER':
            # Check if this is a function call (IDENTIFIER followed by '(')
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].value == '(':
                return self._parse_function_call()
            # Check if this is an assignment
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].value == '=':
                return self._parse_assignment()
            # Check for unary operators like ++ or --
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].value in ('++', '--'):
                return self._parse_unary_op()
            # Otherwise, it's a simple identifier
            self.pos += 1
            left = ASTNode("IDENTIFIER", value=token.value)
        elif token.type in ('NUMBER', 'STRING'):
            self.pos += 1
            left = ASTNode(token.type, value=token.value)
        else:
            return None

        # Check for binary operator
        if self._peek().type == 'OPERATOR' and self._peek().value not in ('++', '--'):
            return self._parse_binary_op(left)
        return left

    def _parse_function_call(self):
        name = self._consume('IDENTIFIER').value
        self._consume('PUNCTUATION', '(')
        args = []
        # Parse arguments (comma-separated expressions)
        while self._peek().value != ')':
            arg = self._parse_expression()
            if arg:
                args.append(arg)
            if self._peek().value == ',':
                self._consume('PUNCTUATION', ',')
            elif self._peek().value != ')':
                raise ValueError(f"Expected ',' or ')', got '{self._peek().value}' at line {self._peek().line}")
        self._consume('PUNCTUATION', ')')
        return ASTNode("FunctionCall", value=name, children=args)

    def _parse_assignment(self):
        var = self._consume('IDENTIFIER').value
        self._consume('OPERATOR', '=')
        value = self._parse_expression()
        return ASTNode("Assignment", value=var, children=[value])

    def _parse_unary_op(self):
        var = self._consume('IDENTIFIER').value
        op = self._consume('OPERATOR').value  # ++ or --
        return ASTNode("UnaryOp", value=op, children=[ASTNode("IDENTIFIER", value=var)])

    def _parse_binary_op(self, left):
        op = self._consume('OPERATOR').value
        right = self._parse_expression()
        if right is None:
            raise ValueError(f"Expected expression after operator '{op}' at line {self._peek().line}")
        return ASTNode("BinaryOp", value=op, children=[left, right])