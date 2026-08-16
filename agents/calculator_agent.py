import ast
import operator
from typing import Any, Union
from core.agent import BaseAgent
from core.result import Result
from core.task import Task


class SafeMathEvaluator(ast.NodeVisitor):
    """AST NodeVisitor for safe arithmetic expression evaluation without eval()."""

    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(self, expression: str) -> Union[int, float]:
        """Parses and safely evaluates a math expression string."""
        cleaned_expr = expression.strip()
        if not cleaned_expr:
            raise ValueError("Empty mathematical expression")
        parsed_ast = ast.parse(cleaned_expr, mode="eval")
        return self.visit(parsed_ast)

    def visit(self, node: ast.AST) -> Union[int, float]:
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise ValueError(f"Unsupported literal constant: {node.value}")
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_OPERATORS:
                raise ValueError(f"Unsupported operation: {op_type.__name__}")
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right_val == 0:
                raise ZeroDivisionError("Division by zero")
            return self.ALLOWED_OPERATORS[op_type](left_val, right_val)
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_OPERATORS:
                raise ValueError(f"Unsupported operation: {op_type.__name__}")
            operand_val = self.visit(node.operand)
            return self.ALLOWED_OPERATORS[op_type](operand_val)
        else:
            raise ValueError(f"Disallowed expression node: {type(node).__name__}")


class CalculatorAgent(BaseAgent):
    """Agent capable of safely evaluating basic arithmetic expressions."""

    def __init__(self, agent_id: str = "agent-calculator-01"):
        super().__init__(
            name="CalculatorAgent",
            capabilities=["math", "calculation", "arithmetic"],
            agent_id=agent_id,
        )
        self.evaluator = SafeMathEvaluator()

    def execute(self, task: Task) -> Result:
        raw_input = task.input_data
        expression_str = ""

        if isinstance(raw_input, str):
            expression_str = raw_input
        elif isinstance(raw_input, dict) and "expression" in raw_input:
            expression_str = str(raw_input["expression"])
        elif isinstance(raw_input, (int, float)):
            return Result(
                success=True,
                output=raw_input,
                agent_id=self.id,
                metadata={"expression": str(raw_input)}
            )
        else:
            expression_str = str(task.description or "")

        try:
            output_val = self.evaluator.evaluate(expression_str)
            # Format integer outputs cleanly if whole number
            if isinstance(output_val, float) and output_val.is_integer():
                output_val = int(output_val)

            return Result(
                success=True,
                output=output_val,
                agent_id=self.id,
                metadata={"expression": expression_str}
            )
        except ZeroDivisionError as e:
            return Result(
                success=False,
                output=None,
                error=f"Math Error: {str(e)}",
                agent_id=self.id,
                metadata={"expression": expression_str}
            )
        except Exception as e:
            return Result(
                success=False,
                output=None,
                error=f"Invalid expression or evaluation error: {str(e)}",
                agent_id=self.id,
                metadata={"expression": expression_str}
            )
