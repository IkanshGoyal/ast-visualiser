class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return self.value

class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 0  # Start at 0 to match character positions
        self.keywords = {
            'int', 'char', 'float', 'double', 'void', 'if', 'else', 'while', 'for',
            'return', 'struct', 'typedef', 'switch', 'case', 'default', 'break', 'continue'
        }
        self.operators = {
            '+', '-', '*', '/', '%', '=', '==', '!=', '<', '>', '<=', '>=', '&&', '||',
            '!', '&', '|', '^', '<<', '>>', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=',
            '<<=', '>>=', '->', '.', '++', '--'
        }

    def tokenize(self):
        tokens = []
        while self.pos < len(self.code):
            char = self.code[self.pos]
            
            # Skip whitespace
            if char.isspace():
                if char == '\n':
                    self.line += 1
                    self.column = 0
                else:
                    self.column += 1
                self.pos += 1
                continue
            
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                start_column = self.column
                value = self._read_identifier()
                token_type = 'KEYWORD' if value in self.keywords else 'IDENTIFIER'
                tokens.append(Token(token_type, value, self.line, start_column))
                continue
            
            # Numbers
            if char.isdigit():
                start_column = self.column
                value = self._read_number()
                tokens.append(Token('NUMBER', value, self.line, start_column))
                continue
            
            # Operators and punctuation
            if char in self.operators or char in '();,{}[]':
                start_column = self.column
                value = self._read_operator_or_punctuation()
                token_type = 'OPERATOR' if value in self.operators else 'PUNCTUATION'
                tokens.append(Token(token_type, value, self.line, start_column))
                continue
            
            # Strings
            if char == '"':
                start_column = self.column
                value = self._read_string()
                tokens.append(Token('STRING', value, self.line, start_column))
                continue
            
            # Handle unexpected characters
            raise ValueError(f"Unexpected character '{char}' at line {self.line}, column {self.column}")
        
        tokens.append(Token('EOF', '', self.line, self.column))
        return tokens

    def _read_identifier(self):
        start = self.pos
        while self.pos < len(self.code) and (self.code[self.pos].isalnum() or self.code[self.pos] == '_'):
            self.pos += 1
            self.column += 1
        return self.code[start:self.pos]

    def _read_number(self):
        start = self.pos
        while self.pos < len(self.code) and (self.code[self.pos].isdigit() or self.code[self.pos] == '.'):
            self.pos += 1
            self.column += 1
        return self.code[start:self.pos]

    def _read_operator_or_punctuation(self):
        start = self.pos
        # Only look for multi-character operators, not punctuation
        if self.pos + 1 < len(self.code):
            candidate = self.code[self.pos:self.pos + 2]
            if candidate in self.operators:
                self.pos += 2
                self.column += 2
                return candidate
        # Single character operator or punctuation
        char = self.code[self.pos]
        self.pos += 1
        self.column += 1
        return char

    def _read_string(self):
        start = self.pos
        self.pos += 1  # Skip opening quote
        self.column += 1
        while self.pos < len(self.code):
            if self.code[self.pos] == '"' and self.code[self.pos - 1] != '\\':
                self.pos += 1
                self.column += 1
                return self.code[start:self.pos]
            if self.code[self.pos] == '\n':
                self.line += 1
                self.column = 0
            else:
                self.column += 1
            self.pos += 1
        raise ValueError(f"Unterminated string at line {self.line}, column {self.column}")