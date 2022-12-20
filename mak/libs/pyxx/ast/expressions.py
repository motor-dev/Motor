from motor_typing import TYPE_CHECKING


class Expression(object):
    pass


class ExpressionList(Expression):

    def __init__(self, expressions):
        # type: (Optional[List[Expression]]) -> None
        self._expressions = expressions

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_expression_list(self)


class IdExpression(Expression):

    def __init__(self, reference):
        # type: (Reference) -> None
        self._reference = reference

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_id_expression(self)


class AmbiguousExpression(Expression):

    def __init__(self, ambiguous_expressions):
        # type: (List[Expression]) -> None
        self._ambiguous_expressions = ambiguous_expressions

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_expression(self)


class LiteralExpression(Expression):

    def __init__(self, literal):
        # type: (Literal) -> None
        self._literal = literal

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_literal_expression(self)


class UnaryExpression(Expression):

    def __init__(self, operand, operator):
        # type: (Expression, Expression, str) -> None
        self._operand = operand
        self._operator = operator

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_unary_expression(self)


class BinaryExpression(Expression):

    def __init__(self, left_operand, right_operand, operator):
        # type: (Expression, Expression, str) -> None
        self._left_operand = left_operand
        self._right_operand = right_operand
        self._operator = operator

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_binary_expression(self)


class PostfixExpression(Expression):

    def __init__(self, operand, operator):
        # type: (Expression, Expression, str) -> None
        self._operand = operand
        self._operator = operator

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_postfix_expression(self)


class SizeofExpression(Expression):

    def __init__(self, operand):
        # type: (Expression) -> None
        self._operand = operand

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_sizeof_expression(self)


class SizeofTypeExpression(Expression):

    def __init__(self, type):
        # type: (TypeId) -> None
        self._type = type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_sizeof_type_expression(self)


class SizeofPackExpression(Expression):

    def __init__(self, identifier):
        # type: (str) -> None
        self._identifier = identifier

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_sizeof_pack_expression(self)


class AlignofExpression(Expression):

    def __init__(self, alignof_token, type):
        # type: (str, TypeId) -> None
        self._alignof_token = alignof_token
        self._type = type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_alignof_expression(self)


class NoexceptExpression(Expression):

    def __init__(self, operand):
        # type: (Expression) -> None
        self._operand = operand

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_noexcept_expression(self)


class CallExpression(Expression):

    def __init__(self, method, arguments):
        # type: (Expression, ExpressionList) -> None
        self._method = method
        self._arguments = arguments

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_call_expression(self)


class SubscriptExpression(Expression):

    def __init__(self, operand, subscript):
        # type: (Expression, Expression) -> None
        self._operand = operand
        self._subscript = subscript

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_subscript_expression(self)


class CastExpression(Expression):

    def __init__(self, operand, target_type):
        # type: (Expression, TypeId) -> None
        self._operand = operand
        self._target_type = target_type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_cast_expression(self)


class CxxCastExpression(Expression):

    def __init__(self, operand, target_type, cast_type):
        # type: (Expression, TypeId, str) -> None
        self._operand = operand
        self._target_type = target_type
        self._cast_type = cast_type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_cxx_cast_expression(self)


class ConditionalExpression(Expression):

    def __init__(self, condition, expression_true, expression_false):
        # type: (Expression, Expression, Expression) -> None
        self._condition = condition
        self._expression_true = expression_true
        self._expression_false = expression_false

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_conditional_expression(self)


class MemberAccessExpression(Expression):

    def __init__(self, expression, member_expression, template):
        # type: (Expression, Expression, bool) -> None
        self._expression = expression
        self._member_expression = member_expression
        self._template = template

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_member_access_expression(self)


class MemberAccessPtrExpression(Expression):

    def __init__(self, expression, member_expression, template):
        # type: (Expression, Expression, bool) -> None
        self._expression = expression
        self._member_expression = member_expression
        self._template = template

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_member_access_ptr_expression(self)


class MemberPtrExpression(Expression):

    def __init__(self, expression, member_expression):
        # type: (Expression, Expression) -> None
        self._expression = expression
        self._member_expression = member_expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_member_ptr_expression(self)


class TypeIdExpression(Expression):

    def __init__(self, operand):
        # type: (Expression) -> None
        self._operand = operand

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_type_id_expression(self)


class TypeIdExpressionType(Expression):

    def __init__(self, type):
        # type: (TypeId) -> None
        self._type = type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_type_id_expression_type(self)


class SimpleCastExpression(Expression):

    def __init__(self, expression, type):
        # type: (Expression, TypeId) -> None
        self._expression = expression
        self._type = type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_simple_cast_expression(self)


class NewExpression(Expression):

    def __init__(self, type, placement, initializer, root):
        # type: (TypeId, Optional[Expression], Optional[Expression], bool) -> None
        self._type = type
        self._placement = placement
        self._initializer = initializer
        self._root = root

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_new_expression(self)


class DeleteExpression(Expression):

    def __init__(self, operand, array, root):
        # type: (Expression, bool, bool) -> None
        self._operand = operand
        self._array = array
        self._root = root

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_delete_expression(self)


class ThrowExpression(Expression):

    def __init__(self, operand):
        # type: (Optional[Expression]) -> None
        self._operand = operand

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_throw_expression(self)


class YieldExpression(Expression):

    def __init__(self, operand):
        # type: (Expression) -> None
        self._operand = operand

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_yield_expression(self)


class AwaitExpression(Expression):

    def __init__(self, operand):
        # type: (Expression) -> None
        self._operand = operand

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_await_expression(self)


class FoldExpressionLeft(Expression):

    def __init__(self, expression, operator):
        # type: (Expression, str) -> None
        self._expression = expression
        self._operator = operator

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_fold_expression_left(self)


class FoldExpressionRight(Expression):

    def __init__(self, expression, operator):
        # type: (Expression, str) -> None
        self._expression = expression
        self._operator = operator

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_fold_expression_right(self)


class FoldExpressionBoth(Expression):

    def __init__(self, expression_left, operator_left, expression_right, operator_right):
        # type: (Expression, str, Expression, str) -> None
        self._expression_left = expression_left
        self._expression_right = expression_right
        self._operator_left = operator_left
        self._operator_right = operator_right

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_fold_expression_both(self)


class ParenthesizedExpression(Expression):

    def __init__(self, expression):
        # type: (Expression) -> None
        self._expression = expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_parenthesized_expression(self)


class ThisExpression(Expression):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_this_expression(self)


class NullPtrExpression(Expression):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_null_ptr_expression(self)


class TypeTraitExpression(Expression):

    def __init__(self, type_trait, arguments):
        # type: (str, Optional[List[Token]]) -> None
        self._type_trait = type_trait
        self._arguments = arguments

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_type_trait_expression(self)


if TYPE_CHECKING:
    from typing import List, Optional
    from . import Visitor
    from .reference import Reference
    from .literals import Literal
    from .type import TypeId
    from glrp import Token