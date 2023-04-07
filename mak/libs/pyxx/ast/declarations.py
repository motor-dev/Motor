class Declaration(object):

    def accept(self, visitor):
        # type: (Visitor) -> None
        raise NotImplementedError


from motor_typing import TYPE_CHECKING
from .type import TypeSpecifierSeq


class ErrorDeclaration(Declaration):

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_error_declaration(self)


class AmbiguousDeclaration(Declaration):

    def __init__(self, declarations):
        # type: (List[Declaration]) -> None
        self._declarations = declarations

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_declaration(self)

    def accept_first(self, visitor):
        # type: (Visitor) -> None
        self._declarations[0].accept(visitor)

    def accept_all(self, visitor):
        # type: (Visitor) -> None
        for declaration in self._declarations:
            declaration.accept(visitor)


class SimpleDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, decl_specifier_seq, declarator_lists):
        # type: (List[Attribute], Optional[DeclSpecifierSeq], List[List[_InitDeclarator]]) -> None
        self._attributes = attribute_specifier_seq
        self._decl_specifier_seq = decl_specifier_seq
        if len(declarator_lists) == 1:
            self._declarators = InitDeclaratorList(declarator_lists[0])                       # type: _InitDeclaratorList
        else:
            self._declarators = AmbiguousInitDeclaratorList(
                [InitDeclaratorList(declarator_list) for declarator_list in declarator_lists]
            )

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_simple_declaration(self)

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_decl_specifier_seq(self, visitor):
        # type: (Visitor) -> None
        if self._decl_specifier_seq is not None:
            self._decl_specifier_seq.accept(visitor)

    def accept_init_declarator_list(self, visitor):
        # type: (Visitor) -> None
        if self._declarators is not None:
            self._declarators.accept(visitor)


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

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_initializer(self, visitor):
        # type: (Visitor) -> None
        self._initializer.accept(visitor)


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

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)


class NamespaceDeclaration(Declaration):

    def __init__(
        self, attribute_specifier_seq, attribute_specifier_seq_namespace, attribute_specifier_seq_namespace_identifier,
        inline, nested_name, namespace_name, declaration_seq
    ):
        # type: (List[Attribute], List[Attribute], List[Attribute], bool, List[Tuple[bool, str]], Optional[str], List[Declaration]) -> None
        self._attributes = attribute_specifier_seq
        self._attributes_namespace = attribute_specifier_seq_namespace + attribute_specifier_seq_namespace_identifier
        self._inline = inline
        self._nested_name = nested_name
        self._namespace_name = namespace_name
        self._declaration_seq = declaration_seq

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_namespace_declaration(self)

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_children(self, visitor):
        # type: (Visitor) -> None
        for decl in self._declaration_seq:
            decl.accept(visitor)


class NamespaceAliasDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, attribute_specifier_seq_namespace, alias_name, target_name):
        # type: (List[Attribute], List[Attribute], str, AbstractReference) -> None
        self._attributes = attribute_specifier_seq
        self._attributes_namespace = attribute_specifier_seq_namespace
        self._alias_name = alias_name
        self._target_name = target_name

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_namespace_alias_declaration(self)

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)


class UsingDirective(Declaration):

    def __init__(self, attribute_specifier_seq, reference):
        # type: (List[Attribute], AbstractReference) -> None
        self._attributes = attribute_specifier_seq
        self._reference = reference

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_using_directive(self)

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)

    def accept_reference(self, visitor):
        # type: (Visitor) -> None
        self._reference.accept(visitor)


class UsingDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq, references):
        # type: (List[Attribute], List[AbstractReference]) -> None
        self._attributes = attribute_specifier_seq
        self._references = references

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_using_declaration(self)

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)


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

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)


class LinkageSpecification(Declaration):

    def __init__(self, attribute_specifier_seq, linkage_type, declaration_seq):
        # type: (List[Attribute], str, List[Declaration]) -> None
        self._attributes = attribute_specifier_seq
        self._linkage_type = linkage_type
        self._declaration_seq = declaration_seq

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_linkage_specification(self)

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)


class OpaqueEnumDeclaration(Declaration):

    def __init__(self, name, decl_attributes, attributes, is_scoped, base_type):
        # type: (AbstractReference, List[Attribute], List[Attribute], bool, Optional[TypeSpecifierSeq]) -> None
        self._name = name
        self._attributes = decl_attributes + attributes
        self._is_scoped = is_scoped
        self._base_type = base_type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_opaque_enum_declaration(self)

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)


