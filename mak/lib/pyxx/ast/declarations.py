from typing import List, Optional, Tuple
from . import Visitor
from .base import Attribute, Declarator, TypeSpecifier, TypeId, Declaration, Expression
from .type import ElaboratedEnumTypeSpecifier, TypeSpecifierSeq, RefQualifier
from .reference import AbstractReference, TemplateId
from .constraints import RequiresClause
from glrp import Token


class ErrorDeclaration(Declaration):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_error_declaration(self)


class AmbiguousDeclaration(Declaration):

    def __init__(self, declarations: List[Declaration]) -> None:
        self.declarations = declarations

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_declaration(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.declarations[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for declaration in self.declarations:
            declaration.accept(visitor)


class SimpleDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq: List[Attribute], decl_specifier_seq: Optional["DeclSpecifierSeq"],
                 declarator_lists: List[List["_InitDeclarator"]]):
        self.attributes = attribute_specifier_seq
        self.decl_specifier_seq = decl_specifier_seq
        if len(declarator_lists) == 1:
            self.declarators = InitDeclaratorList(declarator_lists[0])  # type: _InitDeclaratorList
        else:
            self.declarators = AmbiguousInitDeclaratorList(
                [InitDeclaratorList(declarator_list) for declarator_list in declarator_lists]
            )

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_simple_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_decl_specifier_seq(self, visitor: Visitor) -> None:
        if self.decl_specifier_seq is not None:
            self.decl_specifier_seq.accept(visitor)

    def accept_init_declarator_list(self, visitor: Visitor) -> None:
        if self.declarators is not None:
            self.declarators.accept(visitor)


class StructuredBindingDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq: List[Attribute], decl_specifier_seq: Optional["DeclSpecifierSeq"],
                 ref_qualifier: Optional[RefQualifier], names: List[str], initializer: Expression) -> None:
        self.attributes = attribute_specifier_seq
        self.decl_specifier_seq = decl_specifier_seq
        self.ref_qualifier = ref_qualifier
        self.names = names
        self.initializer = initializer

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_structured_binding_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_decl_specifier_seq(self, visitor: Visitor) -> None:
        if self.decl_specifier_seq is not None:
            self.decl_specifier_seq.accept(visitor)

    def accept_ref_qualifier(self, visitor: Visitor) -> None:
        if self.ref_qualifier is not None:
            self.ref_qualifier.accept(visitor)

    def accept_initializer(self, visitor: Visitor) -> None:
        self.initializer.accept(visitor)


class StaticAssert(Declaration):

    def __init__(self, condition: Expression, message: Optional[Expression]):
        self.condition = condition
        self.message = message

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_static_assert(self)

    def accept_condition(self, visitor: Visitor) -> None:
        self.condition.accept(visitor)

    def accept_message(self, visitor: Visitor) -> None:
        if self.message is not None:
            self.message.accept(visitor)


class AliasDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq: List[Attribute], name: str,
                 attribute_specifier_seq_alias: List[Attribute], type_id: TypeId) -> None:
        self.attributes = attribute_specifier_seq
        self.alias = name
        self.alias_attributes = attribute_specifier_seq_alias
        self.type_id = type_id

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_alias_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_alias_attributes(self, visitor: Visitor) -> None:
        for attribute in self.alias_attributes:
            attribute.accept(visitor)

    def accept_type_id(self, visitor: Visitor) -> None:
        self.type_id.accept(visitor)


class NamespaceDeclaration(Declaration):

    def __init__(
            self, attribute_specifier_seq: List[Attribute], attribute_specifier_seq_namespace: List[Attribute],
            attribute_specifier_seq_namespace_identifier: List[Attribute],
            inline: bool, nested_name: List[Tuple[bool, str]], namespace_name: Optional[str],
            declaration_seq: List[Declaration]
    ) -> None:
        self.attributes = attribute_specifier_seq
        self.attributes_namespace = attribute_specifier_seq_namespace + attribute_specifier_seq_namespace_identifier
        self.inline = inline
        self.nested_name = nested_name
        self.namespace_name = namespace_name
        self.declaration_seq = declaration_seq

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_namespace_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes + self.attributes_namespace:
            attribute.accept(visitor)

    def accept_children(self, visitor: Visitor) -> None:
        for decl in self.declaration_seq:
            decl.accept(visitor)


class NamespaceAliasDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq: List[Attribute], attribute_specifier_seq_namespace: List[Attribute],
                 alias_name: str, target_name: AbstractReference) -> None:
        self.attributes = attribute_specifier_seq
        self.attributes_namespace = attribute_specifier_seq_namespace
        self.alias_name = alias_name
        self.target_name = target_name

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_namespace_alias_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_reference(self, visitor: Visitor) -> None:
        self.target_name.accept(visitor)


