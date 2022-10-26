from motor_typing import TYPE_CHECKING


class Expression(object):
    pass


class ExpressionList(Expression):

    def __init__(self, expressions):
        # type: (Optional[List[Expression]]) -> None
        self._expressions = expressions


class ExpressionId(Expression):

    def __init__(self, reference):
        # type: (Reference) -> None
        self._reference = reference


class AmbiguousExpression(Expression):

    def __init__(self, ambiguous_expressions):
        # type: (List[Expression]) -> None
        self._ambiguous_expressions = ambiguous_expressions


class LiteralExpression(Expression):

    def __init__(self, literal):
        # type: (Literal) -> None
        self._literal = literal


class UnaryExpression(Expression):

    def __init__(self, operand, operator):
        # type: (Expression, Expression, str) -> None
        self._operand = operand
        self._operator = operator


class BinaryExpression(Expression):

    def __init__(self, left_operand, right_operand, operator):
        # type: (Expression, Expression, str) -> None
        self._left_operand = left_operand
        self._right_operand = right_operand
        self._operator = operator


class PostfixExpression(Expression):

    def __init__(self, operand, operator):
        # type: (Expression, Expression, str) -> None
        self._operand = operand
        self._operator = operator


class SizeofExpression(Expression):

    def __init__(self, operand):
        # type: (Expression) -> None
        self._operand = operand


class SizeofTypeExpression(Expression):

    def __init__(self, type):
        # type: (TypeId) -> None
        self._type = type


class SizeofPackExpression(Expression):

    def __init__(self, identifier):
        # type: (str) -> None
        self._identifier = identifier


class AlignofExpression(Expression):

    def __init__(self, type):
        # type: (TypeId) -> None
        self._type = type


class NoexceptExpression(Expression):

    def __init__(self, operand):
        # type: (Expression) -> None
        self._operand = operand


class CallExpression(Expression):

    def __init__(self, method, arguments):
        # type: (Expression, ExpressionList) -> None
        self._method = method
        self._arguments = arguments


class SubscriptExpression(Expression):

    def __init__(self, operand, subscript):
        # type: (Expression, Expression) -> None
        self._operand = operand
        self._subscript = subscript


class CastExpression(Expression):

    def __init__(self, operand, target_type):
        # type: (Expression, TypeId) -> None
        self._operand = operand
        self._target_type = target_type


class CxxCastExpression(Expression):

    def __init__(self, operand, target_type, cast_type):
        # type: (Expression, TypeId, str) -> None
        self._operand = operand
        self._target_type = target_type
        self._cast_type = cast_type


class ConditionalExpression(Expression):

    def __init__(self, condition, expression_true, expression_false):
        # type: (Expression, Expression, Expression) -> None
        self._condition = condition
        self._expression_true = expression_true
        self._expression_false = expression_false


class MemberAccessExpression(Expression):

    def __init__(self, expression, member_expression, template):
        # type: (Expression, Expression, bool) -> None
        self._expression = expression
        self._member_expression = member_expression
        self._template = template


class MemberAccessPtrExpression(Expression):

    def __init__(self, expression, member_expression, template):
        # type: (Expression, Expression, bool) -> None
        self._expression = expression
        self._member_expression = member_expression
        self._template = template


class MemberPtrExpression(Expression):

    def __init__(self, expression, member_expression):
        # type: (Expression, Expression) -> None
        self._expression = expression
        self._member_expression = member_expression


class TypeIdExpression(Expression):

    def __init__(self, operand):
        # type: (Expression) -> None
        self._operand = operand


class TypeIdExpressionType(Expression):

    def __init__(self, type):
        # type: (TypeId) -> None
        self._type = type


class SimpleCastExpression(Expression):

    def __init__(self, expression, type):
        # type: (Expression, TypeId) -> None
        self._expression = expression
        self._type = type


class NewExpression(Expression):

    def __init__(self, type, placement, initializer, root):
        # type: (TypeId, Optional[Expression], Optional[Expression], bool) -> None
        self._type = type
        self._placement = placement
        self._initializer = initializer
        self._root = root


class DeleteExpression(Expression):

    def __init__(self, operand, array, root):
        # type: (Expression, bool, bool) -> None
        self._operand = operand
        self._array = array
        self._root = root


class ThrowExpression(Expression):

    def __init__(self, operand):
        # type: (Optional[Expression]) -> None
        self._operand = operand


class YieldExpression(Expression):

    def __init__(self, operand):
        # type: (Expression) -> None
        self._operand = operand


class AwaitExpression(Expression):

    def __init__(self, operand):
        # type: (Expression) -> None
        self._operand = operand


class FoldExpressionLeft(Expression):

    def __init__(self, expression, operator):
        # type: (Expression, str) -> None
        self._expression = expression
        self._operator = operator


class FoldExpressionRight(Expression):

    def __init__(self, expression, operator):
        # type: (Expression, str) -> None
        self._expression = expression
        self._operator = operator


class FoldExpressionBoth(Expression):

    def __init__(self, expression_left, operator_left, expression_right, operator_right):
        # type: (Expression, str, Expression, str) -> None
        self._expression_left = expression_left
        self._expression_right = expression_right
        self._operator_left = operator_left
        self._operator_right = operator_right


if TYPE_CHECKING:
    from .reference import Reference
    from .literals import Literal
    from .types import TypeId
    from typing import Any, List, Optional