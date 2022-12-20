from motor_typing import TYPE_CHECKING


class Visitor(object):

    def visit_translation_unit(self, translation_unit):
        # type: (TranslationUnit) -> None
        pass

    def visit_module_declaration(self, module_declaration):
        # type: (ModuleDeclaration) -> None
        pass

    def visit_module_import_declaration(self, module_import_declaration):
        # type: (ModuleImportDeclaration) -> None
        pass

    def visit_private_module_fragment(self, private_module_fragment):
        # type: (PrivateModuleFragment) -> None
        pass

    def visit_export_declaration(self, export_declaration):
        # type: (ExportDeclaration) -> None
        pass

    def visit_global_module_fragment(self, global_module_fragment):
        # type: (GlobalModuleFragment) -> None
        pass

    def visit_type_specifier_seq(self, type_specifier_seq):
        # type: (TypeSpecifierSeq) -> None
        pass

    def visit_ambiguous_declaration(self, ambiguous_declaration):
        # type: (AmbiguousDeclaration) -> None
        pass

    def visit_simple_declaration(self, simple_declaration):
        # type: (SimpleDeclaration) -> None
        pass

    def visit_structured_binding_declaration(self, structured_binding_declaration):
        # type: (StructuredBindingDeclaration) -> None
        pass

    def visit_static_assert(self, static_assert):
        # type: (StaticAssert) -> None
        pass

    def visit_alias_declaration(self, alias_declaration):
        # type: (AliasDeclaration) -> None
        pass

    def visit_namespace_declaration(self, namespace_declaration):
        # type: (NamespaceDeclaration) -> None
        pass

    def visit_namespace_alias_declaration(self, namespace_alias_declaration):
        # type: (NamespaceAliasDeclaration) -> None
        pass

    def visit_using_directive(self, using_directive):
        # type: (UsingDirective) -> None
        pass

    def visit_using_declaration(self, using_declaration):
        # type: (UsingDeclaration) -> None
        pass

    def visit_using_enum_declaration(self, using_enum_declaration):
        # type: (UsingEnumDeclaration) -> None
        pass

    def visit_asm_declaration(self, asm_declaration):
        # type: (AsmDeclaration) -> None
        pass

    def visit_linkage_specification(self, linkage_specification):
        # type: (LinkageSpecification) -> None
        pass

    def visit_opaque_enum_declaration(self, opaque_enum_declaration):
        # type: (OpaqueEnumDeclaration) -> None
        pass

    def visit_ambiguous_init_declarator(self, ambiguous_init_declarator):
        # type: (AmbiguousInitDeclarator) -> None
        pass

    def visit_init_declarator(self, init_declarator):
        # type: (InitDeclarator) -> None
        pass

    def visit_member_init_declarator(self, member_init_declarator):
        # type: (MemberInitDeclarator) -> None
        pass

    def visit_init_declarator_list(self, init_declarator_list):
        # type: (InitDeclaratorList) -> None
        pass

    def visit_ambiguous_init_declarator_list(self, ambiguous_init_declarator_list):
        # type: (AmbiguousInitDeclaratorList) -> None
        pass

    def visit_decl_specifier_seq(self, decl_specifier_seq):
        # type: (DeclSpecifierSeq) -> None
        pass

    def visit_declaration_specifier(self, declaration_specifier):
        # type: (DeclarationSpecifier) -> None
        pass

    def visit_declaration_specifier_macro(self, declaration_specifier_macro):
        # type: (DeclarationSpecifierMacro) -> None
        pass

    def visit_storage_class_specifier(self, storage_class_specifier):
        # type: (StorageClassSpecifier) -> None
        pass

    def visit_storage_class_specifier_macro(self, storage_class_specifier_macro):
        # type: (StorageClassSpecifierMacro) -> None
        pass

    def visit_explicit_specifier(self, explicit_specifier):
        # type: (ExplicitSpecifier) -> None
        pass

    def visit_concept_definition(self, concept_definition):
        # type: (ConceptDefinition) -> None
        pass

    def visit_explicit_specialization(self, explicit_specialization):
        # type: (ExplicitSpecialization) -> None
        pass

    def visit_explicit_instantiation(self, explicit_instantiation):
        # type: (ExplicitInstantiation) -> None
        pass

    def visit_deduction_guide(self, deduction_guide):
        # type: (DeductionGuide) -> None
        pass

    def visit_declaration(self, declaration):
        # type: (Declaration) -> None
        pass

    def visit_function_definition(self, function_definition):
        # type: (FunctionDefinition) -> None
        pass

    def visit_simple_parameter_clause(self, simple_parameter_clause):
        # type: (SimpleParameterClause) -> None
        pass

    def visit_ambiguous_parameter_clause(self, ambiguous_parameter_clause):
        # type: (AmbiguousParameterClause) -> None
        pass

    def visit_parameter_declaration(self, parameter_declaration):
        # type: (ParameterDeclaration) -> None
        pass

    def visit_try_function_body(self, try_function_body):
        # type: (TryFunctionBody) -> None
        pass

    def visit_pure_virtual_function_body(self, pure_virtual_function_body):
        # type: (PureVirtualFunctionBody) -> None
        pass

    def visit_default_function_body(self, default_function_body):
        # type: (DefaultFunctionBody) -> None
        pass

    def visit_deleted_function_body(self, deleted_function_body):
        # type: (DeletedFunctionBody) -> None
        pass

    def visit_statement_function_body(self, statement_function_body):
        # type: (StatementFunctionBody) -> None
        pass

    def visit_virt_specifier_final(self, virt_specifier_final):
        # type: (VirtSpecifierFinal) -> None
        pass

    def visit_virt_specifier_override(self, virt_specifier_override):
        # type: (VirtSpecifierOverride) -> None
        pass

    def visit_virt_specifier_pure(self, virt_specifier_pure):
        # type: (VirtSpecifierPure) -> None
        pass

    def visit_virt_specifier_macro(self, virt_specifier_macro):
        # type: (VirtSpecifierMacro) -> None
        pass

    def visit_access_specifier_default(self, access_specifier_default):
        # type: (AccessSpecifierDefault) -> None
        pass

    def visit_access_specifier_public(self, access_specifier_public):
        # type: (AccessSpecifierPublic) -> None
        pass

    def visit_access_specifier_protected(self, access_specifier_protected):
        # type: (AccessSpecifierProtected) -> None
        pass

    def visit_access_specifier_private(self, access_specifier_private):
        # type: (AccessSpecifierPrivate) -> None
        pass

    def visit_access_specifier_macro(self, access_specifier_macro):
        # type: (AccessSpecifierMacro) -> None
        pass

    def visit_class_specifier(self, class_specifier):
        # type: (ClassSpecifier) -> None
        pass

    def visit_base_specifier(self, base_specifier):
        # type: (BaseSpecifier) -> None
        pass

    def visit_member_initializer(self, member_initializer):
        # type: (MemberInitializer) -> None
        pass

    def visit_mem_initializer_id_member(self, mem_initializer_id_member):
        # type: (MemInitializerIdMember) -> None
        pass

    def visit_mem_initializer_id_base(self, mem_initializer_id_base):
        # type: (MemInitializerIdBase) -> None
        pass

    def visit_ambiguous_mem_initializer_id(self, ambiguous_mem_initializer_id):
        # type: (AmbiguousMemInitializerId) -> None
        pass

    def visit_enum_specifier(self, enum_specifier):
        # type: (EnumSpecifier) -> None
        pass

    def visit_enumerator(self, enumerator):
        # type: (Enumerator) -> None
        pass

    def visit_template_declaration(self, template_declaration):
        # type: (TemplateDeclaration) -> None
        pass

    def visit_template_argument_pack_expand(self, template_argument_pack_expand):
        # type: (TemplateArgumentPackExpand) -> None
        pass

    def visit_ambiguous_template_argument(self, ambiguous_template_argument):
        # type: (AmbiguousTemplateArgument) -> None
        pass

    def visit_template_argument_constant(self, template_argument_constant):
        # type: (TemplateArgumentConstant) -> None
        pass

    def visit_template_argument_type_id(self, template_argument_type_id):
        # type: (TemplateArgumentTypeId) -> None
        pass

    def visit_ambiguous_template_parameter(self, ambiguous_template_parameter):
        # type: (AmbiguousTemplateParameter) -> None
        pass

    def visit_template_parameter_type(self, template_parameter_type):
        # type: (TemplateParameterType) -> None
        pass

    def visit_template_parameter_template(self, template_parameter_template):
        # type: (TemplateParameterTemplate) -> None
        pass

    def visit_template_parameter_constant(self, template_parameter_constant):
        # type: (TemplateParameterConstant) -> None
        pass

    def visit_template_parameter_constraint(self, template_parameter_constraint):
        # type: (TemplateParameterConstraint) -> None
        pass

    def visit_attribute_named_list(self, attribute_named_list):
        # type: (AttributeNamedList) -> None
        pass

    def visit_attribute_named(self, attribute_named):
        # type: (AttributeNamed) -> None
        pass

    def visit_attribute_align_as_type(self, attribute_align_as_type):
        # type: (AttributeAlignAsType) -> None
        pass

    def visit_attribute_align_as_expression(self, attribute_align_as_expression):
        # type: (AttributeAlignAsExpression) -> None
        pass

    def visit_attribute_align_as_ambiguous(self, attribute_align_as_ambiguous):
        # type: (AttributeAlignAsAmbiguous) -> None
        pass

    def visit_attribute_align_as_ambiguous_pack(self, attribute_align_as_ambiguous_pack):
        # type: (AttributeAlignAsAmbiguousPack) -> None
        pass

    def visit_attribute_documentation(self, attribute_documentation):
        # type: (AttributeDocumentation) -> None
        pass

    def visit_attribute_macro(self, attribute_macro):
        # type: (AttributeMacro) -> None
        pass

    def visit_requires_expression(self, requires_expression):
        # type: (RequiresExpression) -> None
        pass

    def visit_requirement_body(self, requirement_body):
        # type: (RequirementBody) -> None
        pass

    def visit_ambiguous_requirement(self, ambiguous_requirement):
        # type: (AmbiguousRequirement) -> None
        pass

    def visit_simple_requirement(self, simple_requirement):
        # type: (SimpleRequirement) -> None
        pass

    def visit_type_requirement(self, type_requirement):
        # type: (TypeRequirement) -> None
        pass

    def visit_compound_requirement(self, compound_requirement):
        # type: (CompoundRequirement) -> None
        pass

    def visit_nested_requirement(self, nested_requirement):
        # type: (NestedRequirement) -> None
        pass

    def visit_requires_clause(self, requires_clause):
        # type: (RequiresClause) -> None
        pass

    def visit_pack_expand_type(self, pack_expand_type):
        # type: (PackExpandType) -> None
        pass

    def visit_pack_expand_expression(self, pack_expand_expression):
        # type: (PackExpandExpression) -> None
        pass

    def visit_pack_expand_attribute_named(self, pack_expand_attribute_named):
        # type: (PackExpandAttributeNamed) -> None
        pass

    def visit_ambiguous_statement(self, ambiguous_statement):
        # type: (AmbiguousStatement) -> None
        pass

    def visit_empty_statement(self, empty_statement):
        # type: (EmptyStatement) -> None
        pass

    def visit_expression_statement(self, expression_statement):
        # type: (ExpressionStatement) -> None
        pass

    def visit_declaration_statement(self, declaration_statement):
        # type: (DeclarationStatement) -> None
        pass

    def visit_compound_statement(self, compound_statement):
        # type: (CompoundStatement) -> None
        pass

    def visit_try_block(self, try_block):
        # type: (TryBlock) -> None
        pass

    def visit_exception_handler(self, exception_handler):
        # type: (ExceptionHandler) -> None
        pass

    def visit_exception_declaration_type_specifier(self, exception_declaration_type_specifier):
        # type: (ExceptionDeclarationTypeSpecifier) -> None
        pass

    def visit_exception_declaration_any(self, exception_declaration_any):
        # type: (ExceptionDeclarationAny) -> None
        pass

    def visit_ambiguous_exception_declaration(self, ambiguous_exception_declaration):
        # type: (AmbiguousExceptionDeclaration) -> None
        pass

    def visit_break_statement(self, break_statement):
        # type: (BreakStatement) -> None
        pass

    def visit_continue_statement(self, continue_statement):
        # type: (ContinueStatement) -> None
        pass

    def visit_return_statement(self, return_statement):
        # type: (ReturnStatement) -> None
        pass

    def visit_co_return_statement(self, co_return_statement):
        # type: (CoReturnStatement) -> None
        pass

    def visit_goto_statement(self, goto_statement):
        # type: (GotoStatement) -> None
        pass

    def visit_labeled_statement(self, labeled_statement):
        # type: (LabeledStatement) -> None
        pass

    def visit_case_statement(self, case_statement):
        # type: (CaseStatement) -> None
        pass

    def visit_default_statement(self, default_statement):
        # type: (DefaultStatement) -> None
        pass

    def visit_selection_condition(self, selection_condition):
        # type: (SelectionCondition) -> None
        pass

    def visit_ambiguous_selection_condition(self, ambiguous_selection_condition):
        # type: (AmbiguousSelectionCondition) -> None
        pass

    def visit_switch_statement(self, switch_statement):
        # type: (SwitchStatement) -> None
        pass

    def visit_if_statement(self, if_statement):
        # type: (IfStatement) -> None
        pass

    def visit_if_consteval_statement(self, if_consteval_statement):
        # type: (IfConstevalStatement) -> None
        pass

    def visit_while_statement(self, while_statement):
        # type: (WhileStatement) -> None
        pass

    def visit_do_while_statement(self, do_while_statement):
        # type: (DoWhileStatement) -> None
        pass

    def visit_for_statement(self, for_statement):
        # type: (ForStatement) -> None
        pass

    def visit_ambiguous_for_condition(self, ambiguous_for_condition):
        # type: (AmbiguousForCondition) -> None
        pass

    def visit_for_condition_init(self, for_condition_init):
        # type: (ForConditionInit) -> None
        pass

    def visit_for_condition_range(self, for_condition_range):
        # type: (ForConditionRange) -> None
        pass

    def visit_cv_qualifier(self, cv_qualifier):
        # type: (CvQualifier) -> None
        pass

    def visit_ref_qualifier(self, ref_qualifier):
        # type: (RefQualifier) -> None
        pass

    def visit_dynamic_exception_specifier(self, dynamic_exception_specifier):
        # type: (DynamicExceptionSpecifier) -> None
        pass

    def visit_noexcept_specifier(self, noexcept_specifier):
        # type: (NoExceptSpecifier) -> None
        pass

    def visit_primitive_type_specifier(self, primitive_type_specifier):
        # type: (PrimitiveTypeSpecifier) -> None
        pass

    def visit_elaborated_class_type_specifier(self, elaborated_class_type_specifier):
        # type: (ElaboratedClassTypeSpecifier) -> None
        pass

    def visit_elaborated_enum_type_specifier(self, elaborated_enum_type_specifier):
        # type: (ElaboratedEnumTypeSpecifier) -> None
        pass

    def visit_auto_type_specifier(self, auto_type_specifier):
        # type: (AutoTypeSpecifier) -> None
        pass

    def visit_decltype_type_specifier(self, decltype_type_specifier):
        # type: (DecltypeTypeSpecifier) -> None
        pass

    def visit_decltype_auto_type_specifier(self, decltype_auto_type_specifier):
        # type: (DecltypeAutoTypeSpecifier) -> None
        pass

    def visit_constrained_type_specifier(self, constrained_type_specifier):
        # type: (ConstrainedTypeSpecifier) -> None
        pass

    def visit_type_specifier_reference(self, type_specifier_reference):
        # type: (TypeSpecifierReference) -> None
        pass

    def visit_ambiguous_type_specifier(self, ambiguous_type_specifier):
        # type: (AmbiguousTypeSpecifier) -> None
        pass

    def visit_cv_qualifiers(self, cv_qualifiers):
        # type: (CvQualifiers) -> None
        pass

    def visit_ref_qualifiers(self, ref_qualifiers):
        # type: (RefQualifiers) -> None
        pass

    def visit_defining_type_specifier_seq(self, defining_type_specifier_seq):
        # type: (DefiningTypeSpecifierSeq) -> None
        pass

    def visit_declarator_element_id(self, declarator_element_id):
        # type: (DeclaratorElementId) -> None
        pass

    def visit_declarator_element_pack_id(self, declarator_element_pack_id):
        # type: (DeclaratorElementPackId) -> None
        pass

    def visit_declarator_element_abstract_pack_id(self, declarator_element_abstract_pack_id):
        # type: (DeclaratorElementAbstractPackId) -> None
        pass

    def visit_declarator_element_pointer(self, declarator_element_pointer):
        # type: (DeclaratorElementPointer) -> None
        pass

    def visit_declarator_element_reference(self, declarator_element_reference):
        # type: (DeclaratorElementReference) -> None
        pass

    def visit_declarator_element_rvalue_reference(self, declarator_element_rvalue_reference):
        # type: (DeclaratorElementRValueReference) -> None
        pass

    def visit_declarator_element_array(self, declarator_element_array):
        # type: (DeclaratorElementArray) -> None
        pass

    def visit_declarator_element_method(self, declarator_element_method):
        # type: (DeclaratorElementMethod) -> None
        pass

    def visit_abstract_declarator_list(self, abstract_declarator_list):
        # type: (AbstractDeclaratorList) -> None
        pass

    def visit_declarator_list(self, declarator_list):
        # type: (DeclaratorList) -> None
        pass

    def visit_ambiguous_abstract_declarator(self, ambiguous_abstract_declarator):
        # type: (AmbiguousAbstractDeclarator) -> None
        pass

    def visit_type_id_declarator(self, type_id_declarator):
        # type: (TypeIdDeclarator) -> None
        pass

    def visit_ambiguous_type_id(self, ambiguous_type_id):
        # type: (AmbiguousTypeId) -> None
        pass

    def visit_type_id_pack(self, type_id_pack):
        # type: (TypeIdPack) -> None
        pass

    def visit_expression_list(self, expression_list):
        # type: (ExpressionList) -> None
        pass

    def visit_id_expression(self, id_expression):
        # type: (IdExpression) -> None
        pass

    def visit_ambiguous_expression(self, ambiguous_expression):
        # type: (AmbiguousExpression) -> None
        pass

    def visit_literal_expression(self, literal_expression):
        # type: (LiteralExpression) -> None
        pass

    def visit_unary_expression(self, unary_expression):
        # type: (UnaryExpression) -> None
        pass

    def visit_binary_expression(self, binary_expression):
        # type: (BinaryExpression) -> None
        pass

    def visit_postfix_expression(self, postfix_expression):
        # type: (PostfixExpression) -> None
        pass

    def visit_sizeof_expression(self, sizeof_expression):
        # type: (SizeofExpression) -> None
        pass

    def visit_sizeof_type_expression(self, sizeof_type_expression):
        # type: (SizeofTypeExpression) -> None
        pass

    def visit_sizeof_pack_expression(self, sizeof_pack_expression):
        # type: (SizeofPackExpression) -> None
        pass

    def visit_alignof_expression(self, alignof_expression):
        # type: (AlignofExpression) -> None
        pass

    def visit_noexcept_expression(self, noexcept_expression):
        # type: (NoexceptExpression) -> None
        pass

    def visit_call_expression(self, call_expression):
        # type: (CallExpression) -> None
        pass

    def visit_subscript_expression(self, subscript_expression):
        # type: (SubscriptExpression) -> None
        pass

    def visit_cast_expression(self, cast_expression):
        # type: (CastExpression) -> None
        pass

    def visit_cxx_cast_expression(self, cxx_cast_expression):
        # type: (CxxCastExpression) -> None
        pass

    def visit_conditional_expression(self, conditional_expression):
        # type: (ConditionalExpression) -> None
        pass

    def visit_member_access_expression(self, member_access_expression):
        # type: (MemberAccessExpression) -> None
        pass

    def visit_member_access_ptr_expression(self, member_access_ptr_expression):
        # type: (MemberAccessPtrExpression) -> None
        pass

    def visit_member_ptr_expression(self, member_ptr_expression):
        # type: (MemberPtrExpression) -> None
        pass

    def visit_type_id_expression(self, type_id_expression):
        # type: (TypeIdExpression) -> None
        pass

    def visit_type_id_expression_type(self, type_id_expression_type):
        # type: (TypeIdExpressionType) -> None
        pass

    def visit_simple_cast_expression(self, simple_cast_expression):
        # type: (SimpleCastExpression) -> None
        pass

    def visit_new_expression(self, new_expression):
        # type: (NewExpression) -> None
        pass

    def visit_delete_expression(self, delete_expression):
        # type: (DeleteExpression) -> None
        pass

    def visit_throw_expression(self, throw_expression):
        # type: (ThrowExpression) -> None
        pass

    def visit_yield_expression(self, yield_expression):
        # type: (YieldExpression) -> None
        pass

    def visit_await_expression(self, await_expression):
        # type: (AwaitExpression) -> None
        pass

    def visit_fold_expression_left(self, fold_expression_left):
        # type: (FoldExpressionLeft) -> None
        pass

    def visit_fold_expression_right(self, fold_expression_right):
        # type: (FoldExpressionRight) -> None
        pass

    def visit_fold_expression_both(self, fold_expression_both):
        # type: (FoldExpressionBoth) -> None
        pass

    def visit_parenthesized_expression(self, parenthesized_expression):
        # type: (ParenthesizedExpression) -> None
        pass

    def visit_this_expression(self, this_expression):
        # type: (ThisExpression) -> None
        pass

    def visit_null_ptr_expression(self, null_ptr_expression):
        # type: (NullPtrExpression) -> None
        pass

    def visit_type_trait_expression(self, type_trait_expression):
        # type: (TypeTraitExpression) -> None
        pass

    def visit_braced_init_list(self, braced_init_list):
        # type: (BracedInitList) -> None
        pass

    def visit_designated_braced_init_list(self, designated_braced_init_list):
        # type: (DesignatedBracedInitList) -> None
        pass

    def visit_designated_initializer(self, designated_initializer):
        # type: (DesignatedInitializer) -> None
        pass

    def visit_boolean_literal(self, boolean_literal):
        # type: (BooleanLiteral) -> None
        pass

    def visit_integer_literal(self, integer_literal):
        # type: (IntegerLiteral) -> None
        pass

    def visit_user_defined_integer_literal(self, user_defined_integer_literal):
        # type: (UserDefinedIntegerLiteral) -> None
        pass

    def visit_character_literal(self, character_literal):
        # type: (CharacterLiteral) -> None
        pass

    def visit_user_defined_character_literal(self, user_defined_character_literal):
        # type: (UserDefinedCharacterLiteral) -> None
        pass

    def visit_string_literal(self, string_literal):
        # type: (StringLiteral) -> None
        pass

    def visit_string_literal_macro(self, string_literal_macro):
        # type: (StringLiteralMacro) -> None
        pass

    def visit_user_defined_string_literal(self, user_defined_string_literal):
        # type: (UserDefinedStringLiteral) -> None
        pass

    def visit_string_list(self, string_list):
        # type: (StringList) -> None
        pass

    def visit_floating_literal(self, floating_literal):
        # type: (FloatingLiteral) -> None
        pass

    def visit_user_defined_floating_literal(self, user_defined_floating_literal):
        # type: (UserDefinedFloatingLiteral) -> None
        pass

    def visit_lambda_expression(self, lambda_expression):
        # type: (LambdaExpression) -> None
        pass

    def visit_template_lambda_expression(self, template_lambda_expression):
        # type: (TemplateLambdaExpression) -> None
        pass

    def visit_lambda_capture_default_copy(self, lambda_capture_default_copy):
        # type: (LambdaCaptureDefaultCopy) -> None
        pass

    def visit_lambda_capture_default_reference(self, lambda_capture_default_reference):
        # type: (LambdaCaptureDefaultReference) -> None
        pass

    def visit_lambda_capture_list(self, lambda_capture_list):
        # type: (LambdaCaptureList) -> None
        pass

    def visit_simple_capture(self, simple_capture):
        # type: (SimpleCapture) -> None
        pass

    def visit_this_capture(self, this_capture):
        # type: (ThisCapture) -> None
        pass

    def visit_lambda_specifier(self, lambda_specifier):
        # type: (LambdaSpecifier) -> None
        pass

    def visit_lambda_declarator(self, lambda_declarator):
        # type: (LambdaDeclarator) -> None
        pass


