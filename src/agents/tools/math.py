from sympy import solve, sympify, SympifyError, symbols, Eq, solve, parse_expr

from .tool import Tool


class EvaluateExpressionTool(Tool):

    def __init__(self):
        description = (
            "Evaluate arithmetic or mathematical expressions provided as strings."
        )
        name = "evaluate_expression"
        parameters = {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The arithmetic or mathematical expression to evaluate.",
                }
            },
            "required": ["expression"],
        }
        super().__init__(description, name, parameters)

    def func(self, expression):
        try:
            result = sympify(expression)
            if result.is_number:
                result = float(result)
            else:
                result = str(result)
                return result
        except SympifyError as e:
            return str(e)


class CalculatePolynomialRootsTool(Tool):

    def __init__(self):
        description = "Find all real roots of a given polynomial."
        name = "calculate_polynomial_roots"
        parameters = {
            "type": "object",
            "properties": {
                "equation": {
                    "type": "string",
                    "description": "The polynomial equation to calculate the roots of.",
                }
            },
            "required": ["equation"],
        }
        super().__init__(description, name, parameters)

    def func(self, equation):
        try:
            roots = solve(sympify(equation), dict=True)
            roots_list = [str(root) for root in roots]
            return roots_list
        except SympifyError as e:
            return str(e)


class SolveAlgebraicEquationTool(Tool):

    def __init__(self):
        description = "Revises the existing function that solves a single variable algebraic equation to handle equations more robustly with variable terms on both sides."
        name = "solve_algebraic_equation"
        parameters = {
            "type": "object",
            "properties": {
                "equation": {
                    "type": "string",
                    "description": "The algebraic equation to solve.",
                },
                "variable": {
                    "type": "string",
                    "description": "The variable to solve for in the equation.",
                },
            },
            "required": ["equation", "variable"],
        }
        super().__init__(description, name, parameters)

    def func(self, equation, variable):
        # Create a symbolic variable
        symbol = symbols(variable)
        # Parse the equation string into a sympy expression
        left_part, right_part = equation.split("=")
        eq = Eq(parse_expr(left_part), parse_expr(right_part))
        # Solve the equation for the variable
        solution = solve(eq, symbol)
        return solution
