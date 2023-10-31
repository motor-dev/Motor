from typing import List, Optional
from . import Visitor
from .base import Declaration, Attribute, Declarator, Expression
from .type import TypeSpecifierSeq


class Statement(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class ErrorStatement(Statement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_error_statement(self)


class StatementWithAttributes(Statement):

    def __init__(self, attribute_list: List[Attribute], statement: Statement) -> None:
        self.attribute_list = attribute_list
        self.statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_statement_with_attributes(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attribute_list:
            attribute.accept(visitor)

    def accept_statement(self, visitor: Visitor) -> None:
        self.statement.accept(visitor)


class AmbiguousStatement(Statement):

    def __init__(self, statement_list: List[Statement]) -> None:
        self.statement_list = statement_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_statement(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.statement_list[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for statement in self.statement_list:
            statement.accept(visitor)


class EmptyStatement(Statement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_empty_statement(self)


class ExpressionStatement(Statement):

    def __init__(self, expression: "Expression") -> None:
        self.expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_expression_statement(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self.expression.accept(visitor)


class DeclarationStatement(Statement):

    def __init__(self, declaration: Declaration) -> None:
        self.declaration = declaration

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declaration_statement(self)

    def accept_declaration(self, visitor: Visitor) -> None:
        self.declaration.accept(visitor)


class CompoundStatement(Statement):

    def __init__(self, statement_list: List[Statement]) -> None:
        self.statemenent_list = statement_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_compound_statement(self)

    def accept_children(self, visitor: Visitor) -> None:
        for statement in self.statemenent_list:
            statement.accept(visitor)


class ExceptionDeclaration(object):
    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class ExceptionDeclarationError(ExceptionDeclaration):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_exception_declaration_error(self)


class ExceptionDeclarationTypeSpecifier(ExceptionDeclaration):

    def __init__(
            self, attribute_list: List[Attribute], type_specifier_seq: "TypeSpecifierSeq",
            declarator: Optional["Declarator"]
    ) -> None:
        self.attribute_list = attribute_list
        self.type_specifier_seq = type_specifier_seq
        self.declarator = declarator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_exception_declaration_type_specifier(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attribute_list:
            attribute.accept(visitor)

    def accept_type_specifier_seq(self, visitor: Visitor) -> None:
        self.type_specifier_seq.accept(visitor)

    def accept_declarator(self, visitor: Visitor) -> None:
        if self.declarator is not None:
            self.declarator.accept(visitor)


class ExceptionDeclarationAny(ExceptionDeclaration):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_exception_declaration_any(self)


class AmbiguousExceptionDeclaration(ExceptionDeclaration):

    def __init__(self, exception_declaration_list: List[ExceptionDeclaration]) -> None:
        self.exception_declaration_list = exception_declaration_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_exception_declaration(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.exception_declaration_list[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for exception_declaration in self.exception_declaration_list:
            exception_declaration.accept(visitor)


class ExceptionHandler(object):

    def __init__(self, exception_declaration: ExceptionDeclaration, handler_statement: CompoundStatement) -> None:
        self.exception_declaration = exception_declaration
        self.handler_statement = handler_statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_exception_handler(self)

    def accept_exception_declaration(self, visitor: Visitor) -> None:
        self.exception_declaration.accept(visitor)

    def accept_handler_statement(self, visitor: Visitor) -> None:
        self.handler_statement.accept(visitor)


class TryBlock(Statement):

    def __init__(self, try_statement: CompoundStatement, handlers: List[ExceptionHandler]) -> None:
        self.try_statement = try_statement
        self.handlers = handlers

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_try_block(self)

    def accept_try_statement(self, visitor: Visitor) -> None:
        self.try_statement.accept(visitor)

    def accept_handlers(self, visitor: Visitor) -> None:
        for handler in self.handlers:
            handler.accept(visitor)


class BreakStatement(Statement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_break_statement(self)


class ContinueStatement(Statement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_continue_statement(self)


class ReturnStatement(Statement):

    def __init__(self, return_expression: Optional["Expression"]) -> None:
        self.return_expression = return_expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_return_statement(self)

    def accept_return_expression(self, visitor: Visitor) -> None:
        if self.return_expression is not None:
            self.return_expression.accept(visitor)


class CoReturnStatement(Statement):

    def __init__(self, return_expression: Optional["Expression"]) -> None:
        self.return_expression = return_expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_co_return_statement(self)

    def accept_return_expression(self, visitor: Visitor) -> None:
        if self.return_expression is not None:
            self.return_expression.accept(visitor)


class GotoStatement(Statement):

    def __init__(self, label: str) -> None:
        self.label = label

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_goto_statement(self)


class LabeledStatement(Statement):

    def __init__(self, attributes: List[Attribute], label: str, statement: Statement) -> None:
        self.attribute_list = attributes
        self.label = label
        self.statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_labeled_statement(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attribute_list:
            attribute.accept(visitor)

    def accept_statement(self, visitor: Visitor) -> None:
        self.statement.accept(visitor)


class CaseStatement(Statement):

    def __init__(self, attributes: List[Attribute], expression: "Expression", statement: Statement) -> None:
        self.attribute_list = attributes
        self.expression = expression
        self.statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_case_statement(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attribute_list:
            attribute.accept(visitor)

    def accept_expression(self, visitor: Visitor) -> None:
        self.expression.accept(visitor)

    def accept_statement(self, visitor: Visitor) -> None:
        self.statement.accept(visitor)


class DefaultStatement(Statement):

    def __init__(self, attributes: List[Attribute], statement: Statement) -> None:
        self.attribute_list = attributes
        self.statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_default_statement(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attribute_list:
            attribute.accept(visitor)

    def accept_statement(self, visitor: Visitor) -> None:
        self.statement.accept(visitor)


class _SelectionCondition(object):
    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class SelectionCondition(_SelectionCondition):

    def __init__(self, init_statement: Optional[DeclarationStatement], condition: "Expression") -> None:
        self.init_statement = init_statement
        self.condition = condition

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_selection_condition(self)

    def accept_init_statement(self, visitor: Visitor) -> None:
        if self.init_statement is not None:
            self.init_statement.accept(visitor)

    def accept_condition(self, visitor: Visitor) -> None:
        self.condition.accept(visitor)


class AmbiguousSelectionCondition(_SelectionCondition):

    def __init__(self, condition_list: List[_SelectionCondition]) -> None:
        self.condition_list = condition_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_selection_condition(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.condition_list[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for condition in self.condition_list:
            condition.accept(visitor)


class SwitchStatement(Statement):

    def __init__(self, condition: _SelectionCondition, statement: Statement) -> None:
        self.condition = condition
        self.statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_switch_statement(self)

    def accept_condition(self, visitor: Visitor) -> None:
        self.condition.accept(visitor)

    def accept_statement(self, visitor: Visitor) -> None:
        self.statement.accept(visitor)


class IfStatement(Statement):

    def __init__(
            self, condition: _SelectionCondition, true_statement: Statement, false_statement: Optional[Statement],
            is_constexpr: bool
    ) -> None:
        self.condition = condition
        self.true_statement = true_statement
        self.false_statement = false_statement
        self.is_constexpr = is_constexpr

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_if_statement(self)

    def accept_condition(self, visitor: Visitor) -> None:
        self.condition.accept(visitor)

    def accept_true_statement(self, visitor: Visitor) -> None:
        self.true_statement.accept(visitor)

    def accept_false_statement(self, visitor: Visitor) -> None:
        if self.false_statement is not None:
            self.false_statement.accept(visitor)


class IfConstevalStatement(Statement):

    def __init__(self, is_reversed: bool, true_statement: Statement, false_statement: Optional[Statement]) -> None:
        self.is_reversed = is_reversed
        self.true_statement = true_statement
        self.false_statement = false_statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_if_consteval_statement(self)

    def accept_true_statement(self, visitor: Visitor) -> None:
        self.true_statement.accept(visitor)

    def accept_false_statement(self, visitor: Visitor) -> None:
        if self.false_statement is not None:
            self.false_statement.accept(visitor)


class WhileStatement(Statement):

    def __init__(self, condition: "Expression", statement: Statement) -> None:
        self.condition = condition
        self.statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_while_statement(self)

    def accept_condition(self, visitor: Visitor) -> None:
        self.condition.accept(visitor)

    def accept_statement(self, visitor: Visitor) -> None:
        self.statement.accept(visitor)


class DoWhileStatement(Statement):

    def __init__(self, condition: "Expression", statement: Statement) -> None:
        self.condition = condition
        self.statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_do_while_statement(self)

    def accept_condition(self, visitor: Visitor) -> None:
        self.condition.accept(visitor)

    def accept_statement(self, visitor: Visitor) -> None:
        self.statement.accept(visitor)


class ForCondition(object):
    def accept(self, viitor: Visitor) -> None:
        raise NotImplementedError


class AmbiguousForCondition(ForCondition):

    def __init__(self, for_condition_list: List[ForCondition]) -> None:
        self.for_condition_list = for_condition_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_for_condition(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.for_condition_list[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for for_condition in self.for_condition_list:
            for_condition.accept(visitor)


class ForConditionInit(ForCondition):

    def __init__(
            self, init_statement: Statement, condition: Optional["Expression"], update: Optional["Expression"]
    ) -> None:
        self.init_statement = init_statement
        self.condition = condition
        self.update = update

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_for_condition_init(self)

    def accept_init_statement(self, visitor: Visitor) -> None:
        self.init_statement.accept(visitor)

    def accept_condition(self, visitor: Visitor) -> None:
        if self.condition is not None:
            self.condition.accept(visitor)

    def accept_update(self, visitor: Visitor) -> None:
        if self.update is not None:
            self.update.accept(visitor)


class ForConditionRange(ForCondition):

    def __init__(self, init_statement: Optional[Statement], declaration: Declaration) -> None:
        self.init_statement = init_statement
        self.declaration = declaration

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_for_condition_range(self)

    def accept_init_statement(self, visitor: Visitor) -> None:
        if self.init_statement is not None:
            self.init_statement.accept(visitor)

    def accept_declaration(self, visitor: Visitor) -> None:
        self.declaration.accept(visitor)


class ForStatement(Statement):

    def __init__(self, for_range: ForCondition, statement: Statement) -> None:
        self.for_range = for_range
        self.statement = statement

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_for_statement(self)

    def accept_for_condition(self, visitor: Visitor) -> None:
        self.for_range.accept(visitor)

    def accept_statement(self, visitor: Visitor) -> None:
        self.statement.accept(visitor)