if TYPE_CHECKING:

    from .translation_unit import TranslationUnit
    from .module import ModuleDeclaration, ModuleImportDeclaration, PrivateModuleFragment, ExportDeclaration, GlobalModuleFragment
    from .declarations import AmbiguousDeclaration, SimpleDeclaration, StructuredBindingDeclaration, StaticAssert, AliasDeclaration, NamespaceDeclaration, NamespaceAliasDeclaration, UsingDirective, UsingDeclaration, UsingEnumDeclaration, AsmDeclaration, LinkageSpecification, OpaqueEnumDeclaration, AmbiguousInitDeclarator, InitDeclarator, MemberInitDeclarator, InitDeclaratorList, AmbiguousInitDeclaratorList, DeclSpecifierSeq, DeclarationSpecifier, DeclarationSpecifierMacro, StorageClassSpecifier, StorageClassSpecifierMacro, ExplicitSpecifier, ConceptDefinition, ExplicitSpecialization, ExplicitInstantiation, DeductionGuide
    from .function import FunctionDefinition, SimpleParameterClause, AmbiguousParameterClause, ParameterDeclaration, TryFunctionBody, PureVirtualFunctionBody, DefaultFunctionBody, DeletedFunctionBody, StatementFunctionBody, VirtSpecifierFinal, VirtSpecifierOverride, VirtSpecifierPure, VirtSpecifierMacro
    from .klass import AccessSpecifierDefault, AccessSpecifierPublic, AccessSpecifierProtected, AccessSpecifierPrivate, AccessSpecifierMacro, ClassSpecifier, BaseSpecifier, MemberInitializer, MemInitializerIdMember, MemInitializerIdBase, AmbiguousMemInitializerId
    from .enumeration import EnumSpecifier, Enumerator
    from .template import Declaration, TemplateDeclaration, TemplateArgumentPackExpand, AmbiguousTemplateArgument, TemplateArgumentConstant, TemplateArgumentTypeId, AmbiguousTemplateParameter, TemplateParameterType, TemplateParameterTemplate, TemplateParameterConstant, TemplateParameterConstraint
    from .attributes import AttributeNamedList, AttributeNamed, AttributeAlignAsType, AttributeAlignAsExpression, AttributeAlignAsAmbiguous, AttributeAlignAsAmbiguousPack, AttributeDocumentation, AttributeMacro
    from .constraints import RequiresExpression, RequirementBody, AmbiguousRequirement, SimpleRequirement, TypeRequirement, CompoundRequirement, NestedRequirement, RequiresClause
    from .pack import PackExpandType, PackExpandExpression, PackExpandAttributeNamed
    from .statements import AmbiguousStatement, EmptyStatement, ExpressionStatement, DeclarationStatement, CompoundStatement, TryBlock, ExceptionHandler, ExceptionDeclarationTypeSpecifier, ExceptionDeclarationAny, AmbiguousExceptionDeclaration, BreakStatement, ContinueStatement, ReturnStatement, CoReturnStatement, GotoStatement, LabeledStatement, CaseStatement, DefaultStatement, SelectionCondition, AmbiguousSelectionCondition, SwitchStatement, IfStatement, IfConstevalStatement, WhileStatement, DoWhileStatement, ForStatement, AmbiguousForCondition, ForConditionInit, ForConditionRange
    from .type import CvQualifier, RefQualifier, DynamicExceptionSpecifier, NoExceptSpecifier, PrimitiveTypeSpecifier, ElaboratedClassTypeSpecifier, ElaboratedEnumTypeSpecifier, AutoTypeSpecifier, DecltypeTypeSpecifier, DecltypeAutoTypeSpecifier, ConstrainedTypeSpecifier, TypeSpecifierReference, AmbiguousTypeSpecifier, CvQualifiers, RefQualifiers, TypeSpecifierSeq, DefiningTypeSpecifierSeq, DeclaratorElementId, DeclaratorElementPackId, DeclaratorElementAbstractPackId, DeclaratorElementPointer, DeclaratorElementReference, DeclaratorElementRValueReference, DeclaratorElementArray, DeclaratorElementMethod, AbstractDeclaratorList, DeclaratorList, AmbiguousAbstractDeclarator, TypeIdDeclarator, AmbiguousTypeId, TypeIdPack
    from .expressions import ExpressionList, IdExpression, AmbiguousExpression, LiteralExpression, UnaryExpression, BinaryExpression, PostfixExpression, SizeofExpression, SizeofTypeExpression, SizeofPackExpression, AlignofExpression, NoexceptExpression, CallExpression, SubscriptExpression, CastExpression, CxxCastExpression, ConditionalExpression, MemberAccessExpression, MemberAccessPtrExpression, MemberPtrExpression, TypeIdExpression, TypeIdExpressionType, SimpleCastExpression, NewExpression, DeleteExpression, ThrowExpression, YieldExpression, AwaitExpression, FoldExpressionLeft, FoldExpressionRight, FoldExpressionBoth, ParenthesizedExpression, ThisExpression, NullPtrExpression, TypeTraitExpression
    from .literals import BracedInitList, DesignatedBracedInitList, DesignatedInitializer, BooleanLiteral, IntegerLiteral, UserDefinedIntegerLiteral, CharacterLiteral, UserDefinedCharacterLiteral, StringLiteral, StringLiteralMacro, UserDefinedStringLiteral, StringList, FloatingLiteral, UserDefinedFloatingLiteral
    from .lambdas import LambdaExpression, TemplateLambdaExpression, LambdaCaptureDefaultCopy, LambdaCaptureDefaultReference, LambdaCaptureList, SimpleCapture, ThisCapture, LambdaSpecifier, LambdaDeclarator
