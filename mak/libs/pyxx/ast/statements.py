from typing import List, Optional
from . import Visitor
from .declarations import Declaration
from .expressions import Expression
from .type import TypeSpecifierSeq, Declarator
from .attributes import Attribute


class Statement(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class ErrorStatement(Statement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_error_statement(self)


class StatementWithAttributes(Statement):

    def __init__(self, attribute_list: List[Attribute], statement: Statement) -> None:
        self._attribute_list = attribute_list
        self._statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_statement_with_attributes(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attribute_list:
            attribute.accept(visitor)

    def accept_statement(self, visitor: Visitor) -> None:
        self._statement.accept(visitor)


class AmbiguousStatement(Statement):

    def __init__(self, statement_list: List[Statement]) -> None:
        self._statement_list = statement_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_statement(self)


class EmptyStatement(Statement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_empty_statement(self)


class ExpressionStatement(Statement):

    def __init__(self, expression: Expression) -> None:
        self._expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_expression_statement(self)


class DeclarationStatement(Statement):

    def __init__(self, declaration: Declaration) -> None:
        self._declaration = declaration

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declaration_statement(self)


class CompoundStatement(Statement):

    def __init__(self, statement_list: List[Statement]) -> None:
        self._statemenent_list = statement_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_compound_statement(self)


class ExceptionDeclaration(object):
    pass


class ExceptionDeclarationError(ExceptionDeclaration):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_exception_declaration_error(self)


class ExceptionDeclarationTypeSpecifier(ExceptionDeclaration):

    def __init__(
        self, attribute_list: List[Attribute], type_specifier_seq: TypeSpecifierSeq, declarator: Optional[Declarator]
    ) -> None:
        self._attribute_list = attribute_list
        self._type_specifier_seq = type_specifier_seq
        self._declarator = declarator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_exception_declaration_type_specifier(self)


class ExceptionDeclarationAny(ExceptionDeclaration):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_exception_declaration_any(self)


class AmbiguousExceptionDeclaration(ExceptionDeclaration):

    def __init__(self, exception_declaration_list: List[ExceptionDeclaration]) -> None:
        self._exception_declaration_list = exception_declaration_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_exception_declaration(self)


class ExceptionHandler(object):

    def __init__(self, exception_declaration: ExceptionDeclaration, handler_statement: CompoundStatement) -> None:
        self._exception_declaration = exception_declaration
        self._handler_statement = handler_statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_exception_handler(self)


class TryBlock(Statement):

    def __init__(self, try_statement: CompoundStatement, handlers: List[ExceptionHandler]) -> None:
        self._try_statement = try_statement
        self._handlers = handlers

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_try_block(self)


class BreakStatement(Statement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_break_statement(self)


class ContinueStatement(Statement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_continue_statement(self)


class ReturnStatement(Statement):

    def __init__(self, return_expression: Optional[Expression]) -> None:
        self._return_expression = return_expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_return_statement(self)


class CoReturnStatement(Statement):

    def __init__(self, return_expression: Optional[Expression]) -> None:
        self._return_expression = return_expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_co_return_statement(self)


class GotoStatement(Statement):

    def __init__(self, label: str) -> None:
        self._label = label

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_goto_statement(self)


class LabeledStatement(Statement):

    def __init__(self, attributes: List[Attribute], label: str, statement: Statement) -> None:
        self._attributes = attributes
        self._label = label
        self._statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_labeled_statement(self)


class CaseStatement(Statement):

    def __init__(self, attributes: List[Attribute], expression: Expression, statement: Statement) -> None:
        self._attributes = attributes
        self._expression = expression
        self._statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_case_statement(self)


class DefaultStatement(Statement):

    def __init__(self, attributes: List[Attribute], statement: Statement) -> None:
        self._attributes = attributes
        self._statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_default_statement(self)


class _SelectionCondition(object):
    pass


class SelectionCondition(_SelectionCondition):

    def __init__(self, init_statement: Optional[DeclarationStatement], condition: Expression) -> None:
        self._init_statement = init_statement
        self._condition = condition

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_selection_condition(self)


class AmbiguousSelectionCondition(_SelectionCondition):

    def __init__(self, condition_list: List[_SelectionCondition]) -> None:
        self._condition_list = condition_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_selection_condition(self)


class SwitchStatement(Statement):

    def __init__(self, condition: _SelectionCondition, statement: Statement) -> None:
        self._condition = condition
        self._statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_switch_statement(self)


class IfStatement(Statement):

    def __init__(
        self, condition: _SelectionCondition, true_statement: Statement, false_statement: Optional[Statement],
        is_constexpr: bool
    ) -> None:
        self._condition = condition
        self._true_statement = true_statement
        self._false_statement = false_statement
        self._is_constexpr = is_constexpr

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_if_statement(self)


class IfConstevalStatement(Statement):

    def __init__(self, is_reversed: bool, true_statement: Statement, false_statement: Optional[Statement]) -> None:
        self._is_reversed = is_reversed
        self._true_statement = true_statement
        self._false_statement = false_statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_if_consteval_statement(self)


class WhileStatement(Statement):

    def __init__(self, condition: Expression, statement: Statement) -> None:
        self._condition = condition
        self._statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_while_statement(self)


class DoWhileStatement(Statement):

    def __init__(self, condition: Expression, statement: Statement) -> None:
        self._condition = condition
        self._statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_do_while_statement(self)


class ForCondition(object):
    pass


class AmbiguousForCondition(ForCondition):

    def __init__(self, for_condition_list: List[ForCondition]) -> None:
        self._for_condition_list = for_condition_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_for_condition(self)


class ForConditionInit(ForCondition):

    def __init__(
        self, init_statement: Statement, condition: Optional[Expression], update: Optional[Expression]
    ) -> None:
        self._init_statement = init_statement
        self._condition = condition
        self._update = update

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_for_condition_init(self)


class ForConditionRange(ForCondition):

    def __init__(self, init_statement: Optional[Statement], declaration: Declaration) -> None:
        self._init_statement = init_statement
        self._declaration = declaration

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_for_condition_range(self)


class ForStatement(Statement):

    def __init__(self, for_range: ForCondition, statement: Statement) -> None:
        self._for_range = for_range
        self._statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_for_statement(self)
