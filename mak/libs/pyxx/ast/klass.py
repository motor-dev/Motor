from .type import TypeSpecifier
from motor_typing import TYPE_CHECKING


class AccessSpecifier(object):
    pass


class AccessSpecifierDefault(AccessSpecifier):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_access_specifier_default(self)


class AccessSpecifierPublic(AccessSpecifier):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_access_specifier_public(self)


class AccessSpecifierProtected(AccessSpecifier):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_access_specifier_protected(self)


class AccessSpecifierPrivate(AccessSpecifier):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_access_specifier_private(self)


class AccessSpecifierMacro(AccessSpecifier):

    def __init__(self, macro, arguments):
        # type: (str, Optional[List[Token]]) -> None
        self._name = macro
        self._arguments = arguments

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_access_specifier_macro(self)


class ClassSpecifier(TypeSpecifier):

    def __init__(self, class_type, attribute_list, name, is_final, base_class_list, member_list):
        # type: (str, List[Attribute], Optional[Reference], bool, List[List[Tuple[AccessSpecifier, Reference]]], List[Tuple[AccessSpecifier, List[Declaration]]]) -> None
        TypeSpecifier.__init__(self)
        self._is_defining_type_specifier = True
        self._class_type = class_type
        self._attribute_list = attribute_list
        self._name = name
        self._base_class_list = base_class_list
        self._virt_specifier = is_final
        self._member_list = member_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_class_specifier(self)


class BaseSpecifier(object):

    def __init__(self, base_type, attribute_list, access_specifier, is_virtual, is_pack_expand):
        # type: (TypeSpecifier, List[Attribute], AccessSpecifier, bool, bool) -> None
        self._base_type = base_type
        self._attribute_list = attribute_list
        self._access_specifier = access_specifier
        self._is_virtual = is_virtual
        self._is_pack_expand = is_pack_expand

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_base_specifier(self)


class MemberInitializer(object):

    def __init__(self, id, value, is_pack_expand):
        # type: (MemInitializerId, Optional[Expression], bool) -> None
        self._id = id
        self._value = value
        self._is_pack_expand = is_pack_expand

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_member_initializer(self)


class MemInitializerId(object):
    pass


class MemInitializerIdMember(MemInitializerId):

    def __init__(self, member):
        # type: (str) -> None
        self._member = member

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_mem_initializer_id_member(self)


class MemInitializerIdBase(MemInitializerId):

    def __init__(self, base):
        # type: (TypeSpecifier) -> None
        self._base = base

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_mem_initializer_id_base(self)


class AmbiguousMemInitializerId(MemInitializerId):

    def __init__(self, mem_initializer_ids):
        # type: (List[MemInitializerId]) -> None
        self._mem_initializer_ids = mem_initializer_ids

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_mem_initializer_id(self)


if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from glrp import Token
    from . import Visitor
    from .type import TypeSpecifier
    from .expressions import Expression
    from .declarations import Declaration
    from .attributes import Attribute
    from .reference import Reference
