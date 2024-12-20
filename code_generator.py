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
        # Try to determine if the condition is a compile-time boolean
        condition_expr = if_stmt["Condition"]
        condition_value = self._evaluate_condition(condition_expr)

        if condition_value is True:
            # Condition is always True, process only 'Then' block
            self._process_block(if_stmt["Then"])
        elif condition_value is False:
            # Condition is always False, process only 'Else' block if present
            if "Else" in if_stmt:
                self._process_block(if_stmt["Else"])
            # If no else block, do nothing
        else:
            # Condition not known at compile time, generate normal if statement
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

    def _evaluate_condition(self, condition_expr):
        """
        Attempt to evaluate the condition at compile time.
        Since your language requires conditions to be comparisons,
        we handle them as booleans (True/False) if both sides are known.
        Return True/False if evaluated, or None if not known at compile time.
        """

        # Handle direct literals or identifiers first
        def eval_operand(op):
            # If literal
            if "Literal" in op:
                return int(op["Literal"])
            # If identifier and known constant
            if "Identifier" in op:
                identifier = op["Identifier"]
                if identifier in self.constants and self.constants[identifier].isdigit():
                    return int(self.constants[identifier])
                return None  # unknown
            # If a nested expression that we can evaluate
            if "Left" in op and "Operator" in op and "Right" in op:
                val = self._process_expression(op)
                if val.isdigit():
                    return int(val)
                return None
            return None

        # If condition_expr is a comparison: it will have Left, Operator, Right
        if "Left" in condition_expr and "Operator" in condition_expr and "Right" in condition_expr:
            left_val = eval_operand(condition_expr["Left"])
            right_val = eval_operand(condition_expr["Right"])
            operator = condition_expr["Operator"]

            # If we know both sides as integers, we can evaluate
            if left_val is not None and right_val is not None:
                if operator == "==":
                    return left_val == right_val
                elif operator == "!=":
                    return left_val != right_val
                elif operator == ">":
                    return left_val > right_val
                elif operator == ">=":
                    return left_val >= right_val
                elif operator == "<":
                    return left_val < right_val
                elif operator == "<=":
                    return left_val <= right_val
                # If some operator not handled, return None
            return None
        else:
            # Not a comparison or can't evaluate
            return None

    def _process_loop_statement(self, loop_stmt):
        iteration_count = self._process_expression(loop_stmt["IterationCount"])
        # If iteration_count is known and zero, we can skip the loop entirely
        if iteration_count.isdigit() and int(iteration_count) == 0:
            # No loop needed
            return
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
        if "Left" in output_stmt and "Operator" in output_stmt and "Right" in output_stmt:
            expression = self._process_expression(output_stmt)
            self.output_code.append(f"{self._indent()}print({expression})")
        elif "StringLiteral" in output_stmt:
            string_literal = output_stmt["StringLiteral"]
            self.output_code.append(
                f'{self._indent()}print("{string_literal}")')
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
        Also applies constant folding, constant propagation, and algebraic simplifications.
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

            # String concatenation handling
            if operator == "+":
                is_left_string = (left.startswith('"') or left.startswith("'"))
                is_right_string = (right.startswith('"') or right.startswith("'"))
                if is_left_string or is_right_string:
                    left = f"str({left})" if not is_left_string else left
                    right = f"str({right})" if not is_right_string else right
                    return f"{left} + {right}"

            # Constant folding (if both operands are digits)
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
                    # Avoid division by zero in code gen (not handled by AST)
                    if right_value != 0:
                        return str(left_value / right_value)

            # Algebraic simplifications when one side is a constant
            left_is_digit = left.isdigit()
            right_is_digit = right.isdigit()
            if operator == "+":
                # x + 0 -> x, 0 + x -> x
                if right_is_digit and int(right) == 0:
                    return left
                if left_is_digit and int(left) == 0:
                    return right
            elif operator == "-":
                # x - 0 -> x
                if right_is_digit and int(right) == 0:
                    return left
            elif operator == "*":
                # x * 1 -> x, 1 * x -> x
                # x * 0 -> 0, 0 * x -> 0
                if right_is_digit:
                    if int(right) == 1:
                        return left
                    elif int(right) == 0:
                        return "0"
                if left_is_digit:
                    if int(left) == 1:
                        return right
                    elif int(left) == 0:
                        return "0"
            elif operator == "/":
                # x / 1 -> x
                if right_is_digit and int(right) == 1:
                    return left

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
