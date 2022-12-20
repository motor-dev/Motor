from motor_typing import TYPE_CHECKING


class TypeSpecifier(object):

    def __init__(self):
        # type: () -> None
        self._is_identifier = False
        self._is_defining_type_specifier = True


class CvQualifier(TypeSpecifier):

    def __init__(self, qualifier):
        # type: (str) -> None
        TypeSpecifier.__init__(self)
        self._qualifier = qualifier
        self._is_defining_type_specifier = False

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_cv_qualifier(self)


class RefQualifier:

    def __init__(self, qualifier):
        # type: (str) -> None
        self._qualifier = qualifier

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ref_qualifier(self)


class ExceptionSpecifier(object):
    pass


class DynamicExceptionSpecifier(ExceptionSpecifier):

    def __init__(self, type_list):
        # type: (Optional[List[List[TypeId]]]) -> None
        self._type_list = type_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_dynamic_exception_specifier(self)


class NoExceptSpecifier(ExceptionSpecifier):

    def __init__(self, value):
        # type: (Optional[Expression]) -> None
        self._value = value

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_noexcept_specifier(self)


class PrimitiveTypeSpecifier(TypeSpecifier):

    def __init__(self, type):
        # type: (str) -> None
        TypeSpecifier.__init__(self)
        self._type = type

    def accept(self, visitor):
        # type: (Visitor) -> None
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

    def __init__(self, class_type, attributes, name):
        # type: (str, List[Attribute], Reference) -> None
        TypeSpecifier.__init__(self)
        self._attributes = attributes
        self._type = class_type
        self._name = name

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_elaborated_class_type_specifier(self)


class ElaboratedEnumTypeSpecifier(TypeSpecifier):

    def __init__(self, enum_type, attributes, name):
        # type: (str, List[Attribute], Reference) -> None
        TypeSpecifier.__init__(self)
        self._attributes = attributes
        self._type = enum_type
        self._name = name

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_elaborated_enum_type_specifier(self)


class AutoTypeSpecifier(TypeSpecifier):

    def __init__(self):
        # type: () -> None
        TypeSpecifier.__init__(self)

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_auto_type_specifier(self)


class DecltypeTypeSpecifier(TypeSpecifier):

    def __init__(self, decltype_kw, expression):
        # type: (str, Expression) -> None
        TypeSpecifier.__init__(self)
        self._decltype_kw = decltype_kw
        self._expression = expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_decltype_type_specifier(self)


class DecltypeAutoTypeSpecifier(TypeSpecifier):

    def __init__(self, decltype_kw):
        # type: (str) -> None
        TypeSpecifier.__init__(self)
        self._decltype_kw = decltype_kw

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_decltype_auto_type_specifier(self)


class ConstrainedTypeSpecifier(TypeSpecifier):

    def __init__(self, concept_reference, placeholder_type_specifier):
        # type: (Reference, TypeSpecifier) -> None
        TypeSpecifier.__init__(self)
        self._concept_reference = concept_reference
        self._placeholder_type_specifier = placeholder_type_specifier

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_constrained_type_specifier(self)


class TypeSpecifierReference(TypeSpecifier):

    def __init__(self, reference, is_typename):
        # type: (Reference, bool) -> None
        TypeSpecifier.__init__(self)
        self._is_identifier = True
        self._is_typename = is_typename
        self._reference = reference

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_type_specifier_reference(self)


class AmbiguousTypeSpecifier(TypeSpecifier):

    def __init__(self, type_specifiers):
        # type: (List[TypeSpecifier]) -> None
        self._type_specifiers = type_specifiers

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_type_specifier(self)


class CvQualifiers(object):
    CONST = CvQualifier('const')
    VOLATILE = CvQualifier('volatile')


class RefQualifiers(object):
    REF = RefQualifier('&')
    RREF = RefQualifier('&&')


class TypeSpecifierSeq(object):

    def __init__(self, attributes):
        # type: (List[Attribute]) -> None
        self._attributes = attributes
        self._types = []       # type: List[TypeSpecifier]
        self._qualifiers = []  # type: List[CvQualifier]

    def add(self, type_specifier):
        # type: (TypeSpecifier) -> None
        if isinstance(type_specifier, CvQualifier):
            self._qualifiers.insert(0, type_specifier)
        else:
            self._types.insert(0, type_specifier)

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_type_specifier_seq(self)


