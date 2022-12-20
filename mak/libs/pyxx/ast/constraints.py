from .expressions import Expression
from motor_typing import TYPE_CHECKING


class RequiresExpression(Expression):

    def __init__(self, parameter_clause, requirement_body):
        # type: (Optional[ParameterClause], RequirementBody) -> None
        self._parameter_clause = parameter_clause
        self._requirement_body = requirement_body

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_requires_expression(self)


class RequirementBody(object):

    def __init__(self, requirement_list):
        # type: (List[Requirement]) -> None
        self._requirement_list = requirement_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_requirement_body(self)


class Requirement(object):
    pass


class AmbiguousRequirement(Requirement):

    def __init__(self, ambiguous_requirements):
        # type: (List[Requirement]) -> None
        self._ambiguous_requirements = ambiguous_requirements

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_requirement(self)


class SimpleRequirement(Requirement):

    def __init__(self, expression):
        # type: (Expression) -> None
        self._expression = expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_simple_requirement(self)


class TypeRequirement(Requirement):

    def __init__(self, type):
        # type: (TypeSpecifierReference) -> None
        self._type = type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_type_requirement(self)


class CompoundRequirement(Requirement):

    def __init__(self, expression, noexcept, type_constraint):
        # type: (Expression, bool, TypeRequirement) -> None
        self._expression = expression
        self._noexcept = noexcept
        self._type_constraint = type_constraint

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_compound_requirement(self)


class NestedRequirement(Requirement):

    def __init__(self, expression):
        # type: (Expression) -> None
        self._expression = expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_nested_requirement(self)


class RequiresClause(object):

    def __init__(self, requirement_expression):
        # type: (Expression) -> None
        self._requirement_expression = requirement_expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_requires_clause(self)


if TYPE_CHECKING:
    from typing import List, Optional
    from . import Visitor
    from .function import ParameterClause
    from .type import TypeSpecifierReference