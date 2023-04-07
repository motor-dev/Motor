from typing import List, Optional
from . import Visitor
from .expressions import Expression


class Requirement(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class ErrorRequirement(Requirement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_error_requirement(self)


class RequirementBody(object):

    def __init__(self, requirement_list: List[Requirement]) -> None:
        self._requirement_list = requirement_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_requirement_body(self)

    def accept_children(self, visitor: Visitor) -> None:
        for requirement in self._requirement_list:
            requirement.accept(visitor)


class AmbiguousRequirement(Requirement):

    def __init__(self, ambiguous_requirements: List[Requirement]):
        self._ambiguous_requirements = ambiguous_requirements

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_requirement(self)

    def accept_first(self, visitor: Visitor) -> None:
        self._ambiguous_requirements[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for requirement in self._ambiguous_requirements:
            requirement.accept(visitor)


class SimpleRequirement(Requirement):

    def __init__(self, expression: Expression):
        self._expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_simple_requirement(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)


class TypeRequirement(Requirement):

    def __init__(self, type: "TypeSpecifierReference") -> None:
        self._type = type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_requirement(self)

    def accept_type(self, visitor: Visitor) -> None:
        self._type.accept(visitor)


class CompoundRequirement(Requirement):

    def __init__(self, expression: Expression, noexcept: bool, type_constraint: TypeRequirement) -> None:
        self._expression = expression
        self._noexcept = noexcept
        self._type_constraint = type_constraint

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_compound_requirement(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)

    def accept_type_constraint(self, visitor: Visitor) -> None:
        self._type_constraint.accept(visitor)


class NestedRequirement(Requirement):

    def __init__(self, expression: Expression):
        self._expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_nested_requirement(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)


class RequiresExpression(Expression):

    def __init__(self, parameter_clause: Optional["ParameterClause"], requirement_body: RequirementBody) -> None:
        self._parameter_clause = parameter_clause
        self._requirement_body = requirement_body

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_requires_expression(self)

    def accept_parameter_clause(self, visitor: Visitor) -> None:
        if self._parameter_clause is not None:
            self._parameter_clause.accept(visitor)

    def accept_requirement_body(self, visitor: Visitor) -> None:
        self._requirement_body.accept(visitor)


class RequiresClause(object):

    def __init__(self, requirement_expression: Expression):
        self._requirement_expression = requirement_expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_requires_clause(self)

    def accept_requirement_expression(self, visitor: Visitor) -> None:
        self._requirement_expression.accept(visitor)


from .function import ParameterClause
from .type import TypeSpecifierReference
