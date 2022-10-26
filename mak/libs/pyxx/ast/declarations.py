from motor_typing import TYPE_CHECKING
from .types import TypeSpecifierSeq


class Declaration(object):
    pass


class AmbiguousDeclaration(Declaration):

    def __init__(self, declarations):
        # type: (List[Declaration]) -> None
        self._declarations = declarations


class SimpleDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, decl_specifier_seq, declarators):
        # type: (Optional[List[Attribute]], Optional[DeclSpecifierSeq], List[_InitDeclarator]) -> None
        self._attributes = attribute_specifier_seq
        self._decl_specifier_seq = decl_specifier_seq
        self._declarators = declarators


class StructuredBindingDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, decl_specifier_seq, ref_qualifier, names, initializer):
        # type: (Optional[List[Attribute]], Optional[DeclSpecifierSeq], Optional[RefQualifier], List[str], Expression) -> None
        self._attributes = attribute_specifier_seq
        self._decl_specifier_seq = decl_specifier_seq
        self._ref_qualifier = ref_qualifier
        self._names = names
        self._initializer = initializer


class StaticAssert(Declaration):

    def __init__(self, condition, message):
        # type: (Expression, Optional[Expression]) -> None
        self._condition = condition
        self._message = message


class AliasDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, name, attribute_specifier_seq_alias, type_id):
        # type: (Optional[List[Attribute]], str, Optional[List[Attribute]], TypeId) -> None
        self._attributes = attribute_specifier_seq
        self._alias = name
        self._alias_attributes = attribute_specifier_seq_alias
        self._type_id = type_id


class NamespaceDeclaration(Declaration):

    def __init__(
        self, attribute_specifier_seq, attribute_specifier_seq_namespace, attribute_specifier_seq_namespace_identifier,
        inline, nested_name, namespace_name, declaration_seq
    ):
        # type: (Optional[List[Attribute]], Optional[List[Attribute]], Optional[List[Attribute]], bool, Optional[List[Tuple[bool, str]]], Optional[str], List[Declaration]) -> None
        self._attributes = attribute_specifier_seq
        self._attributes_namespace = attribute_specifier_seq_namespace
        self._inline = inline
        self._nested_name = nested_name
        self._namespace_name = namespace_name
        self._declaration_seq = declaration_seq


class NamespaceAliasDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, attribute_specifier_seq_namespace, alias_name, target_name):
        # type: (Optional[List[Attribute]], Optional[List[Attribute]], str, Reference) -> None
        self._attributes = attribute_specifier_seq
        self._attributes_namespace = attribute_specifier_seq_namespace
        self._alias_name = alias_name
        self._target_name = target_name


class UsingDirective(Declaration):

    def __init__(self, attribute_specifier_seq, reference):
        # type: (Optional[List[Attribute]], Reference) -> None
        self._attributes = attribute_specifier_seq
        self._reference = reference


class AsmDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, asm_string):
        # type: (Optional[List[Attribute]], str) -> None
        self._attributes = attribute_specifier_seq
        self._asm_string = asm_string


class _InitDeclarator(object):
    pass


class AmbiguousInitDeclarator(_InitDeclarator):

    def __init__(self, init_declarators):
        # type: (List[InitDeclarator]) -> None
        self.init_declarators = init_declarators


class InitDeclarator(_InitDeclarator):

    def __init__(self, declarator, init_value, constraint):
        # type: (Declarator, Optional[Expression], Optional[Any]) -> None
        self._declarator = declarator
        self._init_value = init_value
        self._constraint = constraint


class DeclSpecifierSeq(object):

    def __init__(self, attribute_specifier_seq):
        # type: (Optional[List[Attribute]]) -> None
        self._decl_specifiers = []     # type: List[DeclarationSpecifier]
        self._type_specifier_seq = TypeSpecifierSeq(attribute_specifier_seq)
        self._has_identifier = False

    def add_decl_specifier(self, specifier):
        # type: (DeclarationSpecifier) -> None
        self._decl_specifiers.insert(0, specifier)

    def add_type_specifier(self, specifier):
        # type: (TypeSpecifier) -> None
        if specifier is None:
            return
        if self._has_identifier and specifier._is_identifier:
            raise SyntaxError
        self._has_identifier = specifier._is_identifier
        self._type_specifier_seq.add(specifier)


class DeclarationSpecifier(object):

    def __init__(self, decl_specifier):
        # type: (str) -> None
        self._decl_specifier = decl_specifier


class DeclarationSpecifierMacro(DeclarationSpecifier):

    def __init__(self, decl_specifier, values):
        # type: (str, Optional[List[Any]]) -> None
        DeclarationSpecifier.__init__(self, decl_specifier)
        self._values = values


class StorageClassSpecifier(DeclarationSpecifier):

    def __init__(self, storage_class_specifier):
        # type: (str) -> None
        DeclarationSpecifier.__init__(self, storage_class_specifier)


class StorageClassSpecifierMacro(StorageClassSpecifier):

    def __init__(self, storage_class_specifier, values):
        # type: (str, Optional[List[Any]]) -> None
        StorageClassSpecifier.__init__(self, storage_class_specifier)
        self._values = values


class StorageClassSpecifiers(object):

    STATIC = StorageClassSpecifier('static')
    EXTERN = StorageClassSpecifier('extern')
    MUTABLE = StorageClassSpecifier('mutable')
    THREAD_LOCAL = StorageClassSpecifier('thread_local')
    AUTO = StorageClassSpecifier('auto')
    REGISTER = StorageClassSpecifier('register')


class DeclarationSpecifiers(object):
    TYPEDEF = DeclarationSpecifier('typedef')
    FRIEND = DeclarationSpecifier('friend')
    CONSTEXPR = DeclarationSpecifier('constexpr')
    CONSTEVAL = DeclarationSpecifier('consteval')
    CONSTINIT = DeclarationSpecifier('constinit')
    INLINE = DeclarationSpecifier('inline')


class FunctionSpecifiers(object):
    VIRTUAL = DeclarationSpecifier('virtual')
    EXPLICIT = DeclarationSpecifier('explicit')


class ExplicitSpecifier(DeclarationSpecifier):

    def __init__(self, value):
        # type: (Optional[Expression]) -> None
        DeclarationSpecifier.__init__(self, 'explicit')
        self._value = value


if TYPE_CHECKING:
    from typing import List, Optional, Any, Tuple
    from .attributes import Attribute
    from .types import Declarator, TypeSpecifier, RefQualifier, TypeId
    from .expressions import Expression
    from .reference import Reference