class UsingDirective(Declaration):

    def __init__(self, attribute_specifier_seq: List[Attribute], reference: AbstractReference):
        self.attributes = attribute_specifier_seq
        self.reference = reference

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_using_directive(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_reference(self, visitor: Visitor) -> None:
        self.reference.accept(visitor)


class UsingDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq: List[Attribute], reference_list: List[AbstractReference]) -> None:
        self.attributes = attribute_specifier_seq
        self.reference_list = reference_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_using_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_reference_list(self, visitor: Visitor) -> None:
        for reference in self.reference_list:
            reference.accept(visitor)


class UsingEnumDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq: List[Attribute], enum_specifier: ElaboratedEnumTypeSpecifier) -> None:
        self.attributes = attribute_specifier_seq
        self.enum_specifier = enum_specifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_using_enum_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_enum_specifier(self, visitor: Visitor) -> None:
        self.enum_specifier.accept(visitor)


class AsmDeclaration(Declaration):

    def __init__(self, attribute_specifier_seq: List[Attribute], asm_string: str) -> None:
        self.attributes = attribute_specifier_seq
        self.asm_string = asm_string

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_asm_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)


class LinkageSpecification(Declaration):

    def __init__(self, attribute_specifier_seq: List[Attribute], linkage_type: str,
                 declaration_seq: List[Declaration]) -> None:
        self.attributes = attribute_specifier_seq
        self.linkage_type = linkage_type
        self.declaration_seq = declaration_seq

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_linkage_specification(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_declarations(self, visitor: Visitor) -> None:
        for decl in self.declaration_seq:
            decl.accept(visitor)


class OpaqueEnumDeclaration(Declaration):

    def __init__(self, name: AbstractReference, decl_attributes: List[Attribute], attributes: List[Attribute],
                 is_scoped: bool, base_type: Optional[TypeSpecifierSeq]):
        self.name = name
        self.attributes = decl_attributes + attributes
        self.is_scoped = is_scoped
        self.base_type = base_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_opaque_enum_declaration(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_name(self, visitor: Visitor) -> None:
        self.name.accept(visitor)

    def accept_base_type(self, visitor: Visitor) -> None:
        if self.base_type is not None:
            self.base_type.accept(visitor)


class _InitDeclarator(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class InitDeclarator(_InitDeclarator):

    def __init__(self, declarator: Optional[Declarator], init_value: Optional[Expression],
                 constraint: Optional[RequiresClause]) -> None:
        self.declarator = declarator
        self.init_value = init_value
        self.constraint = constraint

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_init_declarator(self)

    def accept_declarator(self, visitor: Visitor) -> None:
        if self.declarator is not None:
            self.declarator.accept(visitor)

    def accept_init_value(self, visitor: Visitor) -> None:
        if self.init_value is not None:
            self.init_value.accept(visitor)

    def accept_constraint(self, visitor: Visitor) -> None:
        if self.constraint is not None:
            self.constraint.accept(visitor)


class AmbiguousInitDeclarator(_InitDeclarator):

    def __init__(self, init_declarators: List[InitDeclarator]):
        self.init_declarators = init_declarators

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_init_declarator(self)

    def accept_best(self, visitor: Visitor) -> None:
        self.init_declarators[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for init_declarator in self.init_declarators:
            init_declarator.accept(visitor)


class MemberInitDeclarator(InitDeclarator):

    def __init__(self, declarator: Optional[Declarator], init_value: Optional[Expression],
                 constraint: Optional[RequiresClause], virt_specifier_seq: List["VirtSpecifier"],
                 bitfield_width: Optional[Expression]) -> None:
        InitDeclarator.__init__(self, declarator, init_value, constraint)
        self.virt_specifier_seq = virt_specifier_seq
        self.bitfield_width = bitfield_width

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_member_init_declarator(self)

    def acceot_virt_specifiers(self, visitor: Visitor) -> None:
        for virt_specifier in self.virt_specifier_seq:
            virt_specifier.accept(visitor)

    def accept_bitfield_width(self, visitor: Visitor) -> None:
        if self.bitfield_width is not None:
            self.bitfield_width.accept(visitor)


class _InitDeclaratorList:

    def __init__(self) -> None:
        self.next = None  # type: Optional[_InitDeclarator]

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class InitDeclaratorList(_InitDeclaratorList):

    def __init__(self, init_declarators: List[_InitDeclarator]) -> None:
        super().__init__()
        self.init_declarators = init_declarators

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_init_declarator_list(self)

    def accept_init_declarators(self, visitor: Visitor) -> None:
        for declarator in self.init_declarators:
            declarator.accept(visitor)


class AmbiguousInitDeclaratorList(_InitDeclaratorList):

    def __init__(self, ambigous_init_declarator_lists: List[InitDeclaratorList]) -> None:
        super().__init__()
        self.init_declarator_lists = list(
            sorted(ambigous_init_declarator_lists, key=lambda x: len(x.init_declarators))
        )

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_init_declarator_list(self)

    def accept_best(self, visitor: Visitor) -> None:
        visitor.visit_init_declarator_list(self.init_declarator_lists[0])

    def accept_all(self, visitor: Visitor) -> None:
        for init_declarator_list in self.init_declarator_lists:
            init_declarator_list.accept(visitor)


class DeclarationSpecifier(object):

    def __init__(self, decl_specifier: str) -> None:
        self.decl_specifier = decl_specifier

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declaration_specifier(self)


class DeclSpecifierSeq(object):

    def __init__(self, attribute_specifier_seq: List[Attribute]) -> None:
        self.decl_specifiers = []  # type: List[DeclarationSpecifier]
        self.type_specifier_seq = TypeSpecifierSeq(attribute_specifier_seq)
        self.has_defining_type_specifier = False

    def add_decl_specifier(self, specifier: DeclarationSpecifier) -> None:
        self.decl_specifiers.append(specifier)

    def add_type_specifier(self, specifier: TypeSpecifier) -> None:
        if specifier is None:
            return
        if self.has_defining_type_specifier and specifier.is_identifier:
            # Identifier is part of the declarator, kill this branch
            raise SyntaxError
        self.has_defining_type_specifier |= specifier.is_defining_type_specifier
        self.type_specifier_seq.add(specifier)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_decl_specifier_seq(self)

    def accept_decl_specifiers(self, visitor: Visitor) -> None:
        for decl_specifier in self.decl_specifiers:
            decl_specifier.accept(visitor)

    def accept_type_specifier_seq(self, visitor: Visitor) -> None:
        self.type_specifier_seq.accept(visitor)


class DeclarationSpecifierMacro(DeclarationSpecifier):

    def __init__(self, decl_specifier: str, values: Optional[List[Token]]) -> None:
        DeclarationSpecifier.__init__(self, decl_specifier)
        self.values = values

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_declaration_specifier_macro(self)


class StorageClassSpecifier(DeclarationSpecifier):

    def __init__(self, storage_class_specifier: str) -> None:
        DeclarationSpecifier.__init__(self, storage_class_specifier)

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_storage_class_specifier(self)


class StorageClassSpecifierMacro(StorageClassSpecifier):

    def __init__(self, storage_class_specifier: str, values: Optional[List[Token]]) -> None:
        StorageClassSpecifier.__init__(self, storage_class_specifier)
        self.values = values

    def accept(self, visitor: Visitor) -> None:
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

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_error_specifier(self)


class ExplicitSpecifier(DeclarationSpecifier):

    def __init__(self, value):
        # type: (Optional[Expression]) -> None
        DeclarationSpecifier.__init__(self, 'explicit')
        self.value = value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_explicit_specifier(self)

    def accept_expression(self, visitor: Visitor) -> None:
        if self.value is not None:
            self.value.accept(visitor)


class ConceptDefinition(Declaration):

    def __init__(self, name: str, constraint_expression: Expression) -> None:
        self.name = name
        self.constraint_expression = constraint_expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_concept_definition(self)

    def accept_constraint_expression(self, visitor: Visitor) -> None:
        self.constraint_expression.accept(visitor)


class ExplicitSpecialization(Declaration):

    def __init__(self, declaration: Declaration) -> None:
        self.declaration = declaration

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_explicit_specialization(self)

    def accept_declaration(self, visitor: Visitor) -> None:
        self.declaration.accept(visitor)


class ExplicitInstantiation(Declaration):

    def __init__(self, declaration: Declaration, is_extern: bool) -> None:
        self.declaration = declaration
        self.is_extern = is_extern

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_explicit_instantiation(self)

    def accept_declaration(self, visitor: Visitor) -> None:
        self.declaration.accept(visitor)


class DeductionGuide(Declaration):

    def __init__(self, attributes: List[Attribute], name: str, explicit_specifier: Optional[ExplicitSpecifier],
                 parameter_clause: "ParameterClause", template_id: TemplateId) -> None:
        self.attributes = attributes
        self.name = name
        self.explicit_specifier = explicit_specifier
        self.parameter_clause = parameter_clause
        self.template_id = template_id

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_deduction_guide(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            attribute.accept(visitor)

    def accept_explicit_specifier(self, visitor: Visitor) -> None:
        if self.explicit_specifier is not None:
            self.explicit_specifier.accept(visitor)

    def accept_parameter_clause(self, visitor: Visitor) -> None:
        self.parameter_clause.accept(visitor)

    def accept_template_id(self, visitor: Visitor) -> None:
        self.template_id.accept(visitor)


from .function import VirtSpecifier, ParameterClause
