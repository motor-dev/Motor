from . import Visitor
from typing import Tuple


class Declaration(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class Attribute(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


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
