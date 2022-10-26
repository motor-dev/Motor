from motor_typing import TYPE_CHECKING


class TypeSpecifier(object):

    def __init__(self):
        # type: () -> None
        self._is_identifier = False


class CvQualifier(TypeSpecifier):

    def __init__(self, qualifier):
        # type: (str) -> None
        TypeSpecifier.__init__(self)
        self._qualifier = qualifier


class RefQualifier(TypeSpecifier):

    def __init__(self, qualifier):
        # type: (str) -> None
        TypeSpecifier.__init__(self)
        self._qualifier = qualifier


class ExceptionSpecifier(object):
    pass


class DynamicExceptionSpecifier(ExceptionSpecifier):

    def __init__(self, type_list):
        # type: (Optional[List[TypeId]]) -> None
        self._type_list = type_list


class NoExceptSpecifier(ExceptionSpecifier):

    def __init__(self, value):
        # type: (Optional[Expression]) -> None
        self._value = value


class PrimitiveTypeSpecifier(TypeSpecifier):

    def __init__(self, type):
        # type: (str) -> None
        TypeSpecifier.__init__(self)
        self._type = type


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


class TypeSpecifierReference(TypeSpecifier):

    def __init__(self, reference, is_typename):
        # type: (Reference, bool) -> None
        TypeSpecifier.__init__(self)
        self._is_identifier = True
        self._is_typename = is_typename
        self._reference = reference


class DefiningTypeSpecifier(TypeSpecifier):

    def __init__(self, type):
        # type: (str) -> None
        TypeSpecifier.__init__(self)
        self._type = type


class CvQualifiers(object):
    CONST = CvQualifier('const')
    VOLATILE = CvQualifier('volatile')


class RefQualifiers(object):
    REF = RefQualifier('&')
    RREF = RefQualifier('&&')


class TypeSpecifierSeq(object):

    def __init__(self, attributes):
        # type: (Optional[List[Attribute]]) -> None
        self._attributes = attributes
        self._types = []       # type: List[TypeSpecifier]
        self._qualifiers = []  # type: List[CvQualifier]

    def add(self, type_specifier):
        # type: (TypeSpecifier) -> None
        if isinstance(type_specifier, CvQualifier):
            self._qualifiers.insert(0, type_specifier)
        else:
            self._types.insert(0, type_specifier)


class DefiningTypeSpecifierSeq(TypeSpecifierSeq):
    pass


class DeclaratorElement(object):
    pass


class DeclaratorElementId(DeclaratorElement):

    def __init__(self, name, attributes):
        # type: (Reference, Optional[List[Attribute]]) -> None
        self._name = name
        self._attributes = attributes


class DeclaratorElementPackId(DeclaratorElement):

    def __init__(self, name, attributes):
        # type: (Reference, Optional[List[Attribute]]) -> None
        self._name = name
        self._attributes = attributes


class DeclaratorElementAbstractPackId(DeclaratorElement):
    pass


class DeclaratorElementPointer(DeclaratorElement):

    def __init__(self, qualified, attributes, qualifiers):
        # type: (Optional[List[Tuple[bool, _Id]]], Optional[List[Attribute]], Optional[List[CvQualifier]]) -> None
        self._attributes = attributes
        self._qualified = qualified
        self._qualifiers = qualifiers


class DeclaratorElementReference(DeclaratorElement):

    def __init__(self, attributes):
        # type: (Optional[List[Attribute]]) -> None
        self._attributes = attributes
        self._qualifiers = []  # type: List[CvQualifier]


class DeclaratorElementRValueReference(DeclaratorElement):

    def __init__(self, attributes):
        # type: (Optional[List[Attribute]]) -> None
        self._attributes = attributes


class DeclaratorElementArray(DeclaratorElement):

    def __init__(self, size, attributes):
        # type: (Optional[Expression], Optional[List[Attribute]]) -> None
        self._attributes = attributes
        self._size = size


class DeclaratorElementMethod(DeclaratorElement):

    def __init__(self, parameters, trailing_return_type, cv_qualifiers, ref_qualifier, exception_qualifier, attributes):
        # type: (SimpleParameterClause, Optional[TypeId], List[CvQualifiers], Optional[RefQualifier], Any, Optional[List[Attribute]]) -> None
        self._attributes = attributes
        self._parameters = parameters
        self._trailing_return_type = trailing_return_type
        self._exception_qualifier = exception_qualifier
        self._cv_qualifiers = cv_qualifiers
        self._ref_qualifier = ref_qualifier


class TypeId(object):
    pass


class AbstractDeclarator(object):
    pass


class AbstractDeclaratorList(AbstractDeclarator):

    def __init__(self, declarator_elements):
        # type: (List[DeclaratorElement]) -> None
        self._declarator_elements = declarator_elements


class Declarator(object):
    pass


class DeclaratorList(Declarator):

    def __init__(self, declarator_elements):
        # type: (List[DeclaratorElement]) -> None
        self._declarator_elements = declarator_elements

    def is_method(self):
        # type: () -> bool
        return len(self._declarator_elements) >= 2 and isinstance(self._declarator_elements[1], DeclaratorElementMethod)


class AmbiguousAbstractDeclarator(AbstractDeclarator):

    def __init__(self, declarator_list):
        # type: (List[AbstractDeclarator]) -> None
        self._declarator_list = declarator_list


class TypeIdDeclarator(TypeId):

    def __init__(self, type_specifier_seq, declarator):
        # type: (TypeSpecifierSeq, Optional[AbstractDeclarator]) -> None
        self._type_specifier_seq = type_specifier_seq
        self._declarator = declarator


class AmbiguousTypeId(TypeId):

    def __init__(self, types):
        # type: (List[TypeId]) -> None
        self._types = types


class TypeIdPack(TypeId):

    def __init__(self, type_pack):
        # type: (TypeId) -> None
        self._type_pack = type_pack


if TYPE_CHECKING:
    from typing import Any, List, Optional, Tuple
    from .attributes import Attribute
    from .reference import Reference, _Id
    from .expressions import Expression
    from .function import SimpleParameterClause