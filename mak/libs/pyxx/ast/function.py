from motor_typing import TYPE_CHECKING
from .declarations import Declaration


class ParameterClause(object):
    pass


class SimpleParameterClause(ParameterClause):

    def __init__(self, parameter_list, variadic):
        # type: (List[Declaration], bool) -> None
        self._parameter_list = parameter_list
        self._variadic = variadic


class AmbiguousParameterClause(ParameterClause):

    def __init__(self, ambiguous_parameter_clause_list):
        # type: (List[ParameterClause]) -> None
        self._ambiguous_parameter_clause_list = ambiguous_parameter_clause_list


class ParameterDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, decl_specifier_seq, declarator, default_value, this_specifier):
        # type: (Optional[List[Attribute]], Optional[DeclSpecifierSeq], Optional[Declarator], Optional[Expression], bool) -> None
        self._attributes = attribute_specifier_seq
        self._decl_specifier_seq = decl_specifier_seq
        self._declarator = declarator
        self._default_value = default_value
        self._this_specifier = this_specifier


if TYPE_CHECKING:
    from typing import List, Optional
    from .attributes import Attribute
    from .types import Declarator
    from .expressions import Expression
    from .declarations import DeclSpecifierSeq