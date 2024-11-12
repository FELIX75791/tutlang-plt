import sys

class Scanner:
    def __init__(self):
        self.state = 'START'
        self.tokens = []
        self.current_char = ''

    def scan(self, code):
        i = 0
        start = 0
        self.state = 'START'
        self.tokens = []
        self.current_char = ''
        while i < len(code):
            self.current_char = code[i]

            # DFA State Transitions
            if self.state == 'START':
                if self.current_char.isspace():
                    i += 1  # Skip whitespace
                elif self.current_char.isalpha():  # Identifier or keyword starts with a letter
                    self.state = 'IDENTIFIER'
                    start = i  # Mark start of identifier
                    i += 1
                elif self.current_char.isdigit():  # Number starts with a digit
                    self.state = 'NUMBER'
                    start = i  # Mark start of number
                    i += 1
                elif self.current_char == '"':  # String literal starts with "
                    self.state = 'STRING'
                    start = i  # Mark start of string
                    i += 1
                elif self.current_char == '(':  # LPAR
                    self.tokens.append(('LPAR', '('))
                    i += 1
                elif self.current_char == ')':  # RPAR
                    self.tokens.append(('RPAR', ')'))
                    i += 1
                elif self.current_char == ',':  # COMMA
                    self.tokens.append(('COMMA', ','))
                    i += 1
                elif self.current_char == '{':  # LBRACE
                    self.tokens.append(('LBRACE', '{'))
                    i += 1
                elif self.current_char == '}':  # RBRACE
                    self.tokens.append(('RBRACE', '}'))
                    i += 1
                elif self.current_char in '+-*/<>=':  # Possible operator
                    self.state = 'OPERATOR'
                    start = i  # Mark start of operator
                    i += 1
                else:
                    print(f"Lexical error: Unexpected character '{
                          self.current_char}' at position {i}")
                    return

            # State for handling identifiers or keywords
            elif self.state == 'IDENTIFIER':
                if self.current_char.isalnum() or self.current_char == '_':
                    i += 1  # Continue reading identifier
                else:
                    identifier = code[start:i]
                    if identifier in {"declare", "def", "if", "else", "do", "until", "loop", "return", "output"}:
                        self.tokens.append(('KEYWORD', identifier))
                    else:
                        self.tokens.append(('IDENTIFIER', identifier))
                    self.state = 'START'  # Reinitialize state
                    start = i  # Reset start for the next token

            # State for handling numbers
            elif self.state == 'NUMBER':
                if self.current_char.isdigit():
                    i += 1  # Continue reading number
                else:
                    number = code[start:i]
                    self.tokens.append(('INTLITERAL', number))
                    self.state = 'START'  # Reinitialize state
                    start = i  # Reset start for the next token

            # State for handling string literals
            elif self.state == 'STRING':
                if self.current_char == '"':  # Closing quote
                    string_literal = code[start:i]
                    self.tokens.append(('STRINGLITERAL', string_literal))
                    self.state = 'START'  # Reinitialize state
                    i += 1  # Move past the closing quote
                    start = i  # Reset start for the next token
                elif i == len(code) - 1:  # If the string reaches the end without closing
                    print(
                        f"Lexical error: Unterminated string literal at position {start}")
                    return
                else:
                    i += 1  # Continue reading string literal

            # State for handling operators
            elif self.state == 'OPERATOR':
                # Multi-character operator
                if code[start:i+1] in {"==", "!=", "<=", ">=", "<-"}:
                    self.tokens.append(('OPERATOR', code[start:i+1]))
                    i += 1
                else:
                    self.tokens.append(('OPERATOR', code[start:i]))
                self.state = 'START'  # Reinitialize state
                start = i  # Reset start for the next token
                
        # After loop: Finalize any remaining tokens
        if self.state == 'IDENTIFIER':
            identifier = code[start:i]
            if identifier in {"declare", "def", "if", "else", "do", "until", "loop", "return", "output"}:
                self.tokens.append(('KEYWORD', identifier))
            else:
                self.tokens.append(('IDENTIFIER', identifier))
        elif self.state == 'NUMBER':
            number = code[start:i]
            self.tokens.append(('INTLITERAL', number))
        elif self.state == 'OPERATOR':
            self.tokens.append(('OPERATOR', code[start:i]))
        elif self.state == 'STRING':
            print(f"Lexical error: Unterminated string literal at position {start}")
            return
        
        return self.tokens


# Entry point of the lexer, now accepts an input file
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scanner.py [input_file.tut]")
        sys.exit(1)

    input_file = sys.argv[1]

    # Read the input file
    try:
        with open(input_file, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found!")
        sys.exit(1)

    # Create an instance of the Scanner
    scanner = Scanner()

    # Scan the code from the input file
    tokens = scanner.scan(code)

    # Output tokens in <Token Type, Token Value> format
    if tokens:
        for token in tokens:
            print(f"<{token[0]}, {token[1]}>")


'''
declare a <- 5
''',
'''
def factorial(n) {
    declare fact <- 1
    loop n {
        fact <- fact * n
        n <- n - 1
    }
    return fact
}
''',
'''
if (x == 10) {
    output "x is ten"
} else {
    output "x is not ten"
}
''',
'''
do {
    declare count <- 5
    output "Counting
} until count == 0
''',
'''
declare x <- 10
declare y <- x + 5
if x >= @ {
    x <- x - 2
}
'''
