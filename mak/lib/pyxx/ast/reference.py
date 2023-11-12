from typing import List, Optional, Tuple
from . import Visitor
from .base import TypeId, TemplateArgument, _Id


class AbstractReference(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class Reference(AbstractReference):

    def __init__(self, name_list: List[_Id]) -> None:
        self.name_list = name_list
        self.position = (name_list[0].position[0], name_list[-1].position[1])

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_reference(self)

    def accept_names(self, visitor: Visitor) -> None:
        for name in self.name_list:
            name.accept(visitor)

    def is_absolute(self) -> bool:
        return isinstance(self.name_list[0], RootId)


class TypenameReference(AbstractReference):

    def __init__(self, reference: AbstractReference) -> None:
        self.reference = reference

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_typename_reference(self)

    def accept_reference(self, visitor: Visitor) -> None:
        self.reference.accept(visitor)


class PackExpandReference(AbstractReference):

    def __init__(self, reference: AbstractReference) -> None:
        self.reference = reference

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_pack_expand_reference(self)

    def accept_reference(self, visitor: Visitor) -> None:
        self.reference.accept(visitor)


class TemplateSpecifierId(_Id):

    def __init__(self, position: Tuple[int, int], identifier: _Id) -> None:
        _Id.__init__(self, (position[0], identifier.position[1]))
        self.id = identifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_specifier_id(self)

    def accept_id(self, visitor: Visitor) -> None:
        self.id.accept(visitor)


class RootId(_Id):

    def __init__(self, position: Tuple[int, int]) -> None:
        _Id.__init__(self, position)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_root_id(self)


class Id(_Id):

    def __init__(self, position: Tuple[int, int], name: str) -> None:
        _Id.__init__(self, position)
        self.name = name

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_id(self)


class AbstractTemplateArgumentList:

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class TemplateArgumentList(AbstractTemplateArgumentList):

    def __init__(self, template_arguments: List["TemplateArgument"]) -> None:
        self.template_arguments = template_arguments

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_argument_list(self)

    def accept_arguments(self, visitor: Visitor) -> None:
        for argument in self.template_arguments:
            argument.accept(visitor)


class AmbiguousTemplateArgumentList(AbstractTemplateArgumentList):

    def __init__(self, template_argument_lists: List[TemplateArgumentList]) -> None:
        self.template_argument_lists = template_argument_lists

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_template_argument_list(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.template_argument_lists[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for argument_list in self.template_argument_lists:
            argument_list.accept(visitor)


class TemplateId(_Id):

    def __init__(
            self,
            closing_position: int,
            identifier: _Id,
            template_arguments: List[List["TemplateArgument"]]
    ) -> None:
        _Id.__init__(self, (identifier.position[0], closing_position))
        self.id = identifier
        if len(template_arguments) == 0:
            self.template_arguments = None  # type: Optional[AbstractTemplateArgumentList]
        elif len(template_arguments) == 1:
            self.template_arguments = TemplateArgumentList(template_arguments[0])
        else:
            self.template_arguments = AmbiguousTemplateArgumentList(
                [TemplateArgumentList(x) for x in sorted(template_arguments, key=lambda l: len(l))]
            )

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_template_id(self)

    def accept_id(self, visitor: Visitor) -> None:
        self.id.accept(visitor)

    def accept_template_arguments(self, visitor: Visitor) -> None:
        if self.template_arguments is not None:
            self.template_arguments.accept(visitor)


class DestructorId(_Id):

    def __init__(self, position: Tuple[int, int], identifier: _Id) -> None:
        _Id.__init__(self, (position[0], identifier.position[1]))
        self.id = identifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_destructor_id(self)

    def accept_id(self, visitor: Visitor) -> None:
        self.id.accept(visitor)


class OperatorId(_Id):

    def __init__(self, position: Tuple[int, int], operator: str) -> None:
        _Id.__init__(self, position)
        self.operator = operator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_operator_id(self)


class ConversionOperatorId(_Id):

    def __init__(self, position: Tuple[int, int], conversion_type: TypeId) -> None:
        _Id.__init__(self, position)
        self.conversion_type = conversion_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_conversion_operator_id(self)

    def accept_conversion_type(self, visitor: Visitor) -> None:
        self.conversion_type.accept(visitor)


class LiteralOperatorId(_Id):

    def __init__(self, position: Tuple[int, int], literal_operator: str) -> None:
        _Id.__init__(self, position)
        self.literal_operator = literal_operator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_literal_operator_id(self)
