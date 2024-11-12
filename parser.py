import sys
import json
import re

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # List of tokens from the lexer
        self.pos = 0  # Position in the token list

    def current_token(self):
        # Returns the current token, or None if end of list
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, expected_type, expected_value=None):
        # Check if the current token matches the expected type and optional value
        token = self.current_token()
        if token and token[0] == expected_type and (expected_value is None or token[1] == expected_value):
            self.pos += 1  # Move to the next token
            return token
        return None

    def parse(self):
        # Parse the program and return the AST
        return self.parse_program()

    def parse_program(self):
        statements = []
        while self.current_token() is not None:
            statements.append(self.parse_statement())
        return {"Program": statements}

    # Parsing individual statements based on grammar

    def parse_statement(self):
        token_type, value = self.current_token()
        if token_type == 'KEYWORD' and value == 'declare':
            return self.parse_declaration()
        elif token_type == 'IDENTIFIER':
            return self.parse_assignment()
        elif token_type == 'KEYWORD' and value == 'if':
            return self.parse_if_statement()
        elif token_type == 'KEYWORD' and value == 'do':
            return self.parse_do_until_statement()
        elif token_type == 'KEYWORD' and value == 'loop':
            return self.parse_loop_statement()
        elif token_type == 'KEYWORD' and value == 'output':
            return self.parse_output_statement()
        elif token_type == 'KEYWORD' and value == 'def':
            return self.parse_function()  # Handle function definitions
        elif token_type == 'KEYWORD' and value == 'return':
            return self.parse_return_statement()  # Handle return statements
        else:
            raise SyntaxError(f"Unexpected token: {token_type} {value}")

    def parse_declaration(self):
        self.match("KEYWORD", "declare")
        identifier = self.match("IDENTIFIER")
        self.match("OPERATOR", "<-")
        expression = self.parse_expression()
        return {"Declaration": {"Identifier": identifier[1], "Expression": expression}}

    def parse_assignment(self):
        identifier = self.match("IDENTIFIER")
        self.match("OPERATOR", "<-")
        expression = self.parse_expression()
        return {"Assignment": {"Identifier": identifier[1], "Expression": expression}}

    def parse_if_statement(self):
        self.match("KEYWORD", "if")
        self.match("LPAR")
        condition = self.parse_condition()
        self.match("RPAR")
        then_block = self.parse_block()

        # Check for optional else clause
        else_block = None
        if self.match("KEYWORD", "else"):
            else_block = self.parse_block()

        return {"IfStatement": {"Condition": condition, "Then": then_block, "Else": else_block}}

    def parse_do_until_statement(self):
        self.match("KEYWORD", "do")
        block = self.parse_block()
        self.match("KEYWORD", "until")
        condition = self.parse_condition()
        return {"DoUntilStatement": {"Block": block, "Condition": condition}}

    def parse_loop_statement(self):
        self.match("KEYWORD", "loop")
        expression = self.parse_expression()
        block = self.parse_block()
        return {"LoopStatement": {"Expression": expression, "Block": block}}

    def parse_output_statement(self):
        self.match("KEYWORD", "output")
        string_literal = self.match("STRINGLITERAL")
        return {"OutputStatement": {"StringLiteral": string_literal[1]}}

    def parse_function(self):
        # Match the "def" keyword
        self.match("KEYWORD", "def")
        # Get the function name
        function_name = self.match("IDENTIFIER")
        # Match the opening parenthesis
        self.match("LPAR")
        # Parse the parameter list
        parameters = self.parse_parameter_list()
        # Match the closing parenthesis
        self.match("RPAR")
        # Parse the function body
        body = self.parse_block()
        
        return {
            "Function": {
                "Name": function_name[1],
                "Parameters": parameters,
                "Body": body
            }
        }

    def parse_parameter_list(self):
        # Parse parameters within the function definition
        parameters = []
        if self.current_token()[0] == "IDENTIFIER":
            parameters.append(self.match("IDENTIFIER")[1])
            while self.current_token() and self.current_token()[0] == "COMMA":
                self.match("COMMA")
                parameters.append(self.match("IDENTIFIER")[1])
        return parameters

    def parse_return_statement(self):
        self.match("KEYWORD", "return")
        expression = self.parse_expression()
        return {"Return": {"Expression": expression}}

    # Parsing blocks, conditions, expressions, terms, and factors

    def parse_block(self):
        self.match("LBRACE")
        statements = []
        while self.current_token() and self.current_token()[0] != "RBRACE":
            statements.append(self.parse_statement())
        self.match("RBRACE")
        return {"Block": statements}

    def parse_condition(self):
        left = self.parse_expression()
        operator = self.match("OPERATOR")
        right = self.parse_expression()
        return {"Condition": {"Left": left, "Operator": operator[1], "Right": right}}

    def parse_expression(self):
        # Parse a term and then handle additional "+" or "-" expressions
        left = self.parse_term()
        while self.current_token() and self.current_token()[1] in ["+", "-"]:
            operator = self.match("OPERATOR")
            right = self.parse_term()
            left = {"Expression": {"Left": left, "Operator": operator[1], "Right": right}}
        return left

    def parse_term(self):
        # Parse a factor and then handle additional "*" or "/" expressions
        left = self.parse_factor()
        while self.current_token() and self.current_token()[1] in ["*", "/"]:
            operator = self.match("OPERATOR")
            right = self.parse_factor()
            left = {"Term": {"Left": left, "Operator": operator[1], "Right": right}}
        return left

    def parse_factor(self):
        token = self.current_token()
        if token is None:
            raise SyntaxError("Unexpected end of input while parsing a factor")
        if token[0] == "IDENTIFIER":
            return {"Identifier": self.match("IDENTIFIER")[1]}
        elif token[0] == "INTLITERAL":
            return {"Literal": int(self.match("INTLITERAL")[1])}
        elif token[0] == "STRINGLITERAL":
            return {"StringLiteral": self.match("STRINGLITERAL")[1]}
        elif self.match("LPAR"):
            expr = self.parse_expression()
            self.match("RPAR")
            return expr
        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")

# Main block to execute the parser as a script
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parser.py [tokens_file.txt]")
        sys.exit(1)

    tokens_file = sys.argv[1]

    # Read tokens from file
    try:
        tokens = []
        with open(tokens_file, 'r') as f:
            for line in f:
                match = re.match(r"<([^,]+),\s*(.+)>", line.strip())
                if match:
                    token_type = match.group(1)
                    token_value = match.group(2).strip('"')
                    tokens.append((token_type, token_value))
                else:
                    print("Error: Incorrect token format in tokens file.")
                    sys.exit(1)

    except FileNotFoundError:
        print(f"Error: File '{tokens_file}' not found!")
        sys.exit(1)

    # Initialize and run the parser
    parser = Parser(tokens)
    ast = parser.parse()

    # Output the AST in JSON format for readability
    print(json.dumps(ast, indent=2))