class _InitDeclarator(object):

    def accept(self, visitor):
        # type: (Visitor) -> None
        raise NotImplementedError


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

    def accept_declarator(self, visitor):
        # type: (Visitor) -> None
        if self._declarator is not None:
            self._declarator.accept(visitor)


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

    def accept(self, visitor):
        # type: (Visitor) -> None
        raise NotImplementedError


class InitDeclaratorList(_InitDeclaratorList):

    def __init__(self, init_declarators):
        # type: (List[_InitDeclarator]) -> None
        self._init_declarators = init_declarators

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_init_declarator_list(self)

    def accept_init_declarators(self, visitor):
        # type: (Visitor) -> None
        for declarator in self._init_declarators:
            declarator.accept(visitor)


class AmbiguousInitDeclaratorList(_InitDeclaratorList):

    def __init__(self, ambigous_init_declarator_lists):
        # type: (List[InitDeclaratorList]) -> None
        self._init_declarator_lists = list(
            sorted(ambigous_init_declarator_lists, key=lambda x: len(x._init_declarators))
        )

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_ambiguous_init_declarator_list(self)

    def accept_best(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_init_declarator_list(self._init_declarator_lists[0])

    def accept_all(self, visitor):
        # type: (Visitor) -> None
        for init_declarator_list in self._init_declarator_lists:
            init_declarator_list.accept(visitor)


class DeclSpecifierSeq(object):

    def __init__(self, attribute_specifier_seq):
        # type: (List[Attribute]) -> None
        self._decl_specifiers = []     # type: List[DeclarationSpecifier]
        self._type_specifier_seq = TypeSpecifierSeq(attribute_specifier_seq)
        self._has_defining_type_specifier = False

    def add_decl_specifier(self, specifier):
        # type: (DeclarationSpecifier) -> None
        self._decl_specifiers.append(specifier)

    def add_type_specifier(self, specifier):
        # type: (TypeSpecifier) -> None
        if specifier is None:
            return
        if self._has_defining_type_specifier and specifier._is_identifier:
            # Identifier is part of the declarator, kill this branch
            raise SyntaxError
        self._has_defining_type_specifier |= specifier._is_defining_type_specifier
        self._type_specifier_seq.add(specifier)

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_decl_specifier_seq(self)

    def accept_decl_specifiers(self, visitor):
        # type: (Visitor) -> None
        for decl_specifier in self._decl_specifiers:
            decl_specifier.accept(visitor)

    def accept_type_specifier_seq(self, visitor):
        # type: (Visitor) -> None
        self._type_specifier_seq.accept(visitor)


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


class ErrorSpecifier(DeclarationSpecifier):

    def __init__(self) -> None:
        DeclarationSpecifier.__init__(self, '')

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_error_specifier(self)


class ExplicitSpecifier(DeclarationSpecifier):

    def __init__(self, value):
        # type: (Optional[Expression]) -> None
        DeclarationSpecifier.__init__(self, 'explicit')
        self._value = value

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_explicit_specifier(self)

    def accept_expression(self, visitor):
        # type: (Visitor) -> None
        if self._value is not None:
            self._value.accept(visitor)


class ConceptDefinition(Declaration):

    def __init__(self, name, constraint_expression):
        # type: (str, Expression) -> None
        self._name = name
        self._constraint_expression = constraint_expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_concept_definition(self)

    def accept_constraint_expression(self, visitor):
        # type: (Visitor) -> None
        self._constraint_expression.accept(visitor)


class ExplicitSpecialization(Declaration):

    def __init__(self, declaration):
        # type: (Declaration) -> None
        self._declaration = declaration

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_explicit_specialization(self)

    def accept_declaration(self, visitor):
        # type: (Visitor) -> None
        self._declaration.accept(visitor)


class ExplicitInstantiation(Declaration):

    def __init__(self, declaration, is_extern):
        # type: (Declaration, bool) -> None
        self._declaration = declaration
        self._is_extern = is_extern

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_explicit_instantiation(self)

    def accept_declaration(self, visitor):
        # type: (Visitor) -> None
        self._declaration.accept(visitor)


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

    def accept_attributes(self, visitor):
        # type: (Visitor) -> None
        for attribute in self._attributes:
            attribute.accept(visitor)


if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from . import Visitor
    from .attributes import Attribute
    from .type import Declarator, TypeSpecifier, RefQualifier, TypeId, ElaboratedEnumTypeSpecifier
    from .expressions import Expression
    from .reference import AbstractReference, TemplateId
    from .constraints import RequiresClause
    from .function import VirtSpecifier
    from .function import ParameterClause
    from glrp import Token