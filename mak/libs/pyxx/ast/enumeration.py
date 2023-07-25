from .type import TypeSpecifier
from typing import List, Optional
from . import Visitor
from .expressions import Expression
from .attributes import Attribute
from .reference import Reference
from .type import TypeSpecifierSeq


class Enumerator(object):

    def __init__(self, identifier: str, attributes: List[Attribute], constant_value: Optional[Expression]) -> None:
        self._name = identifier
        self._attributes = attributes
        self._value = constant_value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_enumerator(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_value(self, visitor: Visitor) -> None:
        if self._value is not None:
            self._value.accept(visitor)


class EnumSpecifier(TypeSpecifier):

    def __init__(
            self, name: Optional[Reference], attributes: List[Attribute], is_scoped: bool,
            base_type: Optional[TypeSpecifierSeq],
            enumerator_list: List[Enumerator]
    ) -> None:
        TypeSpecifier.__init__(self)
        self._name = name
        self._attributes = attributes
        self._is_scoped = is_scoped
        self._base_type = base_type
        self._enumerators = enumerator_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_enum_specifier(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_name(self, visitor: Visitor) -> None:
        if self._name is not None:
            self._name.accept(visitor)

    def accept_base_type(self, visitor: Visitor) -> None:
        if self._base_type is not None:
            self._base_type.accept(visitor)

    def accept_enumerators(self, visitor: Visitor) -> None:
        for enumerator in self._enumerators:
            enumerator.accept(visitor)
