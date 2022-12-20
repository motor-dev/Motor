from motor_typing import TYPE_CHECKING
from .declarations import Declaration


class FunctionDefinition(Declaration):

    def __init__(
        self, attribute_specifier_seq, decl_specifier_seq, declarator, requires_clause, virt_specifier_seq,
        function_body
    ):
        # type: (List[Attribute], Optional[DeclSpecifierSeq], Declarator, Optional[RequiresClause], List[VirtSpecifier], FunctionBody) -> None
        Declaration.__init__(self)
        self._attributes = attribute_specifier_seq
        self._decl_specifier_seq = decl_specifier_seq
        self._declarator = declarator
        self._requires_clause = requires_clause
        self._virt_specifier_seq = virt_specifier_seq
        self._function_body = function_body

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_function_definition(self)


class ParameterClause(object):
    pass


class SimpleParameterClause(ParameterClause):

    def __init__(self, parameter_list, variadic):
        # type: (List[Declaration], bool) -> None
        self._parameter_list = parameter_list
        self._variadic = variadic

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_simple_parameter_clause(self)


class AmbiguousParameterClause(ParameterClause):

    def __init__(self, ambiguous_parameter_clause_list):
        # type: (List[ParameterClause]) -> None
        self._ambiguous_parameter_clause_list = ambiguous_parameter_clause_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_parameter_clause(self)


class ParameterDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, decl_specifier_seq, declarator, default_value, this_specifier):
        # type: (List[Attribute], Optional[DeclSpecifierSeq], Optional[Declarator], Optional[Expression], bool) -> None
        self._attributes = attribute_specifier_seq
        self._decl_specifier_seq = decl_specifier_seq
        self._declarator = declarator
        self._default_value = default_value
        self._this_specifier = this_specifier

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_parameter_declaration(self)


class FunctionBody(object):
    pass


class TryFunctionBody(object):

    def __init__(self, statement_function_body, handler):
        # type: (StatementFunctionBody, List[ExceptionHandler]) -> None
        self._statement_function_body = statement_function_body
        self._handler = handler

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_try_function_body(self)


class PureVirtualFunctionBody(FunctionBody):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_pure_virtual_function_body(self)


class DefaultFunctionBody(FunctionBody):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_default_function_body(self)


class DeletedFunctionBody(FunctionBody):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_deleted_function_body(self)


class StatementFunctionBody(FunctionBody):

    def __init__(self, constructor_initializer, statement_list):
        # type: (Optional [List[MemberInitializer]], List[Statement]) -> None
        self._constructor_initializer = constructor_initializer
        self._statement_list = statement_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_statement_function_body(self)


class VirtSpecifier(object):
    pass


class VirtSpecifierFinal(VirtSpecifier):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_virt_specifier_final(self)


class VirtSpecifierOverride(VirtSpecifier):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_virt_specifier_override(self)


class VirtSpecifierPure(VirtSpecifier):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_virt_specifier_pure(self)


class VirtSpecifierMacro(VirtSpecifier):

    def __init__(self, specifier, arguments):
        # type: (str, Optional[List[Token]]) -> None
        self._specifier = specifier
        self._arguments = arguments

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_virt_specifier_macro(self)


if TYPE_CHECKING:
    from typing import List, Optional
    from glrp import Token
    from . import Visitor
    from .attributes import Attribute
    from .type import Declarator
    from .expressions import Expression
    from .declarations import DeclSpecifierSeq
    from .statements import Statement
    from .constraints import RequiresClause
    from .statements import ExceptionHandler
    from .klass import MemberInitializer