import ply.lex as lex

tokens = (
    'INT', 'CHAR', 'VOID', 'IF', 'ELSE', 'WHILE', 'FOR', 'RETURN',
    'ID', 'NUMBER', 'STRING',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'EQUALS',
    'LESS', 'GREATER', 'LESSEQ', 'GREATEREQ', 'EQUALTO', 'NOTEQUAL',
    'AND', 'OR', 'NOT',
    'SEMICOLON', 'COMMA', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET'
)

t_INT = r'int'
t_CHAR = r'char'
t_VOID = r'void'
t_IF = r'if'
t_ELSE = r'else'
t_WHILE = r'while'
t_FOR = r'for'
t_RETURN = r'return'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_EQUALS = r'='
t_LESS = r'<'
t_GREATER = r'>'
t_LESSEQ = r'<='
t_GREATEREQ = r'>='
t_EQUALTO = r'=='
t_NOTEQUAL = r'!='
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_SEMICOLON = r';'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_NUMBER = r'\d+'
t_STRING = r'"[^"]*"'
t_ignore = ' \t\n'


# Error handling
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Tokenization function
def tokenize(code):
    lexer.input(code)
    tokens_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append((tok.type, tok.value))
    return tokens_list

# Test
if __name__ == "__main__":
    code = 'int main() { if (x < 5) { return x + 1; } }'
    print(tokenize(code))