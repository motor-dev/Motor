from motor_typing import TYPE_CHECKING
from .type import TypeSpecifier


class EnumSpecifier(TypeSpecifier):

    def __init__(self, name, attributes, is_scoped, base_type, enumerator_list):
        # type: (Reference, List[Attribute], bool, Optional[TypeSpecifierSeq], List[Enumerator]) -> None
        TypeSpecifier.__init__(self)
        self._name = name
        self._attributes = attributes
        self._is_scoped = is_scoped
        self._base_type = base_type
        self._enumerators = enumerator_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_enum_specifier(self)


class Enumerator(object):

    def __init__(self, identifier, attributes, constant_value):
        # type: (str, List[Attribute], Optional[Expression]) -> None
        self._name = identifier
        self._attributes = attributes
        self._value = constant_value

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_enumerator(self)


if TYPE_CHECKING:
    from typing import List, Optional
    from . import Visitor
    from .expressions import Expression
    from .attributes import Attribute
    from .reference import Reference
    from .type import TypeSpecifierSeq