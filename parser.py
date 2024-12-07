import sys
import json
import re


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # List of tokens from the lexer
        self.pos = 0  # Position in the token list

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, expected_type, expected_value=None):
        token = self.current_token()
        if token and token[0] == expected_type and (expected_value is None or token[1] == expected_value):
            self.pos += 1
            return token
        return None

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        statements = []
        while self.current_token() is not None:
            statements.append(self.parse_statement())
        return {"Program": statements}

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
            return self.parse_function()
        elif token_type == 'KEYWORD' and value == 'return':
            return self.parse_return_statement()
        else:
            raise SyntaxError(f"Unexpected token: {token_type} {
                              value} at position {self.pos}")

    def parse_declaration(self):
        self.match("KEYWORD", "declare")
        identifier = self.match("IDENTIFIER")
        if not identifier:
            raise SyntaxError(
                f"Expected identifier after 'declare' at position {self.pos}")
        if not self.match("OPERATOR", "<-"):
            raise SyntaxError(
                f"Expected '<-' after identifier '{identifier[1]}', but found '{self.current_token()[1]}'")
        expression = self.parse_expression()
        return {"Declaration": {"Identifier": identifier[1], "Expression": expression}}

    def parse_assignment(self):
        identifier = self.match("IDENTIFIER")
        if not self.match("OPERATOR", "<-"):
            raise SyntaxError(
                f"Expected '<-' after identifier '{identifier[1]}', but found '{self.current_token()[1]}'")
        expression = self.parse_expression()
        return {"Assignment": {"Identifier": identifier[1], "Expression": expression}}

    def parse_if_statement(self):
        """
        Parses an 'if' statement, ensuring parentheses for the condition are explicitly matched.
        """
        if not self.match("KEYWORD", "if"):  # Match the 'if' keyword
            raise SyntaxError(f"Expected 'if' at position {
                              self.pos}, found {self.current_token()}")

        if not self.match("LPAR"):  # Match the opening '(' of the condition
            raise SyntaxError(f"Expected '(' at the start of condition at position {
                              self.pos}, found {self.current_token()}")

        condition = self.parse_condition()  # Parse the condition

        if not self.match("RPAR"):  # Match the closing ')'
            raise SyntaxError(f"Expected ')' after condition at position {
                              self.pos}, found {self.current_token()}")

        then_block = self.parse_block()  # Parse the 'then' block

        else_block = None
        if self.match("KEYWORD", "else"):  # Check for 'else'
            else_block = self.parse_block()

        return {"IfStatement": {"Condition": condition, "Then": then_block, "Else": else_block}}

    def parse_condition(self):
        """
        Parses a condition in the form: <expression> <relational_operator> <expression>.
        Assumes parentheses are handled by the caller.
        """
        left = self.parse_expression()  # Parse the left-hand side of the condition

        operator = self.match("OPERATOR")  # Match the relational operator
        if not operator or operator[1] not in ["==", "!=", "<", ">", "<=", ">="]:
            raise SyntaxError(f"Expected a relational operator after expression at position {
                              self.pos}, found {self.current_token()}")

        right = self.parse_expression()  # Parse the right-hand side of the condition

        return {"Left": left, "Operator": operator[1], "Right": right}

    def parse_do_until_statement(self):
        """
        Parses a 'do-until' statement, ensuring parentheses for the condition are explicitly matched.
        """
        self.match("KEYWORD", "do")  # Match 'do'
        block = self.parse_block()  # Parse the block inside 'do'

        if not self.match("KEYWORD", "until"):  # Match 'until'
            raise SyntaxError(f"Expected 'until' after 'do' block at position {
                              self.pos}, found {self.current_token()}")

        if not self.match("LPAR"):  # Match the opening '(' of the condition
            raise SyntaxError(f"Expected '(' at the start of condition at position {
                              self.pos}, found {self.current_token()}")

        condition = self.parse_condition()  # Parse the condition

        if not self.match("RPAR"):  # Match the closing ')'
            raise SyntaxError(f"Expected ')' to close condition at position {
                              self.pos}, found {self.current_token()}")

        return {"DoUntilStatement": {"Block": block, "Condition": condition}}

    def parse_loop_statement(self):
        """
        Parses a loop statement in the form:
        loop <identifier_or_literal> { <block> }
        """
        self.match("KEYWORD", "loop")  # Match 'loop'
        iteration_count = self.parse_factor()  # Parse an identifier or literal
        block = self.parse_block()  # Parse the block inside the loop
        return {"LoopStatement": {"IterationCount": iteration_count, "Block": block}}

    def parse_output_statement(self):
        self.match("KEYWORD", "output")
        expression = self.parse_expression()
        return {"OutputStatement": expression}

    def parse_function(self):
        self.match("KEYWORD", "def")
        function_name = self.match("IDENTIFIER")
        if not function_name:
            raise SyntaxError(
                f"Expected function name after 'def' at position {self.pos}")
        if not self.match("LPAR"):
            raise SyntaxError(f"Expected '(' after function name '{
                              function_name[1]}' at position {self.pos}")
        parameters = self.parse_parameter_list()
        if not self.match("RPAR"):
            raise SyntaxError(f"Expected ')' after parameter list at position {
                              self.pos}")
        body = self.parse_block()
        return {"Function": {"Name": function_name[1], "Parameters": parameters, "Body": body}}

    def parse_parameter_list(self):
        parameters = []
        if self.current_token() and self.current_token()[0] == "IDENTIFIER":
            parameters.append(self.match("IDENTIFIER")[1])
            while self.current_token() and self.current_token()[0] == "COMMA":
                self.match("COMMA")
                parameters.append(self.match("IDENTIFIER")[1])
        return parameters

    def parse_return_statement(self):
        self.match("KEYWORD", "return")
        expression = self.parse_expression()
        return {"Return": {"Expression": expression}}

    def parse_block(self):
        """
        Parses a block in the form: { <statements> }
        """
        if not self.match("LBRACE"):  # Match the '{' token
            raise SyntaxError(f"Expected '{{' to start block at position {
                              self.pos}, but found {self.current_token()}")
        statements = []
        # Loop until '}' is encountered
        while self.current_token() and self.current_token()[0] != "RBRACE":
            statements.append(self.parse_statement())
        if not self.match("RBRACE"):  # Match the '}' token
            raise SyntaxError(f"Expected '}}' to close block at position {
                              self.pos}")
        return statements

    def parse_expression(self):
        """
        Parses expressions with operators (+, -) and ensures correct precedence.
        """
        left = self.parse_term()  # Parse the left-hand term
        while self.current_token() and self.current_token()[1] in ["+", "-"]:
            operator = self.match("OPERATOR")
            right = self.parse_term()  # Parse the right-hand term
            left = {"Left": left, "Operator": operator[1], "Right": right}
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current_token() and self.current_token()[1] in ["*", "/"]:
            operator = self.match("OPERATOR")
            right = self.parse_factor()
            left = {"Left": left, "Operator": operator[1], "Right": right}
        return left

    def parse_factor(self):
        """
        Parses a single factor, such as a literal, identifier, or parenthesized expression.
        """
        token = self.current_token()
        if token is None:
            raise SyntaxError("Unexpected end of input while parsing a factor")

        if token[0] == "IDENTIFIER":
            identifier = self.match("IDENTIFIER")[1]
            if self.match("LPAR"):
                arguments = self.parse_argument_list()
                if not self.match("RPAR"):
                    raise SyntaxError(f"Expected ')' after function arguments at position {
                                      self.pos}")
                return {"FunctionCall": {"Name": identifier, "Arguments": arguments}}
            return {"Identifier": identifier}

        elif token[0] == "INTLITERAL":
            return {"Literal": int(self.match("INTLITERAL")[1])}

        elif token[0] == "STRINGLITERAL":
            return {"StringLiteral": self.match("STRINGLITERAL")[1]}

        elif self.match("LPAR"):  # Parenthesized expression
            expr = self.parse_expression()
            if not self.match("RPAR"):
                raise SyntaxError(f"Expected ')' to close expression at position {
                                  self.pos}")
            return expr

        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")

    def parse_argument_list(self):
        """
        Parses a comma-separated list of arguments in a function call.
        """
        arguments = []
        while self.current_token() and self.current_token()[0] != "RPAR":
            arguments.append(self.parse_expression())
            if not self.match("COMMA"):
                break
        return arguments


# Main block to execute the parser as a script
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parser.py [tokens_file.txt]")
        sys.exit(1)

    tokens_file = sys.argv[1]

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

    parser = Parser(tokens)
    try:
        ast = parser.parse()
        print(json.dumps(ast, indent=2))  # AST output only
    except SyntaxError as e:
        print(f"An error occurred during parsing: {e}")
