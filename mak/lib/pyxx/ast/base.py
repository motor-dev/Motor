from . import Visitor
from typing import List, Tuple


class Attribute(object):

    def __init__(self, position: Tuple[int, int]) -> None:
        self.position = position
        self._is_extended_attribute = False

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError

    def is_extended(self) -> bool:
        return self._is_extended_attribute


class Declaration(object):

    def __init__(self, attributes: List[Attribute]) -> None:
        self.attributes = attributes

    def declared_entity_count(self) -> int:
        return 1

    def declared_entity_position(self, index: int) -> Tuple[int, int]:
        return (0, 0)

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def add_attributes(self, attributes: List[Attribute]) -> None:
        self.attributes = attributes + self.attributes


class TypeId(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class Expression(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class TypeSpecifier(object):

    def __init__(self) -> None:
        self.is_identifier = False
        self.is_defining_type_specifier = True

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class ParameterClause(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class Declarator(object):

    def is_method(self) -> bool:
        return False

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class _Id(object):
    def __init__(self, position: Tuple[int, int]):
        self.position = position

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class TemplateArgument(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError
