from typing import List, Optional
from . import Visitor
from glrp import Token
from .type import TypeId


class Expression(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class ErrorExpression(Expression):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_error_expression(self)


class AbstractInitializerList(Expression):
    pass


class InitializerList(AbstractInitializerList):

    def __init__(self, expressions: List[Expression]) -> None:
        self._expressions = expressions

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_initializer_list(self)

    def accept_expressions(self, visitor: Visitor) -> None:
        if self._expressions is not None:
            for expression in self._expressions:
                expression.accept(visitor)


class AmbiguousInitializerList(AbstractInitializerList):

    def __init__(self, initializer_lists: List[InitializerList]) -> None:
        self._initializer_lists = initializer_lists

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_initializer_list(self)

    def accept_first(self, visitor: Visitor) -> None:
        self._initializer_lists[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for init_list in self._initializer_lists:
            init_list.accept(visitor)


class ParenthesizedExpression(Expression):

    def __init__(self, expression: Optional[AbstractInitializerList]) -> None:
        self._expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_parenthesized_expression(self)

    def accept_expression(self, visitor: Visitor) -> None:
        if self._expression is not None:
            self._expression.accept(visitor)


class IdExpression(Expression):

    def __init__(self, reference: "Reference") -> None:
        self._reference = reference

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_id_expression(self)

    def accept_reference(self, visitor: Visitor) -> None:
        self._reference.accept(visitor)


class AmbiguousExpression(Expression):

    def __init__(self, ambiguous_expressions: List[Expression]) -> None:
        self._ambiguous_expressions = ambiguous_expressions

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_expression(self)

    def accept_first(self, visitor: Visitor) -> None:
        self._ambiguous_expressions[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for expression in self._ambiguous_expressions:
            expression.accept(visitor)


class UnaryExpression(Expression):

    def __init__(self, operand: Expression, operator: str) -> None:
        self._operand = operand
        self._operator = operator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_unary_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)


class BinaryExpression(Expression):

    def __init__(self, left_operand: Expression, right_operand: Expression, operator: str) -> None:
        self._left_operand = left_operand
        self._right_operand = right_operand
        self._operator = operator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_binary_expression(self)

    def accept_left_operand(self, visitor: Visitor) -> None:
        self._left_operand.accept(visitor)

    def accept_right_operand(self, visitor: Visitor) -> None:
        self._right_operand.accept(visitor)


class PostfixExpression(Expression):

    def __init__(self, operand: Expression, operator: str) -> None:
        self._operand = operand
        self._operator = operator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_postfix_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)


class SizeofExpression(Expression):

    def __init__(self, operand: Expression) -> None:
        self._operand = operand

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_sizeof_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)


class SizeofTypeExpression(Expression):

    def __init__(self, type: TypeId) -> None:
        self._type = type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_sizeof_type_expression(self)

    def accept_type(self, visitor: Visitor) -> None:
        self._type.accept(visitor)


class SizeofPackExpression(Expression):

    def __init__(self, identifier: str) -> None:
        self._identifier = identifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_sizeof_pack_expression(self)


class AlignofExpression(Expression):

    def __init__(self, alignof_token: str, type: TypeId) -> None:
        self._alignof_token = alignof_token
        self._type = type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_alignof_expression(self)

    def accept_type(self, visitor: Visitor) -> None:
        self._type.accept(visitor)


class NoexceptExpression(Expression):

    def __init__(self, operand: Expression) -> None:
        self._operand = operand

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_noexcept_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)


class CallExpression(Expression):

    def __init__(self, method: Expression, arguments: ParenthesizedExpression) -> None:
        self._method = method
        self._arguments = arguments

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_call_expression(self)

    def accept_method(self, visitor: Visitor) -> None:
        self._method.accept(visitor)

    def accept_arguments(self, visitor: Visitor) -> None:
        self._arguments.accept(visitor)


class SubscriptExpression(Expression):

    def __init__(self, operand: Expression, subscript: Expression) -> None:
        self._operand = operand
        self._subscript = subscript

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_subscript_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)

    def accept_subscript(self, visitor: Visitor) -> None:
        self._subscript.accept(visitor)


class CastExpression(Expression):

    def __init__(self, operand: Expression, target_type: TypeId) -> None:
        self._operand = operand
        self._target_type = target_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_cast_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)

    def accept_target_type(self, visitor: Visitor) -> None:
        self._target_type.accept(visitor)


class CxxCastExpression(Expression):

    def __init__(self, operand: Expression, target_type: TypeId, cast_type: str) -> None:
        self._operand = operand
        self._target_type = target_type
        self._cast_type = cast_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_cxx_cast_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)

    def accept_target_type(self, visitor: Visitor) -> None:
        self._target_type.accept(visitor)


