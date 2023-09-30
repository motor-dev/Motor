from typing import List, Optional
from glrp import Token
from . import Visitor
from .base import Declaration, ParameterClause, Attribute, Declarator, Expression
from .statements import CompoundStatement, ExceptionHandler
from .constraints import RequiresClause
from .klass import MemberInitializer


class FunctionDefinition(Declaration):

    def __init__(
            self, attribute_specifier_seq: List[Attribute], decl_specifier_seq: Optional["DeclSpecifierSeq"],
            declarator: Declarator, requires_clause: Optional[RequiresClause],
            virt_specifier_seq: List["VirtSpecifier"],
            function_body: "FunctionBody"
    ) -> None:
        Declaration.__init__(self)
        self.attributes = attribute_specifier_seq
        self.decl_specifier_seq = decl_specifier_seq
        self.declarator = declarator
        self.requires_clause = requires_clause
        self.virt_specifier_seq = virt_specifier_seq
        self.function_body = function_body

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_function_definition(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_decl_specifier_seq(self, visitor: Visitor) -> None:
        if self.decl_specifier_seq is not None:
            self.decl_specifier_seq.accept(visitor)

    def accept_declarator(self, visitor: Visitor) -> None:
        self.declarator.accept(visitor)

    def accept_requires_clause(self, visitor: Visitor) -> None:
        if self.requires_clause is not None:
            self.requires_clause.accept(visitor)

    def accept_virt_specifier_seq(self, visitor: Visitor) -> None:
        for virt_specifier in self.virt_specifier_seq:
            virt_specifier.accept(visitor)

    def accept_function_body(self, visitor: Visitor) -> None:
        self.function_body.accept(visitor)


class ParameterDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq: List[Attribute], decl_specifier_seq: Optional["DeclSpecifierSeq"],
                 declarator: Optional[Declarator], default_value: Optional[Expression],
                 this_specifier: bool) -> None:
        self.attributes = attribute_specifier_seq
        self.decl_specifier_seq = decl_specifier_seq
        self.declarator = declarator
        self.default_value = default_value
        self.this_specifier = this_specifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_parameter_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_decl_specifier_seq(self, visitor: Visitor) -> None:
        if self.decl_specifier_seq is not None:
            self.decl_specifier_seq.accept(visitor)

    def accept_declarator(self, visitor: Visitor) -> None:
        if self.declarator is not None:
            self.declarator.accept(visitor)

    def accept_default_value(self, visitor: Visitor) -> None:
        if self.default_value:
            self.default_value.accept(visitor)


class SimpleParameterClause(ParameterClause):

    def __init__(self, parameter_list: List[ParameterDeclaration], variadic: bool) -> None:
        self.parameter_list = parameter_list
        self.variadic = variadic

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_simple_parameter_clause(self)

    def accept_parameter_list(self, visitor: Visitor) -> None:
        for parameter in self.parameter_list:
            parameter.accept(visitor)


class AmbiguousParameterClause(ParameterClause):

    def __init__(self, ambiguous_parameter_clause_list: List[ParameterClause]) -> None:
        self.ambiguous_parameter_clause_list = ambiguous_parameter_clause_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_parameter_clause(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.ambiguous_parameter_clause_list[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for parameter_clause in self.ambiguous_parameter_clause_list:
            parameter_clause.accept(visitor)


class FunctionBody(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class TryFunctionBody(object):

    def __init__(self, statement_function_body: "StatementFunctionBody",
                 handler_list: List[ExceptionHandler]) -> None:
        self.statement_function_body = statement_function_body
        self.handler_list = handler_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_try_function_body(self)

    def accept_statement_function_body(self, visitor: Visitor) -> None:
        self.statement_function_body.accept(visitor)

    def accept_handler_list(self, visitor: Visitor) -> None:
        for handler in self.handler_list:
            handler.accept(visitor)


class PureVirtualFunctionBody(FunctionBody):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_pure_virtual_function_body(self)


class DefaultFunctionBody(FunctionBody):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_default_function_body(self)


class DeletedFunctionBody(FunctionBody):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_deleted_function_body(self)


class StatementFunctionBody(FunctionBody):

    def __init__(self, constructor_initializer_list: Optional[List[MemberInitializer]],
                 statement_list: CompoundStatement) -> None:
        self.constructor_initializer_list = constructor_initializer_list
        self.statement_list = statement_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_statement_function_body(self)

    def accept_constructor_initializer(self, visitor: Visitor) -> None:
        if self.constructor_initializer_list is not None:
            for constructor_initializer in self.constructor_initializer_list:
                constructor_initializer.accept(visitor)

    def accept_statement_list(self, visitor: Visitor) -> None:
        self.statement_list.accept(visitor)


class VirtSpecifier(object):
    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class VirtSpecifierFinal(VirtSpecifier):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_virt_specifier_final(self)


class VirtSpecifierOverride(VirtSpecifier):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_virt_specifier_override(self)


class VirtSpecifierPure(VirtSpecifier):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_virt_specifier_pure(self)


class VirtSpecifierMacro(VirtSpecifier):

    def __init__(self, specifier: str, arguments: Optional[List[Token]]) -> None:
        self.specifier = specifier
        self.arguments = arguments

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_virt_specifier_macro(self)


from .declarations import DeclSpecifierSeq
