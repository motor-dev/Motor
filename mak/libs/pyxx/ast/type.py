from typing import List, Optional, Tuple
from . import Visitor


class TypeId(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


from .function import SimpleParameterClause


class TypeSpecifier(object):

    def __init__(self) -> None:
        self._is_identifier = False
        self._is_defining_type_specifier = True

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class ErrorTypeSpecifier(TypeSpecifier):

    def __init__(self) -> None:
        TypeSpecifier.__init__(self)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_error_type_specifier(self)


class CvQualifier(TypeSpecifier):

    def __init__(self, qualifier: str) -> None:
        TypeSpecifier.__init__(self)
        self._qualifier = qualifier
        self._is_defining_type_specifier = False

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_cv_qualifier(self)


class RefQualifier:

    def __init__(self, qualifier: str) -> None:
        self._qualifier = qualifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ref_qualifier(self)


class ExceptionSpecifier(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class ExceptionSpecifierError(ExceptionSpecifier):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_exception_specifier_error(self)


class DynamicExceptionSpecifier(ExceptionSpecifier):

    def __init__(self, type_list: List[TypeId]) -> None:
        self._type_list = type_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_dynamic_exception_specifier(self)


class AmbiguousExceptionSpecifier(ExceptionSpecifier):

    def __init__(self, exception_specifiers: List[DynamicExceptionSpecifier]):
        self._exception_specifiers = exception_specifiers

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_exception_specifier(self)

    def accept_first(self, visitor: Visitor) -> None:
        self._exception_specifiers[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for exception_specifier in self._exception_specifiers:
            exception_specifier.accept(visitor)


class NoExceptSpecifier(ExceptionSpecifier):

    def __init__(self, value: Optional["Expression"]) -> None:
        self._value = value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_noexcept_specifier(self)

    def accept_value(self, visitor: Visitor) -> None:
        if self._value is not None:
            self._value.accept(visitor)


class PrimitiveTypeSpecifier(TypeSpecifier):

    def __init__(self, type: str) -> None:
        TypeSpecifier.__init__(self)
        self._type = type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_primitive_type_specifier(self)


class PrimitiveTypeSpecifiers(object):
    CHAR = PrimitiveTypeSpecifier('char')
    WCHAR_T = PrimitiveTypeSpecifier('wchar_t')
    BOOL = PrimitiveTypeSpecifier('bool')
    SHORT = PrimitiveTypeSpecifier('short')
    INT = PrimitiveTypeSpecifier('int')
    LONG = PrimitiveTypeSpecifier('long')
    SIGNED = PrimitiveTypeSpecifier('signed')
    UNSIGNED = PrimitiveTypeSpecifier('unsigned')
    FLOAT = PrimitiveTypeSpecifier('float')
    DOUBLE = PrimitiveTypeSpecifier('double')
    VOID = PrimitiveTypeSpecifier('void')
    CHAR8_T = PrimitiveTypeSpecifier('char8_t')
    CHAR16_T = PrimitiveTypeSpecifier('char16_t')
    CHAR32_T = PrimitiveTypeSpecifier('char32_t')
    INT128 = PrimitiveTypeSpecifier('__int128')


class ElaboratedClassTypeSpecifier(TypeSpecifier):

    def __init__(self, class_type: str, attributes: List["Attribute"], name: "AbstractReference") -> None:
        TypeSpecifier.__init__(self)
        self._attributes = attributes
        self._type = class_type
        self._name = name

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_elaborated_class_type_specifier(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_name(self, visitor: Visitor) -> None:
        self._name.accept(visitor)


class ElaboratedEnumTypeSpecifier(TypeSpecifier):

    def __init__(self, enum_type: str, attributes: List["Attribute"], name: "AbstractReference"):
        TypeSpecifier.__init__(self)
        self._attributes = attributes
        self._type = enum_type
        self._name = name

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_elaborated_enum_type_specifier(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_name(self, visitor: Visitor) -> None:
        self._name.accept(visitor)


class AutoTypeSpecifier(TypeSpecifier):

    def __init__(self) -> None:
        TypeSpecifier.__init__(self)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_auto_type_specifier(self)


class DecltypeTypeSpecifier(TypeSpecifier):

    def __init__(self, decltype_kw: str, expression: "Expression") -> None:
        TypeSpecifier.__init__(self)
        self._decltype_kw = decltype_kw
        self._expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_decltype_type_specifier(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)


class DecltypeAutoTypeSpecifier(TypeSpecifier):

    def __init__(self, decltype_kw: str) -> None:
        TypeSpecifier.__init__(self)
        self._decltype_kw = decltype_kw

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_decltype_auto_type_specifier(self)


class ConstrainedTypeSpecifier(TypeSpecifier):

    def __init__(self, concept_reference: "AbstractReference", placeholder_type_specifier: TypeSpecifier) -> None:
        TypeSpecifier.__init__(self)
        self._concept_reference = concept_reference
        self._placeholder_type_specifier = placeholder_type_specifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_constrained_type_specifier(self)

    def accept_constraint(self, visitor: Visitor) -> None:
        self._concept_reference.accept(visitor)

    def accept_placeholder_type_specifier(self, visitor: Visitor) -> None:
        self._placeholder_type_specifier.accept(visitor)


class TypeSpecifierReference(TypeSpecifier):

    def __init__(self, reference: "AbstractReference") -> None:
        TypeSpecifier.__init__(self)
        self._is_identifier = True
        self._reference = reference

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_specifier_reference(self)

    def accept_reference(self, visitor: Visitor) -> None:
        self._reference.accept(visitor)


class AmbiguousTypeSpecifier(TypeSpecifier):

    def __init__(self, type_specifiers: List[TypeSpecifier]) -> None:
        self._type_specifiers = type_specifiers

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_type_specifier(self)

    def accept_first(self, visitor: Visitor) -> None:
        self._type_specifiers[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for type_specifier in self._type_specifiers:
            type_specifier.accept(visitor)


class CvQualifiers(object):
    CONST = CvQualifier('const')
    VOLATILE = CvQualifier('volatile')


class RefQualifiers(object):
    REF = RefQualifier('&')
    RREF = RefQualifier('&&')


class TypeSpecifierSeq(object):

    def __init__(self, attributes: List["Attribute"]) -> None:
        self._attributes = attributes
        self._types = []  # type: List[TypeSpecifier]
        self._qualifiers = []  # type: List[CvQualifier]

    def add(self, type_specifier: TypeSpecifier) -> None:
        if isinstance(type_specifier, CvQualifier):
            self._qualifiers.append(type_specifier)
        else:
            self._types.append(type_specifier)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_specifier_seq(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_qualifiers(self, visitor: Visitor) -> None:
        for qualifier in self._qualifiers:
            qualifier.accept(visitor)

    def accept_types(self, visitor: Visitor) -> None:
        for type in self._types:
            type.accept(visitor)


class DefiningTypeSpecifierSeq(TypeSpecifierSeq):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_defining_type_specifier_seq(self)


class DeclaratorElement(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError

    def is_method_decl(self) -> bool:
        raise NotImplementedError

    def is_element_id(self) -> bool:
        return False


class DeclaratorElementError(DeclaratorElement):

    def __init__(self, next: DeclaratorElement, is_method_decl: bool) -> None:
        self._next = next
        self._is_method_decl = is_method_decl

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_error(self)

    def accept_next(self, visitor: Visitor) -> None:
        self._next.accept(visitor)

    def is_method_decl(self) -> bool:
        return self._is_method_decl


class DeclaratorElementId(DeclaratorElement):

    def __init__(self, name: "AbstractReference", attributes: List["Attribute"]) -> None:
        self._name = name
        self._attributes = attributes

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_id(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_name(self, visitor: Visitor) -> None:
        self._name.accept(visitor)

    def is_method_decl(self) -> bool:
        return False

    def is_element_id(self) -> bool:
        return True


class DeclaratorElementPackId(DeclaratorElementId):

    def __init__(self, name: "AbstractReference", attributes: List["Attribute"]) -> None:
        DeclaratorElementId.__init__(self, name, attributes)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_pack_id(self)


class DeclaratorElementAbstract(DeclaratorElement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_abstract(self)

    def is_method_decl(self) -> bool:
        return False


class DeclaratorElementAbstractPack(DeclaratorElement):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_abstract_pack(self)

    def is_method_decl(self) -> bool:
        return False


class DeclaratorElementGroup(DeclaratorElement):

    def __init__(self, next: DeclaratorElement) -> None:
        self._next = next

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_group(self)

    def accept_next(self, visitor: Visitor) -> None:
        self._next.accept(visitor)

    def is_method_decl(self) -> bool:
        return self._next.is_method_decl()

    def is_element_id(self) -> bool:
        return self._next.is_element_id()


class DeclaratorElementPointer(DeclaratorElement):

    def __init__(
            self, next: DeclaratorElement, qualified: Optional[List[Tuple[bool, "_Id"]]], attributes: List["Attribute"],
            qualifiers: Optional[List[CvQualifier]]
    ) -> None:
        self._next = next
        self._attributes = attributes
        self._qualified = qualified
        self._qualifiers = qualifiers

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_pointer(self)

    def accept_next(self, visitor: Visitor) -> None:
        self._next.accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_qualifiers(self, visitor: Visitor) -> None:
        if self._qualifiers is not None:
            for qualifier in self._qualifiers:
                qualifier.accept(visitor)

    def is_method_decl(self) -> bool:
        return self._next.is_method_decl()


class DeclaratorElementReference(DeclaratorElement):

    def __init__(self, next: DeclaratorElement, attributes: List["Attribute"]) -> None:
        self._next = next
        self._attributes = attributes
        self._qualifiers = []  # type: List[CvQualifier]

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_reference(self)

    def accept_next(self, visitor: Visitor) -> None:
        self._next.accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def is_method_decl(self) -> bool:
        return self._next.is_method_decl()


class DeclaratorElementRValueReference(DeclaratorElement):

    def __init__(self, next: DeclaratorElement, attributes: List["Attribute"]) -> None:
        self._next = next
        self._attributes = attributes

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_rvalue_reference(self)

    def accept_next(self, visitor: Visitor) -> None:
        self._next.accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def is_method_decl(self) -> bool:
        return self._next.is_method_decl()


class DeclaratorElementArray(DeclaratorElement):

    def __init__(self, next: DeclaratorElement, size: Optional["Expression"], attributes: List["Attribute"]) -> None:
        self._next = next
        self._attributes = attributes
        self._size = size

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_array(self)

    def accept_next(self, visitor: Visitor) -> None:
        self._next.accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_size(self, visitor: Visitor) -> None:
        if self._size is not None:
            self._size.accept(visitor)

    def is_method_decl(self) -> bool:
        return self._next.is_method_decl()


class DeclaratorElementMethod(DeclaratorElement):

    def __init__(
            self, next: DeclaratorElement, parameter_clause: SimpleParameterClause,
            trailing_return_type: Optional[TypeId],
            cv_qualifiers: List[CvQualifier], ref_qualifier: Optional[RefQualifier],
            exception_qualifier: Optional[ExceptionSpecifier], attributes: List["Attribute"]
    ) -> None:
        self._next = next
        self._attributes = attributes
        self._parameter_clause = parameter_clause
        self._trailing_return_type = trailing_return_type
        self._exception_qualifier = exception_qualifier
        self._cv_qualifiers = cv_qualifiers
        self._ref_qualifier = ref_qualifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_method(self)

    def accept_next(self, visitor: Visitor) -> None:
        self._next.accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_parameter_clause(self, visitor: Visitor) -> None:
        self._parameter_clause.accept(visitor)

    def accept_cv_qualifiers(self, visitor: Visitor) -> None:
        for qualifier in self._cv_qualifiers:
            qualifier.accept(visitor)

    def accept_ref_qualifier(self, visitor: Visitor) -> None:
        if self._ref_qualifier is not None:
            self._ref_qualifier.accept(visitor)

    def accept_exception_specifier(self, visitor: Visitor) -> None:
        if self._exception_qualifier is not None:
            self._exception_qualifier.accept(visitor)

    def accept_trailing_return_type(self, visitor: Visitor) -> None:
        if self._trailing_return_type is not None:
            self._trailing_return_type.accept(visitor)

    def is_method_decl(self) -> bool:
        return self._next.is_element_id()


class Declarator(object):

    def is_method(self) -> bool:
        return False

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class AbstractDeclarator(Declarator):
    pass


class AbstractDeclaratorList(AbstractDeclarator):

    def __init__(self, declarator_element: DeclaratorElement) -> None:
        self._declarator_element = declarator_element

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_abstract_declarator_list(self)

    def accept_element(self, visitor: Visitor) -> None:
        self._declarator_element.accept(visitor)


class DeclaratorList(Declarator):

    def __init__(self, declarator_element: DeclaratorElement) -> None:
        self._declarator_element = declarator_element

    def is_method(self) -> bool:
        return self._declarator_element.is_method_decl()

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_list(self)

    def accept_element(self, visitor: Visitor) -> None:
        self._declarator_element.accept(visitor)


class AmbiguousAbstractDeclarator(AbstractDeclarator):

    def __init__(self, declarator_list: List[AbstractDeclarator]) -> None:
        self._declarator_list = declarator_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_abstract_declarator(self)

    def accept_first(self, visitor: Visitor) -> None:
        self._declarator_list[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for declarator_list in self._declarator_list:
            declarator_list.accept(visitor)


class TypeIdDeclarator(TypeId):

    def __init__(self, type_specifier_seq: TypeSpecifierSeq, declarator: Optional[AbstractDeclarator]) -> None:
        self._type_specifier_seq = type_specifier_seq
        self._declarator = declarator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_id_declarator(self)

    def accept_type_specifier_seq(self, visitor: Visitor) -> None:
        self._type_specifier_seq.accept(visitor)

    def accept_declarator(self, visitor: Visitor) -> None:
        if self._declarator is not None:
            self._declarator.accept(visitor)


class AmbiguousTypeId(TypeId):

    def __init__(self, types: List[TypeId]) -> None:
        self._types = types

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_type_id(self)

    def accept_first(self, visitor: Visitor) -> None:
        self._types[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for type in self._types:
            type.accept(visitor)


class TypeIdPack(TypeId):

    def __init__(self, type_pack: TypeId) -> None:
        self._type_pack = type_pack

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_id_pack(self)

    def accept_type_pack(self, visitor: Visitor) -> None:
        self._type_pack.accept(visitor)


from .attributes import Attribute
from .reference import AbstractReference, _Id
from .expressions import Expression
