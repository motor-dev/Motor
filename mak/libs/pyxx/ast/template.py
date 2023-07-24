from .declarations import Declaration
from typing import List, Optional
from . import Visitor
from .attributes import Attribute
from .type import TypeId
from .reference import Reference
from .function import ParameterDeclaration
from .expressions import Expression


class TemplateParameter(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class TemplateDeclaration(Declaration):

    def __init__(
            self, attributes: List[Attribute], arguments: List[List[TemplateParameter]],
            requires_clause: Optional["RequiresClause"], is_extern: bool, declaration: Declaration
    ) -> None:
        self._attributes = attributes
        self._arguments = arguments
        self._requires_clause = requires_clause
        self._declaration = declaration
        self._is_extern = is_extern

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)


class TemplateArgument(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class TemplateArgumentError(object):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_argument_error(self)


class TemplateArgumentPackExpand(TemplateArgument):

    def __init__(self, template_argument: TemplateArgument) -> None:
        self._template_argument = template_argument

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_argument_pack_expand(self)

    def accept_argument(self, visitor: Visitor) -> None:
        self._template_argument.accept(visitor)


class AmbiguousTemplateArgument(TemplateArgument):

    def __init__(self, template_arguments: List[TemplateArgument]) -> None:
        self._template_arguments = template_arguments

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_template_argument(self)

    def accept_first(self, visitor: Visitor) -> None:
        self._template_arguments[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for template_argument in self._template_arguments:
            template_argument.accept(visitor)


class TemplateArgumentConstant(TemplateArgument):

    def __init__(self, constant: Expression):
        self._constant = constant

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_argument_constant(self)

    def accept_constant(self, visitor: Visitor) -> None:
        self._constant.accept(visitor)


class TemplateArgumentTypeId(TemplateArgument):

    def __init__(self, type_id: TypeId):
        self._type_id = type_id

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_argument_type_id(self)

    def accept_type_id(self, visitor: Visitor) -> None:
        self._type_id.accept(visitor)


class AmbiguousTemplateParameter(TemplateParameter):

    def __init__(self, template_parameter_list: List[TemplateParameter]) -> None:
        self._template_parameter_list = template_parameter_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_template_parameter(self)


class TemplateParameterType(TemplateParameter):

    def __init__(self, keyword: str, name: Optional[str], default_value: Optional[TypeId], is_pack: bool) -> None:
        self._keyword = keyword
        self._name = name
        self._default_value = default_value
        self._is_pack = is_pack

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_parameter_type(self)


class TemplateParameterTemplate(TemplateParameter):

    def __init__(
            self, keyword: str, template_parameters: List[TemplateParameter],
            requires_clause: Optional["RequiresClause"],
            name: Optional[str], default_value: Optional[Reference], is_pack: bool
    ) -> None:
        self._keyword = keyword
        self._template_parameters = template_parameters
        self._requires_clause = requires_clause
        self._name = name
        self._default_value = default_value
        self._is_pack = is_pack

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_parameter_template(self)


class TemplateParameterConstant(TemplateParameter):

    def __init__(self, parameter_declaration: ParameterDeclaration):
        self._parameter_declaration = parameter_declaration

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_parameter_constant(self)


class TemplateParameterConstraint(TemplateParameter):

    def __init__(
            self, constraint: Reference, name: Optional[str], default_value: Optional[Reference], is_pack: bool
    ) -> None:
        self._constraint = constraint
        self._name = name
        self._default_value = default_value
        self._is_pack = is_pack

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_parameter_constraint(self)


from .constraints import RequiresClause
