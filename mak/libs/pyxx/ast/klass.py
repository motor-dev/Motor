from typing import List, Optional, Tuple
from glrp import Token
from . import Visitor
from .base import Expression, Declaration, Attribute
from .type import TypeSpecifier
from .reference import Reference


class AccessSpecifier(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class AccessSpecifierDefault(AccessSpecifier):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_access_specifier_default(self)


class AccessSpecifierPublic(AccessSpecifier):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_access_specifier_public(self)


class AccessSpecifierProtected(AccessSpecifier):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_access_specifier_protected(self)


class AccessSpecifierPrivate(AccessSpecifier):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_access_specifier_private(self)


class AccessSpecifierMacro(AccessSpecifier):

    def __init__(self, macro: str, arguments: Optional[List[Token]]) -> None:
        self.name = macro
        self.arguments = arguments

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_access_specifier_macro(self)


class BaseSpecifier(object):

    def __init__(
            self, base_type: TypeSpecifier, attribute_list: List[Attribute], access_specifier: AccessSpecifier,
            is_virtual: bool, is_pack_expand: bool
    ) -> None:
        self.base_type = base_type
        self.attribute_list = attribute_list
        self.access_specifier = access_specifier
        self.is_virtual = is_virtual
        self.is_pack_expand = is_pack_expand

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_base_specifier(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attribute_list:
            attribute.accept(visitor)

    def accept_access_specifier(self, visitor: Visitor) -> None:
        self.access_specifier.accept(visitor)

    def accept_base_type(self, visitor: Visitor) -> None:
        self.base_type.accept(visitor)


class AbstractBaseClause:

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class BaseClause(AbstractBaseClause):

    def __init__(self, base_specifiers: List[BaseSpecifier]) -> None:
        self.base_specifiers = base_specifiers

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_base_clause(self)

    def accept_base_specifiers(self, visitor: Visitor) -> None:
        for base_specifier in self.base_specifiers:
            base_specifier.accept(visitor)


class AmbiguousBaseClause(AbstractBaseClause):

    def __init__(self, base_clause_list: List[BaseClause]) -> None:
        self.base_clause_list = base_clause_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_base_clause(self)

    def accept_first_base_clause(self, visitor: Visitor) -> None:
        self.base_clause_list[0].accept(visitor)

    def accept_all_base_clause(self, visitor: Visitor) -> None:
        for base_clause in self.base_clause_list:
            base_clause.accept(visitor)


class ClassSpecifier(TypeSpecifier):

    def __init__(
            self, class_type: str, attribute_list: List[Attribute], name: Optional[Reference], is_final: bool,
            base_class_list: List[List[BaseSpecifier]], member_list: List[Tuple[AccessSpecifier, List[Declaration]]]
    ) -> None:
        TypeSpecifier.__init__(self)
        self.is_defining_type_specifier = True
        self.class_type = class_type
        self.attribute_list = attribute_list
        self.name = name
        if len(base_class_list) == 0:
            self.base_clause = None  # type: Optional[AbstractBaseClause]
        elif len(base_class_list) == 1:
            self.base_clause = BaseClause(base_class_list[0])
        else:
            self.base_clause = AmbiguousBaseClause(
                [BaseClause(x) for x in sorted(base_class_list, key=lambda l: len(l))]
            )
        self.virt_specifier = is_final
        self.member_list = member_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_class_specifier(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attribute_list:
            attribute.accept(visitor)

    def accept_name(self, visitor: Visitor) -> None:
        if self.name is not None:
            self.name.accept(visitor)

    def accept_base_clause(self, visitor: Visitor) -> None:
        if self.base_clause is not None:
            self.base_clause.accept(visitor)

    def accept_members(self, visitor: Visitor) -> None:
        for access_specifier, declarations in self.member_list:
            for declaration in declarations:
                visitor.visit_member_declaration(access_specifier, declaration)


class MemInitializerId(object):
    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class MemInitializerIdMember(MemInitializerId):

    def __init__(self, member: str) -> None:
        self.member = member

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_mem_initializer_id_member(self)


class MemInitializerIdBase(MemInitializerId):

    def __init__(self, base: TypeSpecifier) -> None:
        self.base = base

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_mem_initializer_id_base(self)

    def accept_base(self, visitor: Visitor) -> None:
        self.base.accept(visitor)


class AmbiguousMemInitializerId(MemInitializerId):

    def __init__(self, mem_initializer_ids: List[MemInitializerId]) -> None:
        self.mem_initializer_ids = mem_initializer_ids

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_mem_initializer_id(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.mem_initializer_ids[0].accept(visitor)


class AbstractMemberInitializer(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class MemberInitializerError(AbstractMemberInitializer):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_member_initializer_error(self)


class MemberInitializer(AbstractMemberInitializer):

    def __init__(self, identifier: MemInitializerId, value: Optional[Expression], is_pack_expand: bool) -> None:
        self.id = identifier
        self.value = value
        self.is_pack_expand = is_pack_expand

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_member_initializer(self)

    def accept_mem_initializer_id(self, visitor: Visitor) -> None:
        self.id.accept(visitor)

    def accept_value(self, visitor: Visitor) -> None:
        if self.value is not None:
            self.value.accept(visitor)