class DefiningTypeSpecifierSeq(TypeSpecifierSeq):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_defining_type_specifier_seq(self)


class DeclaratorElement(object):
    pass


class DeclaratorElementId(DeclaratorElement):

    def __init__(self, name, attributes):
        # type: (Reference, List[Attribute]) -> None
        self._name = name
        self._attributes = attributes

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declarator_element_id(self)


class DeclaratorElementPackId(DeclaratorElement):

    def __init__(self, name, attributes):
        # type: (Reference, List[Attribute]) -> None
        self._name = name
        self._attributes = attributes

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declarator_element_pack_id(self)


class DeclaratorElementAbstractPackId(DeclaratorElement):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declarator_element_abstract_pack_id(self)


class DeclaratorElementPointer(DeclaratorElement):

    def __init__(self, qualified, attributes, qualifiers):
        # type: (Optional[List[Tuple[bool, _Id]]], List[Attribute], Optional[List[CvQualifier]]) -> None
        self._attributes = attributes
        self._qualified = qualified
        self._qualifiers = qualifiers

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declarator_element_pointer(self)


class DeclaratorElementReference(DeclaratorElement):

    def __init__(self, attributes):
        # type: (List[Attribute]) -> None
        self._attributes = attributes
        self._qualifiers = []  # type: List[CvQualifier]

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declarator_element_reference(self)


class DeclaratorElementRValueReference(DeclaratorElement):

    def __init__(self, attributes):
        # type: (List[Attribute]) -> None
        self._attributes = attributes

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declarator_element_rvalue_reference(self)


class DeclaratorElementArray(DeclaratorElement):

    def __init__(self, size, attributes):
        # type: (Optional[Expression], List[Attribute]) -> None
        self._attributes = attributes
        self._size = size

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declarator_element_array(self)


class DeclaratorElementMethod(DeclaratorElement):

    def __init__(self, parameters, trailing_return_type, cv_qualifiers, ref_qualifier, exception_qualifier, attributes):
        # type: (SimpleParameterClause, Optional[TypeId], List[CvQualifiers], Optional[RefQualifier], Optional[ExceptionSpecifier], List[Attribute]) -> None
        self._attributes = attributes
        self._parameters = parameters
        self._trailing_return_type = trailing_return_type
        self._exception_qualifier = exception_qualifier
        self._cv_qualifiers = cv_qualifiers
        self._ref_qualifier = ref_qualifier

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declarator_element_method(self)


class TypeId(object):
    pass


class Declarator(object):
    pass


class AbstractDeclarator(Declarator):
    pass


class AbstractDeclaratorList(AbstractDeclarator):

    def __init__(self, declarator_elements):
        # type: (List[DeclaratorElement]) -> None
        self._declarator_elements = declarator_elements

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_abstract_declarator_list(self)


class DeclaratorList(Declarator):

    def __init__(self, declarator_elements):
        # type: (List[DeclaratorElement]) -> None
        self._declarator_elements = declarator_elements

    def is_method(self):
        # type: () -> bool
        return len(self._declarator_elements) >= 2 and isinstance(self._declarator_elements[1], DeclaratorElementMethod)

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declarator_list(self)


class AmbiguousAbstractDeclarator(AbstractDeclarator):

    def __init__(self, declarator_list):
        # type: (List[AbstractDeclarator]) -> None
        self._declarator_list = declarator_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_abstract_declarator(self)


class TypeIdDeclarator(TypeId):

    def __init__(self, type_specifier_seq, declarator):
        # type: (TypeSpecifierSeq, Optional[AbstractDeclarator]) -> None
        self._type_specifier_seq = type_specifier_seq
        self._declarator = declarator

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_type_id_declarator(self)


class AmbiguousTypeId(TypeId):

    def __init__(self, types):
        # type: (List[TypeId]) -> None
        self._types = types

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_type_id(self)


class TypeIdPack(TypeId):

    def __init__(self, type_pack):
        # type: (TypeId) -> None
        self._type_pack = type_pack

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_type_id_pack(self)


if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from . import Visitor
    from .attributes import Attribute
    from .reference import Reference, _Id
    from .expressions import Expression
    from .function import SimpleParameterClause