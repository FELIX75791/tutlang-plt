import json
import sys


class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.indent_level = 0
        self.output_code = []
        self.constants = {}

    def generate(self):
        self._process_program(self.ast["Program"])
        return "\n".join(self.output_code)

    def _process_program(self, program):
        for statement in program:
            self._process_statement(statement)

    def _process_statement(self, statement):
        if "Declaration" in statement:
            self._process_declaration(statement["Declaration"])
        elif "Assignment" in statement:
            self._process_assignment(statement["Assignment"])
        elif "IfStatement" in statement:
            self._process_if_statement(statement["IfStatement"])
        elif "LoopStatement" in statement:
            self._process_loop_statement(statement["LoopStatement"])
        elif "OutputStatement" in statement:
            self._process_output_statement(statement["OutputStatement"])
        elif "Function" in statement:
            self._process_function(statement["Function"])
        elif "Return" in statement:
            self._process_return(statement["Return"])
        elif "DoUntilStatement" in statement:  # Handle DoUntilStatement
            self._process_do_until_statement(statement["DoUntilStatement"])
        else:
            raise ValueError("Unknown statement type.")

    def _process_assignment(self, assignment):
        identifier = assignment["Identifier"]
        expression = self._process_expression(
            assignment["Expression"], skip_constants_for={identifier}
        )

        # Update constant map if the expression is a literal
        if "Literal" in assignment["Expression"]:
            self.constants[identifier] = expression
        else:
            self.constants.pop(identifier, None)  # Remove if no longer constant

        self.output_code.append(f"{self._indent()}{identifier} = {expression}")

    def _process_declaration(self, declaration):
        identifier = declaration["Identifier"]
        expression = self._process_expression(
            declaration["Expression"], skip_constants_for={identifier}
        )

        # Update constant map if the expression is a literal
        if "Literal" in declaration["Expression"]:
            self.constants[identifier] = expression
        else:
            self.constants.pop(identifier, None)  # Remove if no longer constant

        self.output_code.append(f"{self._indent()}{identifier} = {expression}")

    def _process_if_statement(self, if_stmt):
        condition = self._process_expression(if_stmt["Condition"])
        self.output_code.append(f"{self._indent()}if {condition}:")
        self.indent_level += 1
        self._process_block(if_stmt["Then"])
        self.indent_level -= 1
        if "Else" in if_stmt:
            self.output_code.append(f"{self._indent()}else:")
            self.indent_level += 1
            self._process_block(if_stmt["Else"])
            self.indent_level -= 1

    def _process_loop_statement(self, loop_stmt):
        iteration_count = self._process_expression(loop_stmt["IterationCount"])
        self.output_code.append(
            f"{self._indent()}for _ in range({iteration_count}):")
        self.indent_level += 1
        self._process_block(loop_stmt["Block"])
        self.indent_level -= 1

    def _process_do_until_statement(self, do_until_stmt):
        self.output_code.append(f"{self._indent()}while True:")
        self.indent_level += 1
        self._process_block(do_until_stmt["Block"])
        condition = self._process_expression(do_until_stmt["Condition"])
        self.output_code.append(f"{self._indent()}if {condition}:")
        self.indent_level += 1
        self.output_code.append(f"{self._indent()}break")
        self.indent_level -= 1
        self.indent_level -= 1

    def _process_output_statement(self, output_stmt):
        """
        Handles output statements for various types of expressions or identifiers.
        """
        # Check if the output statement is a composite expression
        if "Left" in output_stmt and "Operator" in output_stmt and "Right" in output_stmt:
            expression = self._process_expression(output_stmt)
            self.output_code.append(f"{self._indent()}print({expression})")
        # Check if the output statement is a string literal
        elif "StringLiteral" in output_stmt:
            string_literal = output_stmt["StringLiteral"]
            self.output_code.append(
                f'{self._indent()}print("{string_literal}")')
        # Handle simple expressions (e.g., identifiers or literals)
        else:
            expression = self._process_expression(output_stmt)
            self.output_code.append(f"{self._indent()}print({expression})")

    def _process_function(self, func):
        name = func["Name"]
        params = ", ".join(func["Parameters"])
        self.output_code.append(f"{self._indent()}def {name}({params}):")
        self.indent_level += 1
        self._process_block(func["Body"])
        self.indent_level -= 1

    def _process_return(self, return_stmt):
        expression = self._process_expression(return_stmt["Expression"])
        self.output_code.append(f"{self._indent()}return {expression}")

    def _process_block(self, block):
        for statement in block:
            self._process_statement(statement)

    def _process_expression(self, expression, skip_constants_for=None):
        """
        Processes an expression, supporting literals, identifiers, composite expressions,
        function calls, and string operations.
        :param skip_constants_for: A set of identifiers to skip constant propagation.
        """
        # Handle literals
        if "Literal" in expression:
            return str(expression["Literal"])
        # Handle identifiers
        elif "Identifier" in expression:
            identifier = expression["Identifier"]
            # Skip constant propagation for specified identifiers
            if skip_constants_for and identifier in skip_constants_for:
                return identifier
            # Replace identifier with its constant value if available
            if identifier in self.constants:
                return self.constants[identifier]
            return identifier
        # Handle composite expressions (e.g., concatenations, arithmetic operations)
        elif "Left" in expression and "Operator" in expression and "Right" in expression:
            left = self._process_expression(expression["Left"], skip_constants_for)
            operator = expression["Operator"]
            right = self._process_expression(expression["Right"], skip_constants_for)

            # Handle string concatenation explicitly
            if operator == "+":
                is_left_string = left.startswith('"') or left.startswith("'")
                is_right_string = right.startswith('"') or right.startswith("'")
                if is_left_string or is_right_string:
                    left = f"str({left})" if not is_left_string else left
                    right = f"str({right})" if not is_right_string else right
                    return f"{left} + {right}"

            # Perform constant folding for literals
            if left.isdigit() and right.isdigit():
                left_value = int(left)
                right_value = int(right)
                if operator == "+":
                    return str(left_value + right_value)
                elif operator == "-":
                    return str(left_value - right_value)
                elif operator == "*":
                    return str(left_value * right_value)
                elif operator == "/":
                    return str(left_value / right_value)

            return f"({left} {operator} {right})"
        # Handle string literals explicitly
        elif "StringLiteral" in expression:
            return f'"{expression["StringLiteral"]}"'
        # Handle function calls
        elif "FunctionCall" in expression:
            function_name = expression["FunctionCall"]["Name"]
            arguments = [self._process_expression(
                arg, skip_constants_for) for arg in expression["FunctionCall"]["Arguments"]]
            return f"{function_name}({', '.join(arguments)})"
        else:
            raise ValueError("Unknown expression type.")

    def _indent(self):
        return "    " * self.indent_level


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python code_generator.py <ast_file.json> <output_file.py>")
        sys.exit(1)

    ast_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        with open(ast_file, "r") as f:
            ast = json.load(f)

        generator = CodeGenerator(ast)
        python_code = generator.generate()

        with open(output_file, "w") as f:
            f.write(python_code)

    except Exception as e:
        print(f"An error occurred during code generation: {e}")
        sys.exit(1)
