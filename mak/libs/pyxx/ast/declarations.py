from motor_typing import TYPE_CHECKING
from .type import TypeSpecifierSeq


class Declaration(object):
    pass


class AmbiguousDeclaration(Declaration):

    def __init__(self, declarations):
        # type: (List[Declaration]) -> None
        self._declarations = declarations

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_declaration(self)


class SimpleDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, decl_specifier_seq, declarators):
        # type: (List[Attribute], Optional[DeclSpecifierSeq], Optional[_InitDeclaratorList]) -> None
        self._attributes = attribute_specifier_seq
        self._decl_specifier_seq = decl_specifier_seq
        self._declarators = declarators

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_simple_declaration(self)


class StructuredBindingDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, decl_specifier_seq, ref_qualifier, names, initializer):
        # type: (List[Attribute], Optional[DeclSpecifierSeq], Optional[RefQualifier], List[str], Expression) -> None
        self._attributes = attribute_specifier_seq
        self._decl_specifier_seq = decl_specifier_seq
        self._ref_qualifier = ref_qualifier
        self._names = names
        self._initializer = initializer

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_structured_binding_declaration(self)


class StaticAssert(Declaration):

    def __init__(self, condition, message):
        # type: (Expression, Optional[Expression]) -> None
        self._condition = condition
        self._message = message

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_static_assert(self)


class AliasDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, name, attribute_specifier_seq_alias, type_id):
        # type: (List[Attribute], str, List[Attribute], TypeId) -> None
        self._attributes = attribute_specifier_seq
        self._alias = name
        self._alias_attributes = attribute_specifier_seq_alias
        self._type_id = type_id

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_alias_declaration(self)


class NamespaceDeclaration(Declaration):

    def __init__(
        self, attribute_specifier_seq, attribute_specifier_seq_namespace, attribute_specifier_seq_namespace_identifier,
        inline, nested_name, namespace_name, declaration_seq
    ):
        # type: (List[Attribute], List[Attribute], List[Attribute], bool, Optional[List[Tuple[bool, str]]], Optional[str], List[Declaration]) -> None
        self._attributes = attribute_specifier_seq
        self._attributes_namespace = attribute_specifier_seq_namespace + attribute_specifier_seq_namespace_identifier
        self._inline = inline
        self._nested_name = nested_name
        self._namespace_name = namespace_name
        self._declaration_seq = declaration_seq

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_namespace_declaration(self)


class NamespaceAliasDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, attribute_specifier_seq_namespace, alias_name, target_name):
        # type: (List[Attribute], List[Attribute], str, Reference) -> None
        self._attributes = attribute_specifier_seq
        self._attributes_namespace = attribute_specifier_seq_namespace
        self._alias_name = alias_name
        self._target_name = target_name

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_namespace_alias_declaration(self)


class UsingDirective(Declaration):

    def __init__(self, attribute_specifier_seq, reference):
        # type: (List[Attribute], Reference) -> None
        self._attributes = attribute_specifier_seq
        self._reference = reference

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_using_directive(self)


class UsingDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, references):
        # type: (List[Attribute], List[Tuple[bool, bool, Reference]]) -> None
        self._attributes = attribute_specifier_seq
        self._references = references

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_using_declaration(self)


class UsingEnumDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, enum_specifier):
        # type: (List[Attribute], ElaboratedEnumTypeSpecifier) -> None
        self._attributes = attribute_specifier_seq
        self._enum_specifier = enum_specifier

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_using_enum_declaration(self)


class AsmDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, asm_string):
        # type: (List[Attribute], str) -> None
        self._attributes = attribute_specifier_seq
        self._asm_string = asm_string

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_asm_declaration(self)


class LinkageSpecification(Declaration):

    def __init__(self, attribute_specifier_seq, linkage_type, declaration_seq):
        # type: (List[Attribute], str, List[Declaration]) -> None
        self._attributes = attribute_specifier_seq
        self._linkage_type = linkage_type
        self._declaration_seq = declaration_seq

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_linkage_specification(self)


class OpaqueEnumDeclaration(Declaration):

    def __init__(self, name, decl_attributes, attributes, is_scoped, base_type):
        # type: (Reference, List[Attribute], List[Attribute], bool, Optional[TypeSpecifierSeq]) -> None
        self._name = name
        self._attributes = decl_attributes + attributes
        self._is_scoped = is_scoped
        self._base_type = base_type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_opaque_enum_declaration(self)


class _InitDeclarator(object):
    pass


class AmbiguousInitDeclarator(_InitDeclarator):

    def __init__(self, init_declarators):
        # type: (List[InitDeclarator]) -> None
        self.init_declarators = init_declarators

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_init_declarator(self)


class InitDeclarator(_InitDeclarator):

    def __init__(self, declarator, init_value, constraint):
        # type: (Optional[Declarator], Optional[Expression], Optional[RequiresClause]) -> None
        self._declarator = declarator
        self._init_value = init_value
        self._constraint = constraint

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_init_declarator(self)


