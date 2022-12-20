from motor_typing import TYPE_CHECKING
from .declarations import Declaration


class TemplateDeclaration(Declaration):

    def __init__(self, attributes, arguments, requires_clause, is_extern, declaration):
        # type: (List[Attribute], List[List[TemplateParameter]], Optional[RequiresClause], bool, Declaration) -> None
        self._attributes = attributes
        self._arguments = arguments
        self._requires_clause = requires_clause
        self._declaration = declaration
        self._is_extern = is_extern

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_template_declaration(self)


class TemplateArgument(object):
    pass


class TemplateArgumentPackExpand(TemplateArgument):

    def __init__(self, template_argument):
        # type: (TemplateArgument) -> None
        self._template_argument = template_argument

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_template_argument_pack_expand(self)


class AmbiguousTemplateArgument(TemplateArgument):

    def __init__(self, template_arguments):
        # type: (List[TemplateArgument]) -> None
        self._template_arguments = template_arguments

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_template_argument(self)


class TemplateArgumentConstant(TemplateArgument):

    def __init__(self, constant):
        # type: (Expression) -> None
        self._constant = constant

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_template_argument_constant(self)


class TemplateArgumentTypeId(TemplateArgument):

    def __init__(self, type_id):
        # type: (TypeId) -> None
        self._type_id = type_id

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_template_argument_type_id(self)


class TemplateParameter(object):
    pass


class AmbiguousTemplateParameter(TemplateParameter):

    def __init__(self, template_parameter_list):
        # type: (List[TemplateParameter]) -> None
        self._template_parameter_list = template_parameter_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_template_parameter(self)


class TemplateParameterType(TemplateParameter):

    def __init__(self, keyword, name, default_value, is_pack):
        # type: (str, Optional[str], Optional[TypeId], bool) -> None
        self._keyword = keyword
        self._name = name
        self._default_value = default_value
        self._is_pack = is_pack

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_template_parameter_type(self)


class TemplateParameterTemplate(TemplateParameter):

    def __init__(self, keyword, template_parameters, requires_clause, name, default_value, is_pack):
        # type: (str, List[TemplateParameter], Optional[RequiresClause], Optional[str], Optional[Reference], bool) -> None
        self._keyword = keyword
        self._template_parameters = template_parameters
        self._requires_clause = requires_clause
        self._name = name
        self._default_value = default_value
        self._is_pack = is_pack

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_template_parameter_template(self)


class TemplateParameterConstant(TemplateParameter):

    def __init__(self, parameter_declaration):
        # type: (ParameterDeclaration) -> None
        self._parameter_declaration = parameter_declaration

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_template_parameter_constant(self)


class TemplateParameterConstraint(TemplateParameter):

    def __init__(self, constraint, name, default_value, is_pack):
        # type: (Reference, Optional[str], Optional[Reference], bool) -> None
        self._constraint = constraint
        self._name = name
        self._default_value = default_value
        self._is_pack = is_pack

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_template_parameter_constraint(self)


if TYPE_CHECKING:
    from typing import List, Optional
    from . import Visitor
    from .attributes import Attribute
    from .type import TypeId
    from .reference import Reference
    from .constraints import RequiresClause
    from .function import ParameterDeclaration
    from .expressions import Expression