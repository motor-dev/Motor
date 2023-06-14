from . import Visitor
from typing import List, Optional


class _Id(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class AbstractReference(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class Reference(AbstractReference):

    def __init__(self, name_list: List[_Id]) -> None:
        self._name_list = name_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_reference(self)

    def accept_names(self, visitor: Visitor) -> None:
        for name in self._name_list:
            name.accept(visitor)

    def is_absolute(self) -> bool:
        return isinstance(self._name_list[0], RootId)


class TypenameReference(AbstractReference):

    def __init__(self, reference: AbstractReference) -> None:
        self._reference = reference

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_typename_reference(self)

    def accept_reference(self, visitor: Visitor) -> None:
        self._reference.accept(visitor)


class PackExpandReference(AbstractReference):

    def __init__(self, reference: AbstractReference) -> None:
        self._reference = reference

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_pack_expand_reference(self)

    def accept_reference(self, visitor: Visitor) -> None:
        self._reference.accept(visitor)


from .type import TypeId
from .template import TemplateArgument


class TemplateSpecifierId(_Id):

    def __init__(self, id: _Id) -> None:
        self._id = id

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_specifier_id(self)

    def accept_id(self, visitor: Visitor) -> None:
        self._id.accept(visitor)


class RootId(_Id):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_root_id(self)


class Id(_Id):

    def __init__(self, name: str) -> None:
        self._name = name

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_id(self)


class AbstractTemplateArgumentList:

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class TemplateArgumentList(AbstractTemplateArgumentList):

    def __init__(self, template_arguments: List["TemplateArgument"]) -> None:
        self._template_arguments = template_arguments

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_argument_list(self)

    def accept_arguments(self, visitor: Visitor) -> None:
        for argument in self._template_arguments:
            argument.accept(visitor)


class AmbiguousTemplateArgumentList(AbstractTemplateArgumentList):

    def __init__(self, template_argument_lists: List[TemplateArgumentList]) -> None:
        self._template_argument_lists = template_argument_lists

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_template_argument_list(self)

    def accept_first(self, visitor: Visitor) -> None:
        self._template_argument_lists[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for argument_list in self._template_argument_lists:
            argument_list.accept(visitor)


class TemplateId(_Id):

    def __init__(self, id: _Id, template_arguments: List[List["TemplateArgument"]]) -> None:
        self._id = id
        if len(template_arguments) == 0:
            self._template_arguments = None  # type: Optional[AbstractTemplateArgumentList]
        elif len(template_arguments) == 1:
            self._template_arguments = TemplateArgumentList(template_arguments[0])
        else:
            self._template_arguments = AmbiguousTemplateArgumentList(
                [TemplateArgumentList(x) for x in sorted(template_arguments, key=lambda l: len(l))]
            )

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_id(self)

    def accept_id(self, visitor: Visitor) -> None:
        self._id.accept(visitor)

    def accept_template_arguments(self, visitor: Visitor) -> None:
        if self._template_arguments is not None:
            self._template_arguments.accept(visitor)


class DestructorId(_Id):

    def __init__(self, id: _Id) -> None:
        self._id = id

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_destructor_id(self)


class OperatorId(_Id):

    def __init__(self, operator: str) -> None:
        self._operator = operator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_operator_id(self)


class ConversionOperatorId(_Id):

    def __init__(self, conversion_type: TypeId) -> None:
        self._conversion_type = conversion_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_conversion_operator_id(self)

    def accept_conversion_type(self, visitor: Visitor) -> None:
        self._conversion_type.accept(visitor)


class LiteralOperatorId(_Id):

    def __init__(self, literal_operator: str) -> None:
        self._literal_operator = literal_operator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_literal_operator_id(self)
