class Visitor(object):

    def visit_translation_unit(self, unit: "TranslationUnit") -> None:
        pass

    def visit_module_declaration(self, module_declaration: "ModuleDeclaration") -> None:
        pass

    def visit_module_import_declaration(self, module_import_declaration: "ModuleImportDeclaration") -> None:
        pass

    def visit_private_module_fragment(self, private_module_fragment: "PrivateModuleFragment") -> None:
        pass

    def visit_export_declaration(self, export_declaration: "ExportDeclaration") -> None:
        pass

    def visit_global_module_fragment(self, global_module_fragment: "GlobalModuleFragment") -> None:
        pass

    def visit_type_specifier_seq(self, type_specifier_seq: "TypeSpecifierSeq") -> None:
        pass

    def visit_error_declaration(self, error_declaration: "ErrorDeclaration") -> None:
        pass

    def visit_ambiguous_declaration(self, ambiguous_declaration: "AmbiguousDeclaration") -> None:
        pass

    def visit_simple_declaration(self, simple_declaration: "SimpleDeclaration") -> None:
        pass

    def visit_structured_binding_declaration(
            self, structured_binding_declaration: "StructuredBindingDeclaration"
    ) -> None:
        pass

    def visit_static_assert(self, static_assert: "StaticAssert") -> None:
        pass

    def visit_alias_declaration(self, alias_declaration: "AliasDeclaration") -> None:
        pass

    def visit_namespace_declaration(self, namespace_declaration: "NamespaceDeclaration") -> None:
        pass

    def visit_namespace_alias_declaration(self, namespace_alias_declaration: "NamespaceAliasDeclaration") -> None:
        pass

    def visit_using_directive(self, using_directive: "UsingDirective") -> None:
        pass

    def visit_using_declaration(self, using_declaration: "UsingDeclaration") -> None:
        pass

    def visit_using_enum_declaration(self, using_enum_declaration: "UsingEnumDeclaration") -> None:
        pass

    def visit_asm_declaration(self, asm_declaration: "AsmDeclaration") -> None:
        pass

    def visit_linkage_specification(self, linkage_specification: "LinkageSpecification") -> None:
        pass

    def visit_opaque_enum_declaration(self, opaque_enum_declaration: "OpaqueEnumDeclaration") -> None:
        pass

    def visit_ambiguous_init_declarator(self, ambiguous_init_declarator: "AmbiguousInitDeclarator") -> None:
        pass

    def visit_init_declarator(self, init_declarator: "InitDeclarator") -> None:
        pass

    def visit_member_init_declarator(self, member_init_declarator: "MemberInitDeclarator") -> None:
        pass

    def visit_init_declarator_list(self, init_declarator_list: "InitDeclaratorList") -> None:
        pass

    def visit_ambiguous_init_declarator_list(
            self, ambiguous_init_declarator_list: "AmbiguousInitDeclaratorList"
    ) -> None:
        pass

    def visit_decl_specifier_seq(self, decl_specifier_seq: "DeclSpecifierSeq") -> None:
        pass

    def visit_declaration_specifier(self, declaration_specifier: "DeclarationSpecifier") -> None:
        pass

    def visit_declaration_specifier_macro(self, declaration_specifier_macro: "DeclarationSpecifierMacro") -> None:
        pass

    def visit_storage_class_specifier(self, storage_class_specifier: "StorageClassSpecifier") -> None:
        pass

    def visit_storage_class_specifier_macro(self, storage_class_specifier_macro: "StorageClassSpecifierMacro") -> None:
        pass

    def visit_error_specifier(self, error_specifier: "ErrorSpecifier") -> None:
        pass

    def visit_explicit_specifier(self, explicit_specifier: "ExplicitSpecifier") -> None:
        pass

    def visit_concept_definition(self, concept_definition: "ConceptDefinition") -> None:
        pass

    def visit_explicit_specialization(self, explicit_specialization: "ExplicitSpecialization") -> None:
        pass

    def visit_explicit_instantiation(self, explicit_instantiation: "ExplicitInstantiation") -> None:
        pass

    def visit_deduction_guide(self, deduction_guide: "DeductionGuide") -> None:
        pass

    def visit_function_definition(self, function_definition: "FunctionDefinition") -> None:
        pass

    def visit_simple_parameter_clause(self, simple_parameter_clause: "SimpleParameterClause") -> None:
        pass

    def visit_ambiguous_parameter_clause(self, ambiguous_parameter_clause: "AmbiguousParameterClause") -> None:
        pass

    def visit_parameter_declaration(self, parameter_declaration: "ParameterDeclaration") -> None:
        pass

    def visit_try_function_body(self, try_function_body: "TryFunctionBody") -> None:
        pass

    def visit_pure_virtual_function_body(self, pure_virtual_function_body: "PureVirtualFunctionBody") -> None:
        pass

    def visit_default_function_body(self, default_function_body: "DefaultFunctionBody") -> None:
        pass

    def visit_deleted_function_body(self, deleted_function_body: "DeletedFunctionBody") -> None:
        pass

    def visit_statement_function_body(self, statement_function_body: "StatementFunctionBody") -> None:
        pass

    def visit_virt_specifier_final(self, virt_specifier_final: "VirtSpecifierFinal") -> None:
        pass

    def visit_virt_specifier_override(self, virt_specifier_override: "VirtSpecifierOverride") -> None:
        pass

    def visit_virt_specifier_pure(self, virt_specifier_pure: "VirtSpecifierPure") -> None:
        pass

    def visit_virt_specifier_macro(self, virt_specifier_macro: "VirtSpecifierMacro") -> None:
        pass

    def visit_access_specifier_default(self, access_specifier_default: "AccessSpecifierDefault") -> None:
        pass

    def visit_access_specifier_public(self, access_specifier_public: "AccessSpecifierPublic") -> None:
        pass

    def visit_access_specifier_protected(self, access_specifier_protected: "AccessSpecifierProtected") -> None:
        pass

    def visit_access_specifier_private(self, access_specifier_private: "AccessSpecifierPrivate") -> None:
        pass

    def visit_access_specifier_macro(self, access_specifier_macro: "AccessSpecifierMacro") -> None:
        pass

    def visit_class_specifier(self, class_specifier: "ClassSpecifier") -> None:
        pass

    def visit_base_clause(self, base_clause: "BaseClause") -> None:
        pass

    def visit_ambiguous_base_clause(self, ambiguous_base_clause: "AmbiguousBaseClause") -> None:
        pass

    def visit_base_specifier(self, base_specifier: "BaseSpecifier") -> None:
        pass

    def visit_member_declaration(self, access_specifier: "AccessSpecifier", member_declaration: "Declaration") -> None:
        pass

    def visit_member_initializer(self, member_initializer: "MemberInitializer") -> None:
        pass

    def visit_member_initializer_error(self, member_initializer_error: "MemberInitializerError") -> None:
        pass

    def visit_mem_initializer_id_member(self, mem_initializer_id_member: "MemInitializerIdMember") -> None:
        pass

    def visit_mem_initializer_id_base(self, mem_initializer_id_base: "MemInitializerIdBase") -> None:
        pass

    def visit_ambiguous_mem_initializer_id(self, ambiguous_mem_initializer_id: "AmbiguousMemInitializerId") -> None:
        pass

    def visit_enum_specifier(self, enum_specifier: "EnumSpecifier") -> None:
        pass

    def visit_enumerator(self, enumerator: "Enumerator") -> None:
        pass

    def visit_template_parameter_list(self, template_parameter_list: "TemplateParameterList") -> None:
        pass

    def visit_ambiguous_template_parameter_list(self,
                                                ambiguous_template_parameter_list: "AmbiguousTemplateParameterList") \
            -> None:
        pass

    def visit_template_declaration(self, template_declaration: "TemplateDeclaration") -> None:
        pass

    def visit_template_argument_error(self, template_argument_error: "TemplateArgumentError") -> None:
        pass

    def visit_template_argument_pack_expand(self, template_argument_pack_expand: "TemplateArgumentPackExpand") -> None:
        pass

    def visit_ambiguous_template_argument(self, ambiguous_template_argument: "AmbiguousTemplateArgument") -> None:
        pass

    def visit_template_argument_constant(self, template_argument_constant: "TemplateArgumentConstant") -> None:
        pass

    def visit_template_argument_type_id(self, template_argument_type_id: "TemplateArgumentTypeId") -> None:
        pass

    def visit_ambiguous_template_parameter(self, ambiguous_template_parameter: "AmbiguousTemplateParameter") -> None:
        pass

    def visit_template_parameter_type(self, template_parameter_type: "TemplateParameterType") -> None:
        pass

    def visit_template_parameter_template(self, template_parameter_template: "TemplateParameterTemplate") -> None:
        pass

    def visit_template_parameter_constant(self, template_parameter_constant: "TemplateParameterConstant") -> None:
        pass

    def visit_template_parameter_constraint(self, template_parameter_constraint: "TemplateParameterConstraint") -> None:
        pass

    def visit_attribute_named_list(self, attribute_named_list: "AttributeNamedList") -> None:
        pass

    def visit_invalid_attribute(self, invalid_attribute: "InvalidAttribute") -> None:
        pass

    def visit_attribute_named(self, using_namespace: "Optional[str]", attribute_named: "AttributeNamed") -> None:
        pass

    def visit_attribute_align_as_type(self, attribute_align_as_type: "AttributeAlignAsType") -> None:
        pass

    def visit_attribute_align_as_expression(self, attribute_align_as_expression: "AttributeAlignAsExpression") -> None:
        pass

    def visit_attribute_align_as_ambiguous(self, attribute_align_as_ambiguous: "AttributeAlignAsAmbiguous") -> None:
        pass

    def visit_attribute_documentation(self, attribute_documentation: "AttributeDocumentation") -> None:
        pass

    def visit_attribute_macro(self, attribute_macro: "AttributeMacro") -> None:
        pass

    def visit_requires_expression(self, requires_expression: "RequiresExpression") -> None:
        pass

    def visit_error_requirement(self, error_requirement: "ErrorRequirement") -> None:
        pass

    def visit_requirement_body(self, requirement_body: "RequirementBody") -> None:
        pass

    def visit_ambiguous_requirement(self, ambiguous_requirement: "AmbiguousRequirement") -> None:
        pass

    def visit_simple_requirement(self, simple_requirement: "SimpleRequirement") -> None:
        pass

    def visit_type_requirement(self, type_requirement: "TypeRequirement") -> None:
        pass

    def visit_compound_requirement(self, compound_requirement: "CompoundRequirement") -> None:
        pass

    def visit_nested_requirement(self, nested_requirement: "NestedRequirement") -> None:
        pass

    def visit_requires_clause(self, requires_clause: "RequiresClause") -> None:
        pass

    def visit_pack_expand_type(self, pack_expand_type: "PackExpandType") -> None:
        pass

    def visit_pack_expand_expression(self, pack_expand_expression: "PackExpandExpression") -> None:
        pass

    def visit_pack_expand_attribute_named(self, pack_expand_attribute_named: "PackExpandAttributeNamed") -> None:
        pass

    def visit_statement_with_attributes(self, statement_with_attributes: "StatementWithAttributes") -> None:
        pass

    def visit_error_statement(self, error_statement: "ErrorStatement") -> None:
        pass

    def visit_ambiguous_statement(self, ambiguous_statement: "AmbiguousStatement") -> None:
        pass

    def visit_empty_statement(self, empty_statement: "EmptyStatement") -> None:
        pass

    def visit_expression_statement(self, expression_statement: "ExpressionStatement") -> None:
        pass

    def visit_declaration_statement(self, declaration_statement: "DeclarationStatement") -> None:
        pass

    def visit_compound_statement(self, compound_statement: "CompoundStatement") -> None:
        pass

    def visit_try_block(self, try_block: "TryBlock") -> None:
        pass

    def visit_exception_handler(self, exception_handler: "ExceptionHandler") -> None:
        pass

    def visit_exception_declaration_error(self, exception_declaration_error: "ExceptionDeclarationError") -> None:
        pass

    def visit_exception_declaration_type_specifier(
            self, exception_declaration_type_specifier: "ExceptionDeclarationTypeSpecifier"
    ) -> None:
        pass

    def visit_exception_declaration_any(self, exception_declaration_any: "ExceptionDeclarationAny") -> None:
        pass

    def visit_ambiguous_exception_declaration(
            self, ambiguous_exception_declaration: "AmbiguousExceptionDeclaration"
    ) -> None:
        pass

    def visit_break_statement(self, break_statement: "BreakStatement") -> None:
        pass

    def visit_continue_statement(self, continue_statement: "ContinueStatement") -> None:
        pass

    def visit_return_statement(self, return_statement: "ReturnStatement") -> None:
        pass

    def visit_co_return_statement(self, co_return_statement: "CoReturnStatement") -> None:
        pass

    def visit_goto_statement(self, goto_statement: "GotoStatement") -> None:
        pass

    def visit_labeled_statement(self, labeled_statement: "LabeledStatement") -> None:
        pass

    def visit_case_statement(self, case_statement: "CaseStatement") -> None:
        pass

    def visit_default_statement(self, default_statement: "DefaultStatement") -> None:
        pass

    def visit_selection_condition(self, selection_condition: "SelectionCondition") -> None:
        pass

    def visit_ambiguous_selection_condition(self, ambiguous_selection_condition: "AmbiguousSelectionCondition") -> None:
        pass

    def visit_switch_statement(self, switch_statement: "SwitchStatement") -> None:
        pass

    def visit_if_statement(self, if_statement: "IfStatement") -> None:
        pass

    def visit_if_consteval_statement(self, if_consteval_statement: "IfConstevalStatement") -> None:
        pass

    def visit_while_statement(self, while_statement: "WhileStatement") -> None:
        pass

    def visit_do_while_statement(self, do_while_statement: "DoWhileStatement") -> None:
        pass

    def visit_for_statement(self, for_statement: "ForStatement") -> None:
        pass

    def visit_ambiguous_for_condition(self, ambiguous_for_condition: "AmbiguousForCondition") -> None:
        pass

    def visit_for_condition_init(self, for_condition_init: "ForConditionInit") -> None:
        pass

    def visit_for_condition_range(self, for_condition_range: "ForConditionRange") -> None:
        pass

    def visit_cv_qualifier(self, cv_qualifie: "CvQualifier") -> None:
        pass

    def visit_ref_qualifier(self, ref_qualifier: "RefQualifier") -> None:
        pass

    def visit_exception_specifier_error(self, exception_specifier_error: "ExceptionSpecifierError") -> None:
        pass

    def visit_dynamic_exception_specifier(self, dynamic_exception_specifier: "DynamicExceptionSpecifier") -> None:
        pass

    def visit_ambiguous_exception_specifier(self, ambiguous_exception_specifier: "AmbiguousExceptionSpecifier") -> None:
        pass

    def visit_noexcept_specifier(self, noexcept_specifier: "NoExceptSpecifier") -> None:
        pass

    def visit_primitive_type_specifier(self, primitive_type_specifier: "PrimitiveTypeSpecifier") -> None:
        pass

    def visit_elaborated_class_type_specifier(
            self, elaborated_class_type_specifier: "ElaboratedClassTypeSpecifier"
    ) -> None:
        pass

    def visit_elaborated_enum_type_specifier(
            self, elaborated_enum_type_specifier: "ElaboratedEnumTypeSpecifier"
    ) -> None:
        pass

    def visit_error_type_specifier(self, error_type_specifier: "ErrorTypeSpecifier") -> None:
        pass

    def visit_auto_type_specifier(self, auto_type_specifier: "AutoTypeSpecifier") -> None:
        pass

    def visit_decltype_type_specifier(self, decltype_type_specifier: "DecltypeTypeSpecifier") -> None:
        pass

    def visit_decltype_auto_type_specifier(self, decltype_auto_type_specifier: "DecltypeAutoTypeSpecifier") -> None:
        pass

    def visit_constrained_type_specifier(self, constrained_type_specifier: "ConstrainedTypeSpecifier") -> None:
        pass

    def visit_type_specifier_reference(self, type_specifier_reference: "TypeSpecifierReference") -> None:
        pass

    def visit_ambiguous_type_specifier(self, ambiguous_type_specifier: "AmbiguousTypeSpecifier") -> None:
        pass

    def visit_defining_type_specifier_seq(self, defining_type_specifier_seq: "DefiningTypeSpecifierSeq") -> None:
        pass

    def visit_declarator_element_error(self, declarator_element_error: "DeclaratorElementError") -> None:
        pass

    def visit_declarator_element_id(self, declarator_element_id: "DeclaratorElementId") -> None:
        pass

    def visit_declarator_element_pack_id(self, declarator_element_pack_id: "DeclaratorElementPackId") -> None:
        pass

    def visit_declarator_element_abstract(self, declarator_element_abstract: "DeclaratorElementAbstract") -> None:
        pass

    def visit_declarator_element_abstract_pack(
            self, declarator_element_abstract_pack: "DeclaratorElementAbstractPack"
    ) -> None:
        pass

    def visit_declarator_element_group(self, declarator_element_group: "DeclaratorElementGroup") -> None:
        pass

    def visit_declarator_element_pointer(self, declarator_element_pointer: "DeclaratorElementPointer") -> None:
        pass

    def visit_declarator_element_reference(self, declarator_element_reference: "DeclaratorElementReference") -> None:
        pass

    def visit_declarator_element_rvalue_reference(
            self, declarator_element_rvalue_reference: "DeclaratorElementRValueReference"
    ) -> None:
        pass

    def visit_declarator_element_array(self, declarator_element_array: "DeclaratorElementArray") -> None:
        pass

    def visit_declarator_element_method(self, declarator_element_method: "DeclaratorElementMethod") -> None:
        pass

    def visit_abstract_declarator_list(self, abstract_declarator_list: "AbstractDeclaratorList") -> None:
        pass

    def visit_declarator_list(self, declarator_list: "DeclaratorList") -> None:
        pass

    def visit_ambiguous_abstract_declarator(self, ambiguous_abstract_declarator: "AmbiguousAbstractDeclarator") -> None:
        pass

    def visit_type_id_declarator(self, type_id_declarator: "TypeIdDeclarator") -> None:
        pass

    def visit_ambiguous_type_id(self, ambiguous_type_id: "AmbiguousTypeId") -> None:
        pass

    def visit_type_id_pack(self, type_id_pack: "TypeIdPack") -> None:
        pass

    def visit_error_expression(self, error_expression: "ErrorExpression") -> None:
        pass

    def visit_initializer_list(self, initializer_list: "InitializerList") -> None:
        pass

    def visit_ambiguous_initializer_list(self, ambiguous_initializer_list: "AmbiguousInitializerList") -> None:
        pass

    def visit_id_expression(self, id_expression: "IdExpression") -> None:
        pass

    def visit_ambiguous_expression(self, ambiguous_expression: "AmbiguousExpression") -> None:
        pass

    def visit_unary_expression(self, unary_expression: "UnaryExpression") -> None:
        pass

    def visit_binary_expression(self, binary_expression: "BinaryExpression") -> None:
        pass

    def visit_postfix_expression(self, postfix_expression: "PostfixExpression") -> None:
        pass

    def visit_sizeof_expression(self, sizeof_expression: "SizeofExpression") -> None:
        pass

    def visit_sizeof_type_expression(self, sizeof_type_expression: "SizeofTypeExpression") -> None:
        pass

    def visit_sizeof_pack_expression(self, sizeof_pack_expression: "SizeofPackExpression") -> None:
        pass

    def visit_alignof_expression(self, alignof_expression: "AlignofExpression") -> None:
        pass

    def visit_noexcept_expression(self, noexcept_expression: "NoexceptExpression") -> None:
        pass

    def visit_call_expression(self, call_expression: "CallExpression") -> None:
        pass

    def visit_subscript_expression(self, subscript_expression: "SubscriptExpression") -> None:
        pass

    def visit_cast_expression(self, cast_expression: "CastExpression") -> None:
        pass

    def visit_cxx_cast_expression(self, cxx_cast_expression: "CxxCastExpression") -> None:
        pass

    def visit_conditional_expression(self, conditional_expression: "ConditionalExpression") -> None:
        pass

    def visit_member_access_expression(self, member_access_expression: "MemberAccessExpression") -> None:
        pass

    def visit_member_access_ptr_expression(self, member_access_ptr_expression: "MemberAccessPtrExpression") -> None:
        pass

    def visit_member_ptr_expression(self, member_ptr_expression: "MemberPtrExpression") -> None:
        pass

    def visit_type_id_expression(self, type_id_expression: "TypeIdExpression") -> None:
        pass

    def visit_type_id_expression_type(self, type_id_expression_type: "TypeIdExpressionType") -> None:
        pass

    def visit_simple_cast_expression(self, simple_cast_expression: "SimpleCastExpression") -> None:
        pass

    def visit_new_expression(self, new_expression: "NewExpression") -> None:
        pass

    def visit_delete_expression(self, delete_expression: "DeleteExpression") -> None:
        pass

    def visit_throw_expression(self, throw_expression: "ThrowExpression") -> None:
        pass

    def visit_yield_expression(self, yield_expression: "YieldExpression") -> None:
        pass

    def visit_await_expression(self, await_expression: "AwaitExpression") -> None:
        pass

    def visit_fold_expression_left(self, fold_expression_left: "FoldExpressionLeft") -> None:
        pass

    def visit_fold_expression_right(self, fold_expression_right: "FoldExpressionRight") -> None:
        pass

    def visit_fold_expression_both(self, fold_expression_both: "FoldExpressionBoth") -> None:
        pass

    def visit_parenthesized_expression(self, parenthesized_expression: "ParenthesizedExpression") -> None:
        pass

    def visit_this_expression(self, this_expression: "ThisExpression") -> None:
        pass

    def visit_nullptr_expression(self, nullptr_expression: "NullPtrExpression") -> None:
        pass

    def visit_type_trait_expression(self, type_trait_expression: "TypeTraitExpression") -> None:
        pass

    def visit_braced_init_list(self, braced_init_list: "BracedInitList") -> None:
        pass

    def visit_ambiguous_braced_init_list(self, ambiguous_braced_init_list: "AmbiguousBracedInitList") -> None:
        pass

    def visit_designated_braced_init_list(self, designated_braced_init_list: "DesignatedBracedInitList") -> None:
        pass

    def visit_designated_initializer(self, designated_initializer: "DesignatedInitializer") -> None:
        pass

    def visit_boolean_literal(self, boolean_literal: "BooleanLiteral") -> None:
        pass

    def visit_integer_literal(self, integer_literal: "IntegerLiteral") -> None:
        pass

    def visit_user_defined_integer_literal(self, user_defined_integer_literal: "UserDefinedIntegerLiteral") -> None:
        pass

    def visit_character_literal(self, character_literal: "CharacterLiteral") -> None:
        pass

    def visit_user_defined_character_literal(
            self, user_defined_character_literal: "UserDefinedCharacterLiteral"
    ) -> None:
        pass

    def visit_string_literal(self, string_literal: "StringLiteral") -> None:
        pass

    def visit_string_literal_macro(self, string_literal_macro: "StringLiteralMacro") -> None:
        pass

    def visit_user_defined_string_literal(self, user_defined_string_literal: "UserDefinedStringLiteral") -> None:
        pass

    def visit_string_list(self, string_list: "StringList") -> None:
        pass

    def visit_floating_literal(self, floating_literal: "FloatingLiteral") -> None:
        pass

    def visit_user_defined_floating_literal(self, user_defined_floating_literal: "UserDefinedFloatingLiteral") -> None:
        pass

    def visit_lambda_expression(self, lambda_expression: "LambdaExpression") -> None:
        pass

    def visit_template_lambda_expression(self, template_lambda_expression: "TemplateLambdaExpression") -> None:
        pass

    def visit_lambda_capture_default_copy(self, lambda_capture_default_copy: "LambdaCaptureDefaultCopy") -> None:
        pass

    def visit_lambda_capture_default_reference(
            self, lambda_capture_default_reference: "LambdaCaptureDefaultReference"
    ) -> None:
        pass

    def visit_lambda_capture_list(self, lambda_capture_list: "LambdaCaptureList") -> None:
        pass

    def visit_simple_capture(self, simple_capture: "SimpleCapture") -> None:
        pass

    def visit_this_capture(self, this_capture: "ThisCapture") -> None:
        pass

    def visit_lambda_specifier(self, lambda_specifier: "LambdaSpecifier") -> None:
        pass

    def visit_lambda_declarator(self, lambda_declarator: "LambdaDeclarator") -> None:
        pass

    def visit_reference(self, ref: "Reference") -> None:
        pass

    def visit_typename_reference(self, typename_reference: "TypenameReference") -> None:
        pass

    def visit_pack_expand_reference(self, pack_expand_reference: "PackExpandReference") -> None:
        pass

    def visit_root_id(self, root_id: "RootId") -> None:
        pass

    def visit_template_specifier_id(self, template_specifier_id: "TemplateSpecifierId") -> None:
        pass

    def visit_id(self, identifier: "Id") -> None:
        pass

    def visit_template_id(self, template_id: "TemplateId") -> None:
        pass

    def visit_template_argument_list(self, template_argument_list: "TemplateArgumentList") -> None:
        pass

    def visit_ambiguous_template_argument_list(
            self, ambiguous_template_argument_list: "AmbiguousTemplateArgumentList"
    ) -> None:
        pass

    def visit_destructor_id(self, destructor_id: "DestructorId") -> None:
        pass

    def visit_operator_id(self, operator_id: "OperatorId") -> None:
        pass

    def visit_conversion_operator_id(self, conversion_operator_id: "ConversionOperatorId") -> None:
        pass

    def visit_literal_operator_id(self, literal_operator_id: "LiteralOperatorId") -> None:
        pass


