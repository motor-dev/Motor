from typing import List, Optional
from . import Visitor
from .base import Attribute, Expression
from .reference import Reference
from .type import TypeSpecifier, TypeSpecifierSeq


class Enumerator(object):

    def __init__(self, identifier: str, attributes: List[Attribute], constant_value: Optional[Expression]) -> None:
        self.name = identifier
        self.attributes = attributes
        self.value = constant_value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_enumerator(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_value(self, visitor: Visitor) -> None:
        if self.value is not None:
            self.value.accept(visitor)


class EnumSpecifier(TypeSpecifier):

    def __init__(
            self, name: Optional[Reference], attributes: List[Attribute], is_scoped: bool,
            base_type: Optional[TypeSpecifierSeq],
            enumerator_list: List[Enumerator]
    ) -> None:
        TypeSpecifier.__init__(self)
        self.name = name
        self.attributes = attributes
        self.is_scoped = is_scoped
        self.base_type = base_type
        self.enumerators = enumerator_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_enum_specifier(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_name(self, visitor: Visitor) -> None:
        if self.name is not None:
            self.name.accept(visitor)

    def accept_base_type(self, visitor: Visitor) -> None:
        if self.base_type is not None:
            self.base_type.accept(visitor)

    def accept_enumerators(self, visitor: Visitor) -> None:
        for enumerator in self.enumerators:
            enumerator.accept(visitor)