class MemberInitDeclarator(InitDeclarator):

    def __init__(self, declarator, init_value, constraint, virt_specifier_seq, bitfield_width):
        # type: (Optional[Declarator], Optional[Expression], Optional[RequiresClause], List[VirtSpecifier], Optional[Expression]) -> None
        InitDeclarator.__init__(self, declarator, init_value, constraint)
        self._virt_specifier_seq = virt_specifier_seq
        self._bitfield_width = bitfield_width

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_member_init_declarator(self)


class _InitDeclaratorList:

    def __init__(self):
        # type: () -> None
        self._next = None  # type: Optional[_InitDeclarator]

    def add(self, init_declarator):
        # type: (_InitDeclarator) -> _InitDeclaratorList
        return InitDeclaratorList(init_declarator, self)


class InitDeclaratorList(_InitDeclaratorList):

    def __init__(self, init_declarator, head=None):
        # type: (_InitDeclarator, Optional[_InitDeclaratorList]) -> None
        self._head = head
        self._init_declarator = init_declarator

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_init_declarator_list(self)


class AmbiguousInitDeclaratorList(_InitDeclaratorList):

    def __init__(self, ambigous_init_declarator_lists):
        # type: (List[_InitDeclaratorList]) -> None
        self._init_declarator_lists = ambigous_init_declarator_lists

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_init_declarator_list(self)


class DeclSpecifierSeq(object):

    def __init__(self, attribute_specifier_seq):
        # type: (List[Attribute]) -> None
        self._decl_specifiers = []     # type: List[DeclarationSpecifier]
        self._type_specifier_seq = TypeSpecifierSeq(attribute_specifier_seq)
        self._has_defining_type_specifier = False

    def add_decl_specifier(self, specifier):
        # type: (DeclarationSpecifier) -> None
        self._decl_specifiers.insert(0, specifier)

    def add_type_specifier(self, specifier):
        # type: (TypeSpecifier) -> None
        if specifier is None:
            return
        if self._has_defining_type_specifier and specifier._is_identifier:
            # Identifier is part of the declarator, kill this branch
            raise SyntaxError
        self._has_defining_type_specifier = specifier._is_defining_type_specifier
        self._type_specifier_seq.add(specifier)

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_decl_specifier_seq(self)


class DeclarationSpecifier(object):

    def __init__(self, decl_specifier):
        # type: (str) -> None
        self._decl_specifier = decl_specifier

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declaration_specifier(self)


class DeclarationSpecifierMacro(DeclarationSpecifier):

    def __init__(self, decl_specifier, values):
        # type: (str, Optional[List[Token]]) -> None
        DeclarationSpecifier.__init__(self, decl_specifier)
        self._values = values

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_declaration_specifier_macro(self)


class StorageClassSpecifier(DeclarationSpecifier):

    def __init__(self, storage_class_specifier):
        # type: (str) -> None
        DeclarationSpecifier.__init__(self, storage_class_specifier)

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_storage_class_specifier(self)


class StorageClassSpecifierMacro(StorageClassSpecifier):

    def __init__(self, storage_class_specifier, values):
        # type: (str, Optional[List[Token]]) -> None
        StorageClassSpecifier.__init__(self, storage_class_specifier)
        self._values = values

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_storage_class_specifier_macro(self)


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

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_explicit_specifier(self)


class ConceptDefinition(Declaration):

    def __init__(self, name, constraint_expression):
        # type: (str, Expression) -> None
        self._name = name
        self._constraint_expression = constraint_expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_concept_definition(self)


class ExplicitSpecialization(Declaration):

    def __init__(self, declaration):
        # type: (Declaration) -> None
        self._declaration = declaration

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_explicit_specialization(self)


class ExplicitInstantiation(Declaration):

    def __init__(self, declaration, is_extern):
        # type: (Declaration, bool) -> None
        self._declaration = declaration
        self._is_extern = is_extern

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_explicit_instantiation(self)


class DeductionGuide(Declaration):

    def __init__(self, attributes, name, explicit_specifier, parameter_clause, template_id):
        # type: (List[Attribute], str, Optional[ExplicitSpecifier], ParameterClause, TemplateId) -> None
        self._attributes = attributes
        self._name = name
        self._explicit_specifier = explicit_specifier
        self._parameter_clause = parameter_clause
        self._template_id = template_id

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_deduction_guide(self)


if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from . import Visitor
    from .attributes import Attribute
    from .type import Declarator, TypeSpecifier, RefQualifier, TypeId, ElaboratedEnumTypeSpecifier
    from .expressions import Expression
    from .reference import Reference, TemplateId
    from .constraints import RequiresClause
    from .function import VirtSpecifier
    from .function import ParameterClause
    from glrp import Token