from typing import Optional
from .translation_unit import TranslationUnit
from .module import (
    ModuleDeclaration,
    ModuleImportDeclaration,
    PrivateModuleFragment,
    ExportDeclaration,
    GlobalModuleFragment,
)
from .declarations import (
    ErrorDeclaration,
    AmbiguousDeclaration,
    SimpleDeclaration,
    StructuredBindingDeclaration,
    StaticAssert,
    AliasDeclaration,
    NamespaceDeclaration,
    NamespaceAliasDeclaration,
    UsingDirective,
    UsingDeclaration,
    UsingEnumDeclaration,
    AsmDeclaration,
    LinkageSpecification,
    OpaqueEnumDeclaration,
    AmbiguousInitDeclarator,
    InitDeclarator,
    MemberInitDeclarator,
    InitDeclaratorList,
    AmbiguousInitDeclaratorList,
    DeclSpecifierSeq,
    DeclarationSpecifier,
    DeclarationSpecifierMacro,
    StorageClassSpecifier,
    StorageClassSpecifierMacro,
    ErrorSpecifier,
    ExplicitSpecifier,
    ConceptDefinition,
    ExplicitSpecialization,
    ExplicitInstantiation,
    DeductionGuide,
)
from .function import (
    FunctionDefinition,
    SimpleParameterClause,
    AmbiguousParameterClause,
    ParameterDeclaration,
    TryFunctionBody,
    PureVirtualFunctionBody,
    DefaultFunctionBody,
    DeletedFunctionBody,
    StatementFunctionBody,
    VirtSpecifierFinal,
    VirtSpecifierOverride,
    VirtSpecifierPure,
    VirtSpecifierMacro,
)
from .klass import (
    AccessSpecifier,
    AccessSpecifierDefault,
    AccessSpecifierPublic,
    AccessSpecifierProtected,
    AccessSpecifierPrivate,
    AccessSpecifierMacro,
    ClassSpecifier,
    BaseClause,
    AmbiguousBaseClause,
    BaseSpecifier,
    MemberInitializer,
    MemberInitializerError,
    MemInitializerIdMember,
    MemInitializerIdBase,
    AmbiguousMemInitializerId,
)
from .enumeration import (
    EnumSpecifier,
    Enumerator,
)
from .template import (
    Declaration,
    TemplateParameterList,
    AmbiguousTemplateParameterList,
    TemplateDeclaration,
    TemplateArgumentError,
    TemplateArgumentPackExpand,
    AmbiguousTemplateArgument,
    TemplateArgumentConstant,
    TemplateArgumentTypeId,
    AmbiguousTemplateParameter,
    TemplateParameterType,
    TemplateParameterTemplate,
    TemplateParameterConstant,
    TemplateParameterConstraint,
)
from .attributes import (
    AttributeNamedList,
    InvalidAttribute,
    AttributeNamed,
    AttributeAlignAsType,
    AttributeAlignAsExpression,
    AttributeAlignAsAmbiguous,
    AttributeDocumentation,
    AttributeMacro,
)
from .constraints import (
    RequiresExpression,
    ErrorRequirement,
    RequirementBody,
    AmbiguousRequirement,
    SimpleRequirement,
    TypeRequirement,
    CompoundRequirement,
    NestedRequirement,
    RequiresClause,
)
from .pack import (
    PackExpandType,
    PackExpandExpression,
    PackExpandAttributeNamed,
)
from .statements import (
    ErrorStatement,
    StatementWithAttributes,
    AmbiguousStatement,
    EmptyStatement,
    ExpressionStatement,
    DeclarationStatement,
    CompoundStatement,
    TryBlock,
    ExceptionHandler,
    ExceptionDeclarationError,
    ExceptionDeclarationTypeSpecifier,
    ExceptionDeclarationAny,
    AmbiguousExceptionDeclaration,
    BreakStatement,
    ContinueStatement,
    ReturnStatement,
    CoReturnStatement,
    GotoStatement,
    LabeledStatement,
    CaseStatement,
    DefaultStatement,
    SelectionCondition,
    AmbiguousSelectionCondition,
    SwitchStatement,
    IfStatement,
    IfConstevalStatement,
    WhileStatement,
    DoWhileStatement,
    ForStatement,
    AmbiguousForCondition,
    ForConditionInit,
    ForConditionRange,
)
from .type import (
    CvQualifier,
    RefQualifier,
    ExceptionSpecifierError,
    DynamicExceptionSpecifier,
    AmbiguousExceptionSpecifier,
    NoExceptSpecifier,
    PrimitiveTypeSpecifier,
    ElaboratedClassTypeSpecifier,
    ElaboratedEnumTypeSpecifier,
    ErrorTypeSpecifier,
    AutoTypeSpecifier,
    DecltypeTypeSpecifier,
    DecltypeAutoTypeSpecifier,
    ConstrainedTypeSpecifier,
    TypeSpecifierReference,
    AmbiguousTypeSpecifier,
    CvQualifiers,
    RefQualifiers,
    TypeSpecifierSeq,
    DefiningTypeSpecifierSeq,
    DeclaratorElementError,
    DeclaratorElementId,
    DeclaratorElementPackId,
    DeclaratorElementAbstract,
    DeclaratorElementAbstractPack,
    DeclaratorElementGroup,
    DeclaratorElementPointer,
    DeclaratorElementReference,
    DeclaratorElementRValueReference,
    DeclaratorElementArray,
    DeclaratorElementMethod,
    AbstractDeclaratorList,
    DeclaratorList,
    AmbiguousAbstractDeclarator,
    TypeIdDeclarator,
    AmbiguousTypeId,
    TypeIdPack,
)
from .expressions import (
    ErrorExpression,
    InitializerList,
    AmbiguousInitializerList,
    IdExpression,
    AmbiguousExpression,
    UnaryExpression,
    BinaryExpression,
    PostfixExpression,
    SizeofExpression,
    SizeofTypeExpression,
    SizeofPackExpression,
    AlignofExpression,
    NoexceptExpression,
    CallExpression,
    SubscriptExpression,
    CastExpression,
    CxxCastExpression,
    ConditionalExpression,
    MemberAccessExpression,
    MemberAccessPtrExpression,
    MemberPtrExpression,
    TypeIdExpression,
    TypeIdExpressionType,
    SimpleCastExpression,
    NewExpression,
    DeleteExpression,
    ThrowExpression,
    YieldExpression,
    AwaitExpression,
    FoldExpressionLeft,
    FoldExpressionRight,
    FoldExpressionBoth,
    ParenthesizedExpression,
    ThisExpression,
    NullPtrExpression,
    TypeTraitExpression,
)
from .literals import (
    BracedInitList,
    AmbiguousBracedInitList,
    DesignatedBracedInitList,
    DesignatedInitializer,
    BooleanLiteral,
    IntegerLiteral,
    UserDefinedIntegerLiteral,
    CharacterLiteral,
    UserDefinedCharacterLiteral,
    StringLiteral,
    StringLiteralMacro,
    UserDefinedStringLiteral,
    StringList,
    FloatingLiteral,
    UserDefinedFloatingLiteral,
)
from .lambdas import (
    LambdaExpression,
    TemplateLambdaExpression,
    LambdaCaptureDefaultCopy,
    LambdaCaptureDefaultReference,
    LambdaCaptureList,
    SimpleCapture,
    ThisCapture,
    LambdaSpecifier,
    LambdaDeclarator,
)
from .reference import (
    Reference,
    TypenameReference,
    PackExpandReference,
    RootId,
    TemplateSpecifierId,
    Id,
    TemplateId,
    TemplateArgumentList,
    AmbiguousTemplateArgumentList,
    DestructorId,
    OperatorId,
    ConversionOperatorId,
    LiteralOperatorId,
)
