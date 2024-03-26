from typing import List, Optional
from . import Visitor
from .base import TemplateArgument, Attribute, TypeId, Expression, Declaration
from .reference import Reference
from .constraints import RequiresClause
from .function import ParameterDeclaration


class TemplateParameter(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class AbstractTemplateParameterList:

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class TemplateParameterList(AbstractTemplateParameterList):
    def __init__(self, parameters: List[TemplateParameter]):
        self.parameters = parameters

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_parameter_list(self)

    def accept_parameters(self, visitor: Visitor) -> None:
        for parameter in self.parameters:
            parameter.accept(visitor)


class AmbiguousTemplateParameterList(AbstractTemplateParameterList):
    def __init__(self, ambiguous_parameter_list: List[List[TemplateParameter]]):
        self.parameter_lists = [TemplateParameterList(param_list) for param_list in ambiguous_parameter_list]

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_template_parameter_list(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.parameter_lists[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for parameter_list in self.parameter_lists:
            parameter_list.accept(visitor)


class TemplateDeclaration(Declaration):

    def __init__(
            self,
            parameters: List[List[TemplateParameter]],
            requires_clause: Optional["RequiresClause"],
            is_extern: bool,
            declaration: Declaration
    ) -> None:
        Declaration.__init__(self, [])
        if len(parameters) == 1:
            self.parameters = TemplateParameterList(parameters[0])  # type: AbstractTemplateParameterList
        else:
            self.parameters = AmbiguousTemplateParameterList(parameters)
        self.requires_clause = requires_clause
        self.declaration = declaration
        self.is_extern = is_extern

    def add_attributes(self, attributes: List[Attribute]) -> None:
        self.declaration.add_attributes(attributes)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_parameter_list(self, visitor: Visitor) -> None:
        self.parameters.accept(visitor)

    def accept_requires_clause(self, visitor: Visitor) -> None:
        if self.requires_clause is not None:
            self.requires_clause.accept(visitor)

    def accept_declaration(self, visitor: Visitor) -> None:
        self.declaration.accept(visitor)


class TemplateArgumentError(object):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_argument_error(self)


class TemplateArgumentPackExpand(TemplateArgument):

    def __init__(self, template_argument: TemplateArgument) -> None:
        self.template_argument = template_argument

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_argument_pack_expand(self)

    def accept_argument(self, visitor: Visitor) -> None:
        self.template_argument.accept(visitor)


class AmbiguousTemplateArgument(TemplateArgument):

    def __init__(self, template_arguments: List[TemplateArgument]) -> None:
        self.template_arguments = template_arguments

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_template_argument(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.template_arguments[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for template_argument in self.template_arguments:
            template_argument.accept(visitor)


class TemplateArgumentConstant(TemplateArgument):

    def __init__(self, constant: Expression):
        self.constant = constant

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_argument_constant(self)

    def accept_constant(self, visitor: Visitor) -> None:
        self.constant.accept(visitor)


class TemplateArgumentTypeId(TemplateArgument):

    def __init__(self, type_id: TypeId):
        self.type_id = type_id

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_argument_type_id(self)

    def accept_type_id(self, visitor: Visitor) -> None:
        self.type_id.accept(visitor)


class AmbiguousTemplateParameter(TemplateParameter):

    def __init__(self, template_parameter_list: List[TemplateParameter]) -> None:
        self.template_parameter_list = template_parameter_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_template_parameter(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.template_parameter_list[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for parameter in self.template_parameter_list:
            parameter.accept(visitor)


class TemplateParameterType(TemplateParameter):

    def __init__(self, keyword: str, name: Optional[str], default_value: Optional[TypeId], is_pack: bool) -> None:
        self.keyword = keyword
        self.name = name
        self.default_value = default_value
        self.is_pack = is_pack

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_parameter_type(self)

    def accept_default_value(self, visitor: Visitor) -> None:
        if self.default_value is not None:
            self.default_value.accept(visitor)


class TemplateParameterTemplate(TemplateParameter):

    def __init__(
            self, keyword: str, template_parameter_list: List[List[TemplateParameter]],
            requires_clause: Optional["RequiresClause"],
            name: Optional[str], default_value: Optional[Reference], is_pack: bool
    ) -> None:
        self.keyword = keyword
        if len(template_parameter_list) == 1:
            self.template_parameter_list = TemplateParameterList(
                template_parameter_list[0])  # type: AbstractTemplateParameterList
        else:
            self.template_parameter_list = AmbiguousTemplateParameterList(template_parameter_list)
        self.requires_clause = requires_clause
        self.name = name
        self.default_value = default_value
        self.is_pack = is_pack

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_parameter_template(self)

    def accept_template_parameter_list(self, visitor: Visitor) -> None:
        self.template_parameter_list.accept(visitor)

    def accept_requires_clause(self, visitor: Visitor) -> None:
        if self.requires_clause is not None:
            self.requires_clause.accept(visitor)

    def accept_default_value(self, visitor: Visitor) -> None:
        if self.default_value is not None:
            self.default_value.accept(visitor)


class TemplateParameterConstant(TemplateParameter):

    def __init__(self, parameter_declaration: "ParameterDeclaration"):
        self.parameter_declaration = parameter_declaration

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_parameter_constant(self)

    def accept_parameter_declaration(self, visitor: Visitor) -> None:
        self.parameter_declaration.accept(visitor)


class TemplateParameterConstraint(TemplateParameter):

    def __init__(
            self, constraint: Reference, name: Optional[str], default_value: Optional[Reference], is_pack: bool
    ) -> None:
        self.constraint = constraint
        self.name = name
        self.default_value = default_value
        self.is_pack = is_pack

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_parameter_constraint(self)

    def accept_constraint(self, visitor: Visitor) -> None:
        self.constraint.accept(visitor)

    def accept_default_value(self, visitor: Visitor) -> None:
        if self.default_value is not None:
            self.default_value.accept(visitor)
