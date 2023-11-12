from typing import List, Optional, Tuple, Union
from . import Visitor
from .base import Attribute, TypeId, TypeSpecifier, Declarator, ParameterClause, Expression, _Id
from .reference import AbstractReference, Reference


class ErrorTypeSpecifier(TypeSpecifier):

    def __init__(self, position: Tuple[int, int]) -> None:
        TypeSpecifier.__init__(self)
        self.position = position

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_error_type_specifier(self)


class CvQualifier(TypeSpecifier):

    def __init__(self, qualifier: str) -> None:
        TypeSpecifier.__init__(self)
        self.qualifier = qualifier
        self.is_defining_type_specifier = False

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_cv_qualifier(self)


class RefQualifier:

    def __init__(self, qualifier: str) -> None:
        self.qualifier = qualifier

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
        self.type_list = type_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_dynamic_exception_specifier(self)

    def accept_type_id_list(self, visitor: Visitor) -> None:
        for type_id in self.type_list:
            type_id.accept(visitor)


class AmbiguousExceptionSpecifier(ExceptionSpecifier):

    def __init__(self, exception_specifiers: List[DynamicExceptionSpecifier]):
        self.exception_specifiers = exception_specifiers

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_exception_specifier(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.exception_specifiers[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for exception_specifier in self.exception_specifiers:
            exception_specifier.accept(visitor)


class NoExceptSpecifier(ExceptionSpecifier):

    def __init__(self, value: Optional[Expression]) -> None:
        self.value = value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_noexcept_specifier(self)

    def accept_value(self, visitor: Visitor) -> None:
        if self.value is not None:
            self.value.accept(visitor)


class PrimitiveTypeSpecifier(TypeSpecifier):

    def __init__(self, typename: str) -> None:
        TypeSpecifier.__init__(self)
        self.typename = typename

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

    def __init__(self, class_type: str, attributes: List[Attribute], name: Reference) -> None:
        TypeSpecifier.__init__(self)
        self.attributes = attributes
        self.type = class_type
        self.name = name

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_elaborated_class_type_specifier(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_name(self, visitor: Visitor) -> None:
        self.name.accept(visitor)


class ElaboratedEnumTypeSpecifier(TypeSpecifier):

    def __init__(self, position: Tuple[int, int], is_scoped: bool, attributes: List[Attribute],
                 name: Reference):
        TypeSpecifier.__init__(self)
        self.position = position
        self.attributes = attributes
        self.is_scoped = is_scoped
        self.name = name

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_elaborated_enum_type_specifier(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_name(self, visitor: Visitor) -> None:
        self.name.accept(visitor)


class AutoTypeSpecifier(TypeSpecifier):

    def __init__(self) -> None:
        TypeSpecifier.__init__(self)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_auto_type_specifier(self)


class DecltypeTypeSpecifier(TypeSpecifier):

    def __init__(self, position: Tuple[int, int], decltype_kw: str, expression: Expression) -> None:
        TypeSpecifier.__init__(self)
        self.position = position
        self.decltype_kw = decltype_kw
        self.expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_decltype_type_specifier(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self.expression.accept(visitor)


class DecltypeSpecifierId(_Id):

    def __init__(self, decltype_specifier: Union[DecltypeTypeSpecifier, ErrorTypeSpecifier]) -> None:
        _Id.__init__(self, decltype_specifier.position)
        self.decltype_specifier = decltype_specifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_decltype_specifier_id(self)

    def accept_decltype_specifier(self, visitor: Visitor) -> None:
        self.decltype_specifier.accept(visitor)


class DecltypeAutoTypeSpecifier(TypeSpecifier):

    def __init__(self, decltype_kw: str) -> None:
        TypeSpecifier.__init__(self)
        self.decltype_kw = decltype_kw

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_decltype_auto_type_specifier(self)


class ConstrainedTypeSpecifier(TypeSpecifier):

    def __init__(self, concept_reference: AbstractReference, placeholder_type_specifier: TypeSpecifier) -> None:
        TypeSpecifier.__init__(self)
        self.concept_reference = concept_reference
        self.placeholder_type_specifier = placeholder_type_specifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_constrained_type_specifier(self)

    def accept_constraint(self, visitor: Visitor) -> None:
        self.concept_reference.accept(visitor)

    def accept_placeholder_type_specifier(self, visitor: Visitor) -> None:
        self.placeholder_type_specifier.accept(visitor)


class TypeSpecifierReference(TypeSpecifier):

    def __init__(self, reference: AbstractReference) -> None:
        TypeSpecifier.__init__(self)
        self.is_identifier = True
        self.reference = reference

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_specifier_reference(self)

    def accept_reference(self, visitor: Visitor) -> None:
        self.reference.accept(visitor)


class AmbiguousTypeSpecifier(TypeSpecifier):

    def __init__(self, type_specifiers: List[TypeSpecifier]) -> None:
        super().__init__()
        self.type_specifiers = type_specifiers

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_type_specifier(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.type_specifiers[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for type_specifier in self.type_specifiers:
            type_specifier.accept(visitor)


class CvQualifiers(object):
    CONST = CvQualifier('const')
    VOLATILE = CvQualifier('volatile')


class RefQualifiers(object):
    REF = RefQualifier('&')
    RREF = RefQualifier('&&')


class TypeSpecifierSeq(object):

    def __init__(self, attributes: List[Attribute]) -> None:
        self.attributes = attributes
        self.types = []  # type: List[TypeSpecifier]
        self.qualifiers = []  # type: List[CvQualifier]

    def add(self, type_specifier: TypeSpecifier) -> None:
        if isinstance(type_specifier, CvQualifier):
            self.qualifiers.append(type_specifier)
        else:
            self.types.append(type_specifier)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_specifier_seq(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_qualifiers(self, visitor: Visitor) -> None:
        for qualifier in self.qualifiers:
            qualifier.accept(visitor)

    def accept_types(self, visitor: Visitor) -> None:
        for type_specifier in self.types:
            type_specifier.accept(visitor)


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

    def __init__(self, successor: DeclaratorElement, is_method_decl: bool) -> None:
        self.next = successor
        self._is_method_decl = is_method_decl

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_error(self)

    def accept_next(self, visitor: Visitor) -> None:
        self.next.accept(visitor)

    def is_method_decl(self) -> bool:
        return self._is_method_decl


class DeclaratorElementId(DeclaratorElement):

    def __init__(self, name: AbstractReference, attributes: List[Attribute]) -> None:
        self.name = name
        self.attributes = attributes

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_id(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_name(self, visitor: Visitor) -> None:
        self.name.accept(visitor)

    def is_method_decl(self) -> bool:
        return False

    def is_element_id(self) -> bool:
        return True


class DeclaratorElementPackId(DeclaratorElementId):

    def __init__(self, name: AbstractReference, attributes: List[Attribute]) -> None:
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

    def __init__(self, successor: DeclaratorElement) -> None:
        self.next = successor

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_group(self)

    def accept_next(self, visitor: Visitor) -> None:
        self.next.accept(visitor)

    def is_method_decl(self) -> bool:
        return self.next.is_method_decl()

    def is_element_id(self) -> bool:
        return self.next.is_element_id()


class DeclaratorElementPointer(DeclaratorElement):

    def __init__(
            self, successor: DeclaratorElement, qualified: Optional[List[Tuple[bool, _Id]]],
            attributes: List[Attribute],
            qualifiers: Optional[List[CvQualifier]]
    ) -> None:
        self.next = successor
        self.attributes = attributes
        self.qualified = qualified
        self.qualifiers = qualifiers

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_pointer(self)

    def accept_next(self, visitor: Visitor) -> None:
        self.next.accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_qualifiers(self, visitor: Visitor) -> None:
        if self.qualifiers is not None:
            for qualifier in self.qualifiers:
                qualifier.accept(visitor)

    def is_method_decl(self) -> bool:
        return self.next.is_method_decl()


class DeclaratorElementReference(DeclaratorElement):

    def __init__(self, successor: DeclaratorElement, attributes: List[Attribute]) -> None:
        self.next = successor
        self.attributes = attributes

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_reference(self)

    def accept_next(self, visitor: Visitor) -> None:
        self.next.accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def is_method_decl(self) -> bool:
        return self.next.is_method_decl()


class DeclaratorElementRValueReference(DeclaratorElement):

    def __init__(self, successor: DeclaratorElement, attributes: List[Attribute]) -> None:
        self.next = successor
        self.attributes = attributes

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_rvalue_reference(self)

    def accept_next(self, visitor: Visitor) -> None:
        self.next.accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def is_method_decl(self) -> bool:
        return self.next.is_method_decl()


class DeclaratorElementArray(DeclaratorElement):

    def __init__(self, successor: DeclaratorElement, size: Optional[Expression],
                 attributes: List[Attribute]) -> None:
        self.next = successor
        self.attributes = attributes
        self.size = size

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_array(self)

    def accept_next(self, visitor: Visitor) -> None:
        self.next.accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_size(self, visitor: Visitor) -> None:
        if self.size is not None:
            self.size.accept(visitor)

    def is_method_decl(self) -> bool:
        return self.next.is_method_decl()


class DeclaratorElementMethod(DeclaratorElement):

    def __init__(
            self, successor: DeclaratorElement, parameter_clause: ParameterClause,
            trailing_return_type: Optional[TypeId],
            cv_qualifiers: List[CvQualifier], ref_qualifier: Optional[RefQualifier],
            exception_qualifier: Optional[ExceptionSpecifier], attributes: List[Attribute]
    ) -> None:
        self.next = successor
        self.attributes = attributes
        self.parameter_clause = parameter_clause
        self.trailing_return_type = trailing_return_type
        self.exception_qualifier = exception_qualifier
        self.cv_qualifiers = cv_qualifiers
        self.ref_qualifier = ref_qualifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_element_method(self)

    def accept_next(self, visitor: Visitor) -> None:
        self.next.accept(visitor)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_parameter_clause(self, visitor: Visitor) -> None:
        self.parameter_clause.accept(visitor)

    def accept_trailing_return_type(self, visitor: Visitor) -> None:
        if self.trailing_return_type is not None:
            self.trailing_return_type.accept(visitor)

    def accept_cv_qualifiers(self, visitor: Visitor) -> None:
        for qualifier in self.cv_qualifiers:
            qualifier.accept(visitor)

    def accept_ref_qualifier(self, visitor: Visitor) -> None:
        if self.ref_qualifier is not None:
            self.ref_qualifier.accept(visitor)

    def accept_exception_specifier(self, visitor: Visitor) -> None:
        if self.exception_qualifier is not None:
            self.exception_qualifier.accept(visitor)

    def is_method_decl(self) -> bool:
        return self.next.is_element_id()


class AbstractDeclarator(Declarator):
    pass


class AbstractDeclaratorList(AbstractDeclarator):

    def __init__(self, declarator_element: DeclaratorElement) -> None:
        self.declarator_element = declarator_element

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_abstract_declarator_list(self)

    def accept_element(self, visitor: Visitor) -> None:
        self.declarator_element.accept(visitor)


class DeclaratorList(Declarator):

    def __init__(self, declarator_element: DeclaratorElement) -> None:
        self.declarator_element = declarator_element

    def is_method(self) -> bool:
        return self.declarator_element.is_method_decl()

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declarator_list(self)

    def accept_element(self, visitor: Visitor) -> None:
        self.declarator_element.accept(visitor)


class AmbiguousAbstractDeclarator(AbstractDeclarator):

    def __init__(self, declarator_list: List[AbstractDeclarator]) -> None:
        self.declarator_list = declarator_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_abstract_declarator(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.declarator_list[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for declarator_list in self.declarator_list:
            declarator_list.accept(visitor)


class TypeIdDeclarator(TypeId):

    def __init__(self, type_specifier_seq: TypeSpecifierSeq, declarator: Optional[AbstractDeclarator]) -> None:
        self.type_specifier_seq = type_specifier_seq
        self.declarator = declarator

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_id_declarator(self)

    def accept_type_specifier_seq(self, visitor: Visitor) -> None:
        self.type_specifier_seq.accept(visitor)

    def accept_declarator(self, visitor: Visitor) -> None:
        if self.declarator is not None:
            self.declarator.accept(visitor)


class AmbiguousTypeId(TypeId):

    def __init__(self, types: List[TypeId]) -> None:
        self.types = types

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_type_id(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.types[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for type_id in self.types:
            type_id.accept(visitor)


class TypeIdPack(TypeId):

    def __init__(self, type_pack: TypeId) -> None:
        self.type_pack = type_pack

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_type_id_pack(self)

    def accept_type_pack(self, visitor: Visitor) -> None:
        self.type_pack.accept(visitor)
