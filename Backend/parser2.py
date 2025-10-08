import ply.yacc as yacc
from Backend.lexer2 import tokens

class ASTNode:
    def to_dict(self):
        return {'type': self.__class__.__name__}

class Program(ASTNode):
    def __init__(self, body):
        self.body = body
    def to_dict(self):
        return {'type': 'Program', 'body': [stmt.to_dict() for stmt in self.body]}

class FunctionDef(ASTNode):
    def __init__(self, return_type, name, params, body):
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body
    def to_dict(self):
        return {
            'type': 'FunctionDef',
            'return_type': self.return_type,
            'name': self.name,
            'params': [p.to_dict() for p in self.params],
            'body': [stmt.to_dict() for stmt in self.body]
        }

class Param(ASTNode):
    def __init__(self, type, name):
        self.type = type
        self.name = name
    def to_dict(self):
        return {'type': 'Param', 'type_name': self.type, 'name': self.name}

class IfStmt(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def to_dict(self):
        return {
            'type': 'IfStmt',
            'condition': self.condition.to_dict(),
            'then_branch': [stmt.to_dict() for stmt in self.then_branch],
            'else_branch': [stmt.to_dict() for stmt in self.else_branch] if self.else_branch else None
        }

class WhileStmt(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def to_dict(self):
        return {
            'type': 'WhileStmt',
            'condition': self.condition.to_dict(),
            'body': [stmt.to_dict() for stmt in self.body]
        }

class ForStmt(ASTNode):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
    def to_dict(self):
        return {
            'type': 'ForStmt',
            'init': self.init.to_dict() if self.init else None,
            'condition': self.condition.to_dict() if self.condition else None,
            'update': self.update.to_dict() if self.update else None,
            'body': [stmt.to_dict() for stmt in self.body]
        }

class ReturnStmt(ASTNode):
    def __init__(self, value):
        self.value = value
    def to_dict(self):
        return {'type': 'ReturnStmt', 'value': self.value.to_dict() if self.value else None}

class VarDecl(ASTNode):
    def __init__(self, type, name, init=None):
        self.type = type
        self.name = name
        self.init = init
    def to_dict(self):
        return {
            'type': 'VarDecl',
            'type_name': self.type,
            'name': self.name,
            'init': self.init.to_dict() if self.init else None
        }

class Assignment(ASTNode):
    def __init__(self, target, value):
        self.target = target
        self.value = value
    def to_dict(self):
        return {'type': 'Assignment', 'target': self.target.to_dict(), 'value': self.value.to_dict()}

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def to_dict(self):
        return {'type': 'BinOp', 'op': self.op, 'left': self.left.to_dict(), 'right': self.right.to_dict()}

class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
    def to_dict(self):
        return {'type': 'UnaryOp', 'op': self.op, 'operand': self.operand.to_dict()}

class Number(ASTNode):
    def __init__(self, value):
        self.value = value
    def to_dict(self):
        return {'type': 'Number', 'value': self.value}

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name
    def to_dict(self):
        return {'type': 'Identifier', 'name': self.name}

def p_program(p):
    '''program : statement_list'''
    p[0] = Program(p[1])

def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''statement : declaration
                 | assignment
                 | function_def
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | return_stmt'''
    p[0] = p[1]

def p_declaration(p):
    '''declaration : type ID SEMICOLON
                   | type ID EQUALS expression SEMICOLON'''
    if len(p) == 4:
        p[0] = VarDecl(p[1], p[2])
    else:
        p[0] = VarDecl(p[1], p[2], p[4])

def p_type(p):
    '''type : INT
            | CHAR
            | VOID'''
    p[0] = p[1]

def p_assignment(p):
    'assignment : ID EQUALS expression SEMICOLON'
    p[0] = Assignment(Identifier(p[1]), p[3])

def p_function_def(p):
    'function_def : type ID LPAREN param_list RPAREN LBRACE statement_list RBRACE'
    p[0] = FunctionDef(p[1], p[2], p[4], p[7])

def p_param_list(p):
    '''param_list : 
                  | params'''
    p[0] = p[1] if len(p) > 1 else []

def p_params(p):
    '''params : param
              | params COMMA param'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_param(p):
    'param : type ID'
    p[0] = Param(p[1], p[2])

def p_if_stmt(p):
    '''if_stmt : IF LPAREN expression RPAREN LBRACE statement_list RBRACE
               | IF LPAREN expression RPAREN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE'''
    if len(p) == 8:
        p[0] = IfStmt(p[3], p[6])
    else:
        p[0] = IfStmt(p[3], p[6], p[10])

def p_while_stmt(p):
    'while_stmt : WHILE LPAREN expression RPAREN LBRACE statement_list RBRACE'
    p[0] = WhileStmt(p[3], p[6])

def p_for_stmt(p):
    'for_stmt : FOR LPAREN expression_opt SEMICOLON expression_opt SEMICOLON expression_opt RPAREN LBRACE statement_list RBRACE'
    p[0] = ForStmt(p[3], p[5], p[7], p[10])

def p_expression_opt(p):
    '''expression_opt : 
                      | expression'''
    p[0] = p[1] if len(p) > 1 else None

def p_return_stmt(p):
    '''return_stmt : RETURN expression SEMICOLON
                   | RETURN SEMICOLON'''
    if len(p) == 4:
        p[0] = ReturnStmt(p[2])
    else:
        p[0] = ReturnStmt(None)

def p_expression(p):
    '''expression : expression PLUS term
                  | expression MINUS term
                  | expression TIMES term
                  | expression DIVIDE term
                  | expression MOD term
                  | expression LESS term
                  | expression GREATER term
                  | expression LESSEQ term
                  | expression GREATEREQ term
                  | expression EQUALTO term
                  | expression NOTEQUAL term
                  | expression AND term
                  | expression OR term
                  | term'''
    if len(p) == 4:
        p[0] = BinOp(p[1], p[2], p[3])
    else:
        p[0] = p[1]

def p_term(p):
    '''term : NOT term
            | factor'''
    if len(p) == 3:
        p[0] = UnaryOp(p[1], p[2])
    else:
        p[0] = p[1]

def p_factor(p):
    '''factor : NUMBER
              | ID
              | LPAREN expression RPAREN'''
    if len(p) == 2:
        if p[1].isdigit():
            p[0] = Number(int(p[1]))
        else:
            p[0] = Identifier(p[1])
    else:
        p[0] = p[2]

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at '{p.value}'")
    else:
        raise SyntaxError("Syntax error at EOF")

parser = yacc.yacc()

def parse_code(code):
    try:
        result = parser.parse(code)
        return result.to_dict()
    except SyntaxError as e:
        return {'error': str(e)}

if __name__ == "__main__":
    code = '''
    int main() {
        int x = 0;
        if (x < 5) {
            x = x + 1;
        }
        return x;
    }
    '''
    ast = parse_code(code)
    import json
    print(json.dumps(ast, indent=2))