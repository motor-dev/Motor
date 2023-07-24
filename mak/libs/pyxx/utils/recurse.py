from .. import ast
from typing import Optional


class RecursiveVisitor(object):

    def visit_translation_unit(self, translation_unit: ast.TranslationUnit) -> None:
        translation_unit.visit_children(self)

    def visit_module_declaration(self, module_declaration: ast.ModuleDeclaration) -> None:
        module_declaration.accept(self)

    def visit_module_import_declaration(self, module_import_declaration: ast.ModuleImportDeclaration) -> None:
        module_import_declaration.accept_attributes(self)

    def visit_private_module_fragment(self, private_module_fragment: ast.PrivateModuleFragment) -> None:
        private_module_fragment.accept_declarations(self)

    def visit_export_declaration(self, export_declaration: ast.ExportDeclaration) -> None:
        export_declaration.accept_declarations(self)

    def visit_global_module_fragment(self, global_module_fragment: ast.GlobalModuleFragment) -> None:
        global_module_fragment.accept_declarations(self)

    def visit_type_specifier_seq(self, type_specifier_seq: ast.TypeSpecifierSeq) -> None:
        type_specifier_seq.accept_attributes(self)
        type_specifier_seq.accept_qualifiers(self)
        type_specifier_seq.accept_types(self)

    def visit_ambiguous_declaration(self, ambiguous_declaration: ast.AmbiguousDeclaration) -> None:
        ambiguous_declaration.accept_first(self)

    def visit_simple_declaration(self, simple_declaration: ast.SimpleDeclaration) -> None:
        simple_declaration.accept_attributes(self)
        simple_declaration.accept_decl_specifier_seq(self)
        simple_declaration.accept_init_declarator_list(self)

    def visit_structured_binding_declaration(
            self, structured_binding_declaration: ast.StructuredBindingDeclaration
    ) -> None:
        structured_binding_declaration.accept_attributes(self)
        structured_binding_declaration.accept_decl_specifier_seq(self)
        structured_binding_declaration.accept_ref_qualifier(self)
        structured_binding_declaration.accept_initializer(self)

    def visit_static_assert(self, static_assert: ast.StaticAssert) -> None:
        static_assert.accept_condition(self)
        static_assert.accept_message(self)

    def visit_alias_declaration(self, alias_declaration: ast.AliasDeclaration) -> None:
        alias_declaration.accept_attributes(self)
        alias_declaration.accept_alias_attributes(self)
        alias_declaration.accept_type_id(self)

    def visit_namespace_declaration(self, namespace_declaration: ast.NamespaceDeclaration) -> None:
        namespace_declaration.accept_attributes(self)
        namespace_declaration.accept_children(self)

    def visit_namespace_alias_declaration(self, namespace_alias_declaration: ast.NamespaceAliasDeclaration) -> None:
        namespace_alias_declaration.accept_attributes(self)
        namespace_alias_declaration.accept_reference(self)

    def visit_using_directive(self, using_directive: ast.UsingDirective) -> None:
        using_directive.accept_attributes(self)
        using_directive.accept_reference(self)

    def visit_using_declaration(self, using_declaration: ast.UsingDeclaration) -> None:
        using_declaration.accept_attributes(self)
        using_declaration.accept_reference_list(self)

    def visit_using_enum_declaration(self, using_enum_declaration: ast.UsingEnumDeclaration) -> None:
        using_enum_declaration.accept_attributes(self)
        using_enum_declaration.accept_enum_specifier(self)

    def visit_asm_declaration(self, asm_declaration: ast.AsmDeclaration) -> None:
        asm_declaration.accept_attributes(self)

    def visit_linkage_specification(self, linkage_specification: ast.LinkageSpecification) -> None:
        linkage_specification.accept_attributes(self)
        linkage_specification.accept_declarations(self)

    def visit_opaque_enum_declaration(self, opaque_enum_declaration: ast.OpaqueEnumDeclaration) -> None:
        opaque_enum_declaration.accept_attributes(self)
        opaque_enum_declaration.accept_name(self)
        opaque_enum_declaration.accept_base_type(self)

    def visit_ambiguous_init_declarator(self, ambiguous_init_declarator: ast.AmbiguousInitDeclarator) -> None:
        ambiguous_init_declarator.accept_best(self)

    def visit_init_declarator(self, init_declarator: ast.InitDeclarator) -> None:
        init_declarator.accept_declarator(self)
        init_declarator.accept_init_value(self)
        init_declarator.accept_constraint(self)

    def visit_member_init_declarator(self, member_init_declarator: ast.MemberInitDeclarator) -> None:
        member_init_declarator.accept_declarator(self)
        member_init_declarator.accept_init_value(self)
        member_init_declarator.accept_constraint(self)
        member_init_declarator.acceot_virt_specifiers(self)
        member_init_declarator.accept_bitfield_width(self)

    def visit_init_declarator_list(self, init_declarator_list: ast.InitDeclaratorList) -> None:
        init_declarator_list.accept_init_declarators(self)

    def visit_ambiguous_init_declarator_list(
            self, ambiguous_init_declarator_list: ast.AmbiguousInitDeclaratorList
    ) -> None:
        ambiguous_init_declarator_list.accept_best(self)

    def visit_decl_specifier_seq(self, decl_specifier_seq: ast.DeclSpecifierSeq) -> None:
        decl_specifier_seq.accept_decl_specifiers(self)
        decl_specifier_seq.accept_type_specifier_seq(self)

    def visit_explicit_specifier(self, explicit_specifier: ast.ExplicitSpecifier) -> None:
        explicit_specifier.accept_expression(self)

    def visit_concept_definition(self, concept_definition: ast.ConceptDefinition) -> None:
        concept_definition.accept_constraint_expression(self)

    def visit_explicit_specialization(self, explicit_specialization: ast.ExplicitSpecialization) -> None:
        explicit_specialization.accept_declaration(self)

    def visit_explicit_instantiation(self, explicit_instantiation: ast.ExplicitInstantiation) -> None:
        explicit_instantiation.accept_declaration(self)

    def visit_deduction_guide(self, deduction_guide: ast.DeductionGuide) -> None:
        deduction_guide.accept_attributes(self)
        deduction_guide.accept_explicit_specifier(self)
        deduction_guide.accept_parameter_clause(self)
        deduction_guide.accept_template_id(self)

    def visit_function_definition(self, function_definition: ast.FunctionDefinition) -> None:
        function_definition.accept_attributes(self)
        function_definition.accept_decl_specifier_seq(self)
        function_definition.accept_declarator(self)
        function_definition.accept_requires_clause(self)
        function_definition.accept_virt_specifier_seq(self)
        function_definition.accept_function_body(self)

    def visit_simple_parameter_clause(self, simple_parameter_clause: ast.SimpleParameterClause) -> None:
        simple_parameter_clause.accept_parameter_list(self)

    def visit_ambiguous_parameter_clause(self, ambiguous_parameter_clause: ast.AmbiguousParameterClause) -> None:
        ambiguous_parameter_clause.accept_first(self)

    def visit_parameter_declaration(self, parameter_declaration: ast.ParameterDeclaration) -> None:
        parameter_declaration.accept_attributes(self)
        parameter_declaration.accept_decl_specifier_seq(self)
        parameter_declaration.accept_declarator(self)
        parameter_declaration.accept_default_value(self)

    def visit_try_function_body(self, try_function_body: ast.TryFunctionBody) -> None:
        try_function_body.accept_statement_function_body(self)
        try_function_body.accept_handler_list(self)

    def visit_statement_function_body(self, statement_function_body: ast.StatementFunctionBody) -> None:
        statement_function_body.accept_constructor_initializer(self)
        statement_function_body.accept_statement_list(self)

    def visit_class_specifier(self, class_specifier: ast.ClassSpecifier) -> None:
        class_specifier.accept_attributes(self)
        class_specifier.accept_name(self)
        class_specifier.accept_base_clause(self)
        class_specifier.accept_members(self)

    def visit_base_clause(self, base_clause: ast.BaseClause) -> None:
        base_clause.accept_base_specifiers(self)

    def visit_ambiguous_base_clause(self, ambiguous_base_clause: ast.AmbiguousBaseClause) -> None:
        ambiguous_base_clause.accept_first_base_clause(self)

    def visit_base_specifier(self, base_specifier: ast.BaseSpecifier) -> None:
        base_specifier.accept_attributes(self)
        base_specifier.accept_access_specifier(self)
        base_specifier.accept_base_type(self)

    def visit_member_declaration(self, access_specifier: ast.AccessSpecifier,
                                 member_declaration: ast.Declaration) -> None:
        member_declaration.accept(self)

    def visit_member_initializer(self, member_initializer: ast.MemberInitializer) -> None:
        member_initializer.accept_mem_initializer_id(self)
        member_initializer.accept_value(self)

    def visit_mem_initializer_id_base(self, mem_initializer_id_base: ast.MemInitializerIdBase) -> None:
        mem_initializer_id_base.accept_base(self)

    def visit_ambiguous_mem_initializer_id(self, ambiguous_mem_initializer_id: ast.AmbiguousMemInitializerId) -> None:
        ambiguous_mem_initializer_id.accept_first(self)

    def visit_enum_specifier(self, enum_specifier: ast.EnumSpecifier) -> None:
        enum_specifier.accept_attributes(self)
        enum_specifier.accept_name(self)
        enum_specifier.accept_base_type(self)
        enum_specifier.accept_enumerators(self)

    def visit_enumerator(self, enumerator: ast.Enumerator) -> None:
        enumerator.accept_attributes(self)
        enumerator.accept_value(self)

    def visit_template_declaration(self, template_declaration: ast.TemplateDeclaration) -> None:
        pass

    def visit_template_argument_error(self, template_argument_error: ast.TemplateArgumentError) -> None:
        pass

    def visit_template_argument_pack_expand(self,
                                            template_argument_pack_expand: ast.TemplateArgumentPackExpand) -> None:
        pass

    def visit_ambiguous_template_argument(self, ambiguous_template_argument: ast.AmbiguousTemplateArgument) -> None:
        pass

    def visit_template_argument_constant(self, template_argument_constant: ast.TemplateArgumentConstant) -> None:
        pass

    def visit_template_argument_type_id(self, template_argument_type_id: ast.TemplateArgumentTypeId) -> None:
        pass

    def visit_ambiguous_template_parameter(self, ambiguous_template_parameter: ast.AmbiguousTemplateParameter) -> None:
        pass

    def visit_template_parameter_type(self, template_parameter_type: ast.TemplateParameterType) -> None:
        pass

    def visit_template_parameter_template(self, template_parameter_template: ast.TemplateParameterTemplate) -> None:
        pass

    def visit_template_parameter_constant(self, template_parameter_constant: ast.TemplateParameterConstant) -> None:
        pass

    def visit_template_parameter_constraint(self,
                                            template_parameter_constraint: ast.TemplateParameterConstraint) -> None:
        pass

    def visit_attribute_named_list(self, attribute_named_list: ast.AttributeNamedList) -> None:
        pass

    def visit_attribute_error(self, attribute_error: ast.AttributeError) -> None:
        pass

    def visit_attribute_named(self, using_namespace: Optional[str], attribute_named: ast.AttributeNamed) -> None:
        pass

    def visit_attribute_align_as_type(self, attribute_align_as_type: ast.AttributeAlignAsType) -> None:
        pass

    def visit_attribute_align_as_expression(self,
                                            attribute_align_as_expression: ast.AttributeAlignAsExpression) -> None:
        pass

    def visit_attribute_align_as_ambiguous(self, attribute_align_as_ambiguous: ast.AttributeAlignAsAmbiguous) -> None:
        pass

    def visit_attribute_documentation(self, attribute_documentation: ast.AttributeDocumentation) -> None:
        pass

    def visit_attribute_macro(self, attribute_macro: ast.AttributeMacro) -> None:
        pass

    def visit_requires_expression(self, requires_expression: ast.RequiresExpression) -> None:
        pass

    def visit_error_requirement(self, error_requirement: ast.ErrorRequirement) -> None:
        pass

    def visit_requirement_body(self, requirement_body: ast.RequirementBody) -> None:
        pass

    def visit_ambiguous_requirement(self, ambiguous_requirement: ast.AmbiguousRequirement) -> None:
        pass

    def visit_simple_requirement(self, simple_requirement: ast.SimpleRequirement) -> None:
        pass

    def visit_type_requirement(self, type_requirement: ast.TypeRequirement) -> None:
        pass

    def visit_compound_requirement(self, compound_requirement: ast.CompoundRequirement) -> None:
        pass

    def visit_nested_requirement(self, nested_requirement: ast.NestedRequirement) -> None:
        pass

    def visit_requires_clause(self, requires_clause: ast.RequiresClause) -> None:
        pass

    def visit_pack_expand_type(self, pack_expand_type: ast.PackExpandType) -> None:
        pass

    def visit_pack_expand_expression(self, pack_expand_expression: ast.PackExpandExpression) -> None:
        pass

    def visit_pack_expand_attribute_named(self, pack_expand_attribute_named: ast.PackExpandAttributeNamed) -> None:
        pass

    def visit_statement_with_attributes(self, statement_with_attributes: ast.StatementWithAttributes) -> None:
        pass

    def visit_error_statement(self, error_statement: ast.ErrorStatement) -> None:
        pass

    def visit_ambiguous_statement(self, ambiguous_statement: ast.AmbiguousStatement) -> None:
        pass

    def visit_empty_statement(self, empty_statement: ast.EmptyStatement) -> None:
        pass

    def visit_expression_statement(self, expression_statement: ast.ExpressionStatement) -> None:
        pass

    def visit_declaration_statement(self, declaration_statement: ast.DeclarationStatement) -> None:
        pass

    def visit_compound_statement(self, compound_statement: ast.CompoundStatement) -> None:
        pass

    def visit_try_block(self, try_block: ast.TryBlock) -> None:
        pass

    def visit_exception_handler(self, exception_handler: ast.ExceptionHandler) -> None:
        pass

    def visit_exception_declaration_error(self, exception_declaration_error: ast.ExceptionDeclarationError) -> None:
        pass

    def visit_exception_declaration_type_specifier(
            self, exception_declaration_type_specifier: ast.ExceptionDeclarationTypeSpecifier
    ) -> None:
        pass

    def visit_exception_declaration_any(self, exception_declaration_any: ast.ExceptionDeclarationAny) -> None:
        pass

    def visit_ambiguous_exception_declaration(
            self, ambiguous_exception_declaration: ast.AmbiguousExceptionDeclaration
    ) -> None:
        pass

    def visit_break_statement(self, break_statement: ast.BreakStatement) -> None:
        pass

    def visit_continue_statement(self, continue_statement: ast.ContinueStatement) -> None:
        pass

    def visit_return_statement(self, return_statement: ast.ReturnStatement) -> None:
        pass

    def visit_co_return_statement(self, co_return_statement: ast.CoReturnStatement) -> None:
        pass

    def visit_goto_statement(self, goto_statement: ast.GotoStatement) -> None:
        pass

    def visit_labeled_statement(self, labeled_statement: ast.LabeledStatement) -> None:
        pass

    def visit_case_statement(self, case_statement: ast.CaseStatement) -> None:
        pass

    def visit_default_statement(self, default_statement: ast.DefaultStatement) -> None:
        pass

    def visit_selection_condition(self, selection_condition: ast.SelectionCondition) -> None:
        pass

    def visit_ambiguous_selection_condition(self,
                                            ambiguous_selection_condition: ast.AmbiguousSelectionCondition) -> None:
        pass

    def visit_switch_statement(self, switch_statement: ast.SwitchStatement) -> None:
        pass

    def visit_if_statement(self, if_statement: ast.IfStatement) -> None:
        pass

    def visit_if_consteval_statement(self, if_consteval_statement: ast.IfConstevalStatement) -> None:
        pass

    def visit_while_statement(self, while_statement: ast.WhileStatement) -> None:
        pass

    def visit_do_while_statement(self, do_while_statement: ast.DoWhileStatement) -> None:
        pass

    def visit_for_statement(self, for_statement: ast.ForStatement) -> None:
        pass

    def visit_ambiguous_for_condition(self, ambiguous_for_condition: ast.AmbiguousForCondition) -> None:
        pass

    def visit_for_condition_init(self, for_condition_init: ast.ForConditionInit) -> None:
        pass

    def visit_for_condition_range(self, for_condition_range: ast.ForConditionRange) -> None:
        pass

    def visit_cv_qualifier(self, cv_qualifie: ast.CvQualifier) -> None:
        pass

    def visit_ref_qualifier(self, ref_qualifier: ast.RefQualifier) -> None:
        pass

    def visit_exception_specifier_error(self, exception_specifier_error: ast.ExceptionSpecifierError) -> None:
        pass

    def visit_dynamic_exception_specifier(self, dynamic_exception_specifier: ast.DynamicExceptionSpecifier) -> None:
        pass

    def visit_ambiguous_exception_specifier(self,
                                            ambiguous_exception_specifier: ast.AmbiguousExceptionSpecifier) -> None:
        pass

    def visit_noexcept_specifier(self, noexcept_specifier: ast.NoExceptSpecifier) -> None:
        pass

    def visit_primitive_type_specifier(self, primitive_type_specifier: ast.PrimitiveTypeSpecifier) -> None:
        pass

    def visit_elaborated_class_type_specifier(
            self, elaborated_class_type_specifier: ast.ElaboratedClassTypeSpecifier
    ) -> None:
        pass

    def visit_elaborated_enum_type_specifier(
            self, elaborated_enum_type_specifier: ast.ElaboratedEnumTypeSpecifier
    ) -> None:
        pass

    def visit_error_type_specifier(self, error_type_specifier: ast.ErrorTypeSpecifier) -> None:
        pass

    def visit_auto_type_specifier(self, auto_type_specifier: ast.AutoTypeSpecifier) -> None:
        pass

    def visit_decltype_type_specifier(self, decltype_type_specifier: ast.DecltypeTypeSpecifier) -> None:
        pass

    def visit_decltype_auto_type_specifier(self, decltype_auto_type_specifier: ast.DecltypeAutoTypeSpecifier) -> None:
        pass

    def visit_constrained_type_specifier(self, constrained_type_specifier: ast.ConstrainedTypeSpecifier) -> None:
        pass

    def visit_type_specifier_reference(self, type_specifier_reference: ast.TypeSpecifierReference) -> None:
        pass

    def visit_ambiguous_type_specifier(self, ambiguous_type_specifier: ast.AmbiguousTypeSpecifier) -> None:
        pass

    def visit_cv_qualifiers(self, cv_qualifiers: ast.CvQualifiers) -> None:
        pass

    def visit_ref_qualifiers(self, ref_qualifiers: ast.RefQualifiers) -> None:
        pass

    def visit_defining_type_specifier_seq(self, defining_type_specifier_seq: ast.DefiningTypeSpecifierSeq) -> None:
        pass

    def visit_declarator_element_error(self, declarator_element_error: ast.DeclaratorElementError) -> None:
        pass

    def visit_declarator_element_id(self, declarator_element_id: ast.DeclaratorElementId) -> None:
        pass

    def visit_declarator_element_pack_id(self, declarator_element_pack_id: ast.DeclaratorElementPackId) -> None:
        pass

    def visit_declarator_element_abstract(self, declarator_element_abstract: ast.DeclaratorElementAbstract) -> None:
        pass

    def visit_declarator_element_abstract_pack(
            self, declarator_element_abstract_pack: ast.DeclaratorElementAbstractPack
    ) -> None:
        pass

    def visit_declarator_element_group(self, declarator_element_group: ast.DeclaratorElementGroup) -> None:
        pass

    def visit_declarator_element_pointer(self, declarator_element_pointer: ast.DeclaratorElementPointer) -> None:
        pass

    def visit_declarator_element_reference(self, declarator_element_reference: ast.DeclaratorElementReference) -> None:
        pass

    def visit_declarator_element_rvalue_reference(
            self, declarator_element_rvalue_reference: ast.DeclaratorElementRValueReference
    ) -> None:
        pass

    def visit_declarator_element_array(self, declarator_element_array: ast.DeclaratorElementArray) -> None:
        pass

    def visit_declarator_element_method(self, declarator_element_method: ast.DeclaratorElementMethod) -> None:
        pass

    def visit_abstract_declarator_list(self, abstract_declarator_list: ast.AbstractDeclaratorList) -> None:
        pass

    def visit_declarator_list(self, declarator_list: ast.DeclaratorList) -> None:
        pass

    def visit_ambiguous_abstract_declarator(self,
                                            ambiguous_abstract_declarator: ast.AmbiguousAbstractDeclarator) -> None:
        pass

    def visit_type_id_declarator(self, type_id_declarator: ast.TypeIdDeclarator) -> None:
        pass

    def visit_ambiguous_type_id(self, ambiguous_type_id: ast.AmbiguousTypeId) -> None:
        pass

    def visit_type_id_pack(self, type_id_pack: ast.TypeIdPack) -> None:
        pass

    def visit_error_expression(self, error_expression: ast.ErrorExpression) -> None:
        pass

    def visit_initializer_list(self, initializer_list: ast.InitializerList) -> None:
        pass

    def visit_ambiguous_initializer_list(self, ambiguous_initializer_list: ast.AmbiguousInitializerList) -> None:
        pass

    def visit_id_expression(self, id_expression: ast.IdExpression) -> None:
        pass

    def visit_ambiguous_expression(self, ambiguous_expression: ast.AmbiguousExpression) -> None:
        pass

    def visit_unary_expression(self, unary_expression: ast.UnaryExpression) -> None:
        pass

    def visit_binary_expression(self, binary_expression: ast.BinaryExpression) -> None:
        pass

    def visit_postfix_expression(self, postfix_expression: ast.PostfixExpression) -> None:
        pass

    def visit_sizeof_expression(self, sizeof_expression: ast.SizeofExpression) -> None:
        pass

    def visit_sizeof_type_expression(self, sizeof_type_expression: ast.SizeofTypeExpression) -> None:
        pass

    def visit_sizeof_pack_expression(self, sizeof_pack_expression: ast.SizeofPackExpression) -> None:
        pass

    def visit_alignof_expression(self, alignof_expression: ast.AlignofExpression) -> None:
        pass

    def visit_noexcept_expression(self, noexcept_expression: ast.NoexceptExpression) -> None:
        pass

    def visit_call_expression(self, call_expression: ast.CallExpression) -> None:
        pass

    def visit_subscript_expression(self, subscript_expression: ast.SubscriptExpression) -> None:
        pass

    def visit_cast_expression(self, cast_expression: ast.CastExpression) -> None:
        pass

    def visit_cxx_cast_expression(self, cxx_cast_expression: ast.CxxCastExpression) -> None:
        pass

    def visit_conditional_expression(self, conditional_expression: ast.ConditionalExpression) -> None:
        pass

    def visit_member_access_expression(self, member_access_expression: ast.MemberAccessExpression) -> None:
        pass

    def visit_member_access_ptr_expression(self, member_access_ptr_expression: ast.MemberAccessPtrExpression) -> None:
        pass

    def visit_member_ptr_expression(self, member_ptr_expression: ast.MemberPtrExpression) -> None:
        pass

    def visit_type_id_expression(self, type_id_expression: ast.TypeIdExpression) -> None:
        pass

    def visit_type_id_expression_type(self, type_id_expression_type: ast.TypeIdExpressionType) -> None:
        pass

    def visit_simple_cast_expression(self, simple_cast_expression: ast.SimpleCastExpression) -> None:
        pass

    def visit_new_expression(self, new_expression: ast.NewExpression) -> None:
        pass

    def visit_delete_expression(self, delete_expression: ast.DeleteExpression) -> None:
        pass

    def visit_throw_expression(self, throw_expression: ast.ThrowExpression) -> None:
        pass

    def visit_yield_expression(self, yield_expression: ast.YieldExpression) -> None:
        pass

    def visit_await_expression(self, await_expression: ast.AwaitExpression) -> None:
        pass

    def visit_fold_expression_left(self, fold_expression_left: ast.FoldExpressionLeft) -> None:
        pass

    def visit_fold_expression_right(self, fold_expression_right: ast.FoldExpressionRight) -> None:
        pass

    def visit_fold_expression_both(self, fold_expression_both: ast.FoldExpressionBoth) -> None:
        pass

    def visit_parenthesized_expression(self, parenthesized_expression: ast.ParenthesizedExpression) -> None:
        pass

    def visit_this_expression(self, this_expression: ast.ThisExpression) -> None:
        pass

    def visit_nullptr_expression(self, nullptr_expression: ast.NullPtrExpression) -> None:
        pass

    def visit_type_trait_expression(self, type_trait_expression: ast.TypeTraitExpression) -> None:
        pass

    def visit_braced_init_list(self, braced_init_list: ast.BracedInitList) -> None:
        pass

    def visit_ambiguous_braced_init_list(self, ambiguous_braced_init_list: ast.AmbiguousBracedInitList) -> None:
        pass

    def visit_designated_braced_init_list(self, designated_braced_init_list: ast.DesignatedBracedInitList) -> None:
        pass

    def visit_designated_initializer(self, designated_initializer: ast.DesignatedInitializer) -> None:
        pass

    def visit_boolean_literal(self, boolean_literal: ast.BooleanLiteral) -> None:
        pass

    def visit_integer_literal(self, integer_literal: ast.IntegerLiteral) -> None:
        pass

    def visit_user_defined_integer_literal(self, user_defined_integer_literal: ast.UserDefinedIntegerLiteral) -> None:
        pass

    def visit_character_literal(self, character_literal: ast.CharacterLiteral) -> None:
        pass

    def visit_user_defined_character_literal(
            self, user_defined_character_literal: ast.UserDefinedCharacterLiteral
    ) -> None:
        pass

    def visit_string_literal(self, string_literal: ast.StringLiteral) -> None:
        pass

    def visit_string_literal_macro(self, string_literal_macro: ast.StringLiteralMacro) -> None:
        pass

    def visit_user_defined_string_literal(self, user_defined_string_literal: ast.UserDefinedStringLiteral) -> None:
        pass

    def visit_string_list(self, string_list: ast.StringList) -> None:
        pass

    def visit_floating_literal(self, floating_literal: ast.FloatingLiteral) -> None:
        pass

    def visit_user_defined_floating_literal(self,
                                            user_defined_floating_literal: ast.UserDefinedFloatingLiteral) -> None:
        pass

    def visit_lambda_expression(self, lambda_expression: ast.LambdaExpression) -> None:
        pass

    def visit_template_lambda_expression(self, template_lambda_expression: ast.TemplateLambdaExpression) -> None:
        pass

    def visit_lambda_capture_default_copy(self, lambda_capture_default_copy: ast.LambdaCaptureDefaultCopy) -> None:
        pass

    def visit_lambda_capture_default_reference(
            self, lambda_capture_default_reference: ast.LambdaCaptureDefaultReference
    ) -> None:
        pass

    def visit_lambda_capture_list(self, lambda_capture_list: ast.LambdaCaptureList) -> None:
        pass

    def visit_simple_capture(self, simple_capture: ast.SimpleCapture) -> None:
        pass

    def visit_this_capture(self, this_capture: ast.ThisCapture) -> None:
        pass

    def visit_lambda_specifier(self, lambda_specifier: ast.LambdaSpecifier) -> None:
        pass

    def visit_lambda_declarator(self, lambda_declarator: ast.LambdaDeclarator) -> None:
        pass

    def visit_reference(self, reference: ast.Reference) -> None:
        pass

    def visit_typename_reference(self, typename_reference: ast.TypenameReference) -> None:
        pass

    def visit_pack_expand_reference(self, typename_reference: ast.PackExpandReference) -> None:
        pass

    def visit_root_id(self, root_id: ast.RootId) -> None:
        pass

    def visit_template_specifier_id(self, template_specifier_id: ast.TemplateSpecifierId) -> None:
        pass

    def visit_id(self, id: ast.Id) -> None:
        pass

    def visit_template_id(self, template_id: ast.TemplateId) -> None:
        pass

    def visit_template_argument_list(self, template_argument_list: ast.TemplateArgumentList) -> None:
        pass

    def visit_ambiguous_template_argument_list(
            self, ambiguous_template_argument_list: ast.AmbiguousTemplateArgumentList
    ) -> None:
        pass

    def visit_destructor_id(self, destructor_id: ast.DestructorId) -> None:
        pass

    def visit_operator_id(self, operator_id: ast.OperatorId) -> None:
        pass

    def visit_conversion_operator_id(self, conversion_operator_id: ast.ConversionOperatorId) -> None:
        pass

    def visit_literal_operator_id(self, literal_operator_id: ast.LiteralOperatorId) -> None:
        pass