class ConditionalExpression(Expression):

    def __init__(self, condition: Expression, expression_true: Expression, expression_false: Expression) -> None:
        self._condition = condition
        self._expression_true = expression_true
        self._expression_false = expression_false

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_conditional_expression(self)

    def accept_condition(self, visitor: Visitor) -> None:
        self._condition.accept(visitor)

    def accept_expression_true(self, visitor: Visitor) -> None:
        self._expression_true.accept(visitor)

    def accept_expression_false(self, visitor: Visitor) -> None:
        self._expression_false.accept(visitor)


class MemberAccessExpression(Expression):

    def __init__(self, expression: Expression, member_expression: "Reference", template: bool) -> None:
        self._expression = expression
        self._member_expression = member_expression
        self._template = template

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_member_access_expression(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)

    def accept_member_expression(self, visitor: Visitor) -> None:
        self._member_expression.accept(visitor)


class MemberAccessPtrExpression(Expression):

    def __init__(self, expression: Expression, member_expression: "Reference", template: bool) -> None:
        self._expression = expression
        self._member_expression = member_expression
        self._template = template

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_member_access_ptr_expression(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)

    def accept_member_expression(self, visitor: Visitor) -> None:
        self._member_expression.accept(visitor)


class MemberPtrExpression(Expression):

    def __init__(self, expression: Expression, member_expression: Expression, access_type: str) -> None:
        self._expression = expression
        self._member_expression = member_expression
        self._access_type = access_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_member_ptr_expression(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)

    def accept_member_expression(self, visitor: Visitor) -> None:
        self._member_expression.accept(visitor)


class TypeIdExpression(Expression):

    def __init__(self, operand: Expression) -> None:
        self._operand = operand

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_id_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)


class TypeIdExpressionType(Expression):

    def __init__(self, type: TypeId) -> None:
        self._type = type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_id_expression_type(self)

    def accept_type(self, visitor: Visitor) -> None:
        self._type.accept(visitor)


class SimpleCastExpression(Expression):

    def __init__(self, expression: Expression, type: TypeId) -> None:
        self._expression = expression
        self._type = type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_simple_cast_expression(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)

    def accept_type(self, visitor: Visitor) -> None:
        self._type.accept(visitor)


class NewExpression(Expression):

    def __init__(
        self, type: TypeId, placement: Optional[ParenthesizedExpression], initializer: Optional[Expression], root: bool,
        full_type: bool
    ) -> None:
        self._type = type
        self._placement = placement
        self._initializer = initializer
        self._root = root
        self._full_type = full_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_new_expression(self)

    def accept_type(self, visitor: Visitor) -> None:
        self._type.accept(visitor)

    def accept_placement(self, visitor: Visitor) -> None:
        if self._placement is not None:
            self._placement.accept(visitor)

    def accept_initializer(self, visitor: Visitor) -> None:
        if self._initializer is not None:
            self._initializer.accept(visitor)


class DeleteExpression(Expression):

    def __init__(self, operand: Expression, array: bool, root: bool) -> None:
        self._operand = operand
        self._array = array
        self._root = root

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_delete_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)


class ThrowExpression(Expression):

    def __init__(self, operand: Optional[Expression]) -> None:
        self._operand = operand

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_throw_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        if self._operand is not None:
            self._operand.accept(visitor)


class YieldExpression(Expression):

    def __init__(self, operand: Expression) -> None:
        self._operand = operand

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_yield_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)


class AwaitExpression(Expression):

    def __init__(self, operand: Expression) -> None:
        self._operand = operand

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_await_expression(self)

    def accept_operand(self, visitor: Visitor) -> None:
        self._operand.accept(visitor)


class FoldExpressionLeft(Expression):

    def __init__(self, expression: Expression, operator: str) -> None:
        self._expression = expression
        self._operator = operator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_fold_expression_left(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)


class FoldExpressionRight(Expression):

    def __init__(self, expression: Expression, operator: str) -> None:
        self._expression = expression
        self._operator = operator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_fold_expression_right(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)


class FoldExpressionBoth(Expression):

    def __init__(
        self, expression_left: Expression, operator_left: str, expression_right: Expression, operator_right: str
    ) -> None:
        self._expression_left = expression_left
        self._expression_right = expression_right
        self._operator_left = operator_left
        self._operator_right = operator_right

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_fold_expression_both(self)

    def accept_expression_left(self, visitor: Visitor) -> None:
        self._expression_left.accept(visitor)

    def accept_expression_right(self, visitor: Visitor) -> None:
        self._expression_right.accept(visitor)


class ThisExpression(Expression):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_this_expression(self)


class NullPtrExpression(Expression):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_nullptr_expression(self)


class TypeTraitExpression(Expression):

    def __init__(self, type_trait: str, arguments: Optional[List[Token]]) -> None:
        self._type_trait = type_trait
        self._arguments = arguments

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_trait_expression(self)


from .reference import Reference
