from .. import ast


class RecursiveVisitor(ast.Visitor):

    def visit_translation_unit(self, translation_unit: ast.TranslationUnit) -> None:
        translation_unit.accept_children(self)

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
        template_declaration.accept_attributes(self)
        template_declaration.accept_parameter_list(self)
        template_declaration.accept_requires_clause(self)
        template_declaration.accept_declaration(self)

    def visit_template_parameter_list(self, template_parameter_list: ast.TemplateParameterList) -> None:
        template_parameter_list.accept_parameters(self)

    def visit_ambiguous_template_parameter_list(self,
                                                ambiguous_template_parameter_list: ast.AmbiguousTemplateParameterList) \
            -> None:
        ambiguous_template_parameter_list.accept_first(self)

    def visit_template_argument_pack_expand(self,
                                            template_argument_pack_expand: ast.TemplateArgumentPackExpand) -> None:
        template_argument_pack_expand.accept_argument(self)

    def visit_ambiguous_template_argument(self, ambiguous_template_argument: ast.AmbiguousTemplateArgument) -> None:
        ambiguous_template_argument.accept_first(self)

    def visit_template_argument_constant(self, template_argument_constant: ast.TemplateArgumentConstant) -> None:
        template_argument_constant.accept_constant(self)

    def visit_template_argument_type_id(self, template_argument_type_id: ast.TemplateArgumentTypeId) -> None:
        template_argument_type_id.accept_type_id(self)

    def visit_ambiguous_template_parameter(self, ambiguous_template_parameter: ast.AmbiguousTemplateParameter) -> None:
        ambiguous_template_parameter.accept_first(self)

    def visit_template_parameter_type(self, template_parameter_type: ast.TemplateParameterType) -> None:
        template_parameter_type.accept_default_value(self)

    def visit_template_parameter_template(self, template_parameter_template: ast.TemplateParameterTemplate) -> None:
        template_parameter_template.accept_template_parameter_list(self)
        template_parameter_template.accept_requires_clause(self)
        template_parameter_template.accept_default_value(self)

    def visit_template_parameter_constant(self, template_parameter_constant: ast.TemplateParameterConstant) -> None:
        template_parameter_constant.accept_parameter_declaration(self)

    def visit_template_parameter_constraint(self,
                                            template_parameter_constraint: ast.TemplateParameterConstraint) -> None:
        template_parameter_constraint.accept_constraint(self)
        template_parameter_constraint.accept_default_value(self)

    def visit_attribute_named_list(self, attribute_named_list: ast.AttributeNamedList) -> None:
        attribute_named_list.accept_attributes(self)

    def visit_attribute_align_as_type(self, attribute_align_as_type: ast.AttributeAlignAsType) -> None:
        attribute_align_as_type.accept_type(self)

    def visit_attribute_align_as_expression(self,
                                            attribute_align_as_expression: ast.AttributeAlignAsExpression) -> None:
        attribute_align_as_expression.accept_expression(self)

    def visit_attribute_align_as_ambiguous(self, attribute_align_as_ambiguous: ast.AttributeAlignAsAmbiguous) -> None:
        attribute_align_as_ambiguous.accept_alignas_type(self)

    def visit_requires_expression(self, requires_expression: ast.RequiresExpression) -> None:
        requires_expression.accept_parameter_clause(self)
        requires_expression.accept_requirement_body(self)

    def visit_requirement_body(self, requirement_body: ast.RequirementBody) -> None:
        requirement_body.accept_children(self)

    def visit_ambiguous_requirement(self, ambiguous_requirement: ast.AmbiguousRequirement) -> None:
        ambiguous_requirement.accept_first(self)

    def visit_simple_requirement(self, simple_requirement: ast.SimpleRequirement) -> None:
        simple_requirement.accept_expression(self)

    def visit_type_requirement(self, type_requirement: ast.TypeRequirement) -> None:
        type_requirement.accept_type(self)

    def visit_compound_requirement(self, compound_requirement: ast.CompoundRequirement) -> None:
        compound_requirement.accept_expression(self)
        compound_requirement.accept_type_constraint(self)

    def visit_nested_requirement(self, nested_requirement: ast.NestedRequirement) -> None:
        nested_requirement.accept_expression(self)

    def visit_requires_clause(self, requires_clause: ast.RequiresClause) -> None:
        requires_clause.accept_requirement_expression(self)

    def visit_pack_expand_type(self, pack_expand_type: ast.PackExpandType) -> None:
        pack_expand_type.accept_type(self)

    def visit_pack_expand_expression(self, pack_expand_expression: ast.PackExpandExpression) -> None:
        pack_expand_expression.accept_expression(self)

    def visit_pack_expand_attribute_named(self, pack_expand_attribute_named: ast.PackExpandAttributeNamed) -> None:
        pack_expand_attribute_named.accept_attribute(self)

    def visit_statement_with_attributes(self, statement_with_attributes: ast.StatementWithAttributes) -> None:
        statement_with_attributes.accept_attributes(self)
        statement_with_attributes.accept_statement(self)

    def visit_ambiguous_statement(self, ambiguous_statement: ast.AmbiguousStatement) -> None:
        ambiguous_statement.accept_first(self)

    def visit_expression_statement(self, expression_statement: ast.ExpressionStatement) -> None:
        expression_statement.accept_expression(self)

    def visit_declaration_statement(self, declaration_statement: ast.DeclarationStatement) -> None:
        declaration_statement.accept_declaration(self)

    def visit_compound_statement(self, compound_statement: ast.CompoundStatement) -> None:
        compound_statement.accept_children(self)

    def visit_try_block(self, try_block: ast.TryBlock) -> None:
        try_block.accept_try_statement(self)
        try_block.accept_handlers(self)

    def visit_exception_handler(self, exception_handler: ast.ExceptionHandler) -> None:
        exception_handler.accept_handler_statement(self)
        exception_handler.accept_exception_declaration(self)

    def visit_exception_declaration_type_specifier(
            self, exception_declaration_type_specifier: ast.ExceptionDeclarationTypeSpecifier
    ) -> None:
        exception_declaration_type_specifier.accept_attributes(self)
        exception_declaration_type_specifier.accept_type_specifier_seq(self)
        exception_declaration_type_specifier.accept_declarator(self)

    def visit_ambiguous_exception_declaration(
            self, ambiguous_exception_declaration: ast.AmbiguousExceptionDeclaration
    ) -> None:
        ambiguous_exception_declaration.accept_first(self)

    def visit_return_statement(self, return_statement: ast.ReturnStatement) -> None:
        return_statement.accept_return_expression(self)

    def visit_co_return_statement(self, co_return_statement: ast.CoReturnStatement) -> None:
        co_return_statement.accept_return_expression(self)

    def visit_labeled_statement(self, labeled_statement: ast.LabeledStatement) -> None:
        labeled_statement.accept_attributes(self)
        labeled_statement.accept_statement(self)

    def visit_case_statement(self, case_statement: ast.CaseStatement) -> None:
        case_statement.accept_attributes(self)
        case_statement.accept_expression(self)
        case_statement.accept_statement(self)

    def visit_default_statement(self, default_statement: ast.DefaultStatement) -> None:
        default_statement.accept_attributes(self)
        default_statement.accept_statement(self)

    def visit_selection_condition(self, selection_condition: ast.SelectionCondition) -> None:
        selection_condition.accept_init_statement(self)
        selection_condition.accept_condition(self)

    def visit_ambiguous_selection_condition(self,
                                            ambiguous_selection_condition: ast.AmbiguousSelectionCondition) -> None:
        ambiguous_selection_condition.accept_first(self)

    def visit_switch_statement(self, switch_statement: ast.SwitchStatement) -> None:
        switch_statement.accept_condition(self)
        switch_statement.accept_statement(self)

    def visit_if_statement(self, if_statement: ast.IfStatement) -> None:
        if_statement.accept_condition(self)
        if_statement.accept_true_statement(self)
        if_statement.accept_false_statement(self)

    def visit_if_consteval_statement(self, if_consteval_statement: ast.IfConstevalStatement) -> None:
        if_consteval_statement.accept_true_statement(self)
        if_consteval_statement.accept_false_statement(self)

    def visit_while_statement(self, while_statement: ast.WhileStatement) -> None:
        while_statement.accept_condition(self)
        while_statement.accept_statement(self)

    def visit_do_while_statement(self, do_while_statement: ast.DoWhileStatement) -> None:
        do_while_statement.accept_statement(self)
        do_while_statement.accept_condition(self)

    def visit_for_statement(self, for_statement: ast.ForStatement) -> None:
        for_statement.accept_for_condition(self)
        for_statement.accept_statement(self)

    def visit_ambiguous_for_condition(self, ambiguous_for_condition: ast.AmbiguousForCondition) -> None:
        ambiguous_for_condition.accept_first(self)

    def visit_for_condition_init(self, for_condition_init: ast.ForConditionInit) -> None:
        for_condition_init.accept_init_statement(self)
        for_condition_init.accept_condition(self)
        for_condition_init.accept_update(self)

    def visit_for_condition_range(self, for_condition_range: ast.ForConditionRange) -> None:
        for_condition_range.accept_init_statement(self)
        for_condition_range.accept_declaration(self)

    def visit_dynamic_exception_specifier(self, dynamic_exception_specifier: ast.DynamicExceptionSpecifier) -> None:
        dynamic_exception_specifier.accept_type_id_list(self)

    def visit_ambiguous_exception_specifier(self,
                                            ambiguous_exception_specifier: ast.AmbiguousExceptionSpecifier) -> None:
        ambiguous_exception_specifier.accept_first(self)

    def visit_noexcept_specifier(self, noexcept_specifier: ast.NoExceptSpecifier) -> None:
        noexcept_specifier.accept_value(self)

    def visit_elaborated_class_type_specifier(
            self, elaborated_class_type_specifier: ast.ElaboratedClassTypeSpecifier
    ) -> None:
        elaborated_class_type_specifier.accept_attributes(self)
        elaborated_class_type_specifier.accept_name(self)

    def visit_elaborated_enum_type_specifier(
            self, elaborated_enum_type_specifier: ast.ElaboratedEnumTypeSpecifier
    ) -> None:
        elaborated_enum_type_specifier.accept_attributes(self)
        elaborated_enum_type_specifier.accept_name(self)

    def visit_decltype_type_specifier(self, decltype_type_specifier: ast.DecltypeTypeSpecifier) -> None:
        decltype_type_specifier.accept_expression(self)

    def visit_constrained_type_specifier(self, constrained_type_specifier: ast.ConstrainedTypeSpecifier) -> None:
        constrained_type_specifier.accept_constraint(self)
        constrained_type_specifier.accept_placeholder_type_specifier(self)

    def visit_type_specifier_reference(self, type_specifier_reference: ast.TypeSpecifierReference) -> None:
        type_specifier_reference.accept_reference(self)

    def visit_ambiguous_type_specifier(self, ambiguous_type_specifier: ast.AmbiguousTypeSpecifier) -> None:
        ambiguous_type_specifier.accept_first(self)

    def visit_defining_type_specifier_seq(self, defining_type_specifier_seq: ast.DefiningTypeSpecifierSeq) -> None:
        defining_type_specifier_seq.accept_attributes(self)
        defining_type_specifier_seq.accept_types(self)
        defining_type_specifier_seq.accept_qualifiers(self)

    def visit_declarator_element_id(self, declarator_element_id: ast.DeclaratorElementId) -> None:
        declarator_element_id.accept_name(self)
        declarator_element_id.accept_attributes(self)

    def visit_declarator_element_pack_id(self, declarator_element_pack_id: ast.DeclaratorElementPackId) -> None:
        declarator_element_pack_id.accept_name(self)
        declarator_element_pack_id.accept_attributes(self)

    def visit_declarator_element_group(self, declarator_element_group: ast.DeclaratorElementGroup) -> None:
        declarator_element_group.accept_next(self)

    def visit_declarator_element_pointer(self, declarator_element_pointer: ast.DeclaratorElementPointer) -> None:
        declarator_element_pointer.accept_next(self)
        declarator_element_pointer.accept_attributes(self)
        declarator_element_pointer.accept_qualifiers(self)

    def visit_declarator_element_reference(self, declarator_element_reference: ast.DeclaratorElementReference) -> None:
        declarator_element_reference.accept_next(self)
        declarator_element_reference.accept_attributes(self)

    def visit_declarator_element_rvalue_reference(
            self, declarator_element_rvalue_reference: ast.DeclaratorElementRValueReference
    ) -> None:
        declarator_element_rvalue_reference.accept_next(self)
        declarator_element_rvalue_reference.accept_attributes(self)

    def visit_declarator_element_array(self, declarator_element_array: ast.DeclaratorElementArray) -> None:
        declarator_element_array.accept_next(self)
        declarator_element_array.accept_attributes(self)
        declarator_element_array.accept_size(self)

    def visit_declarator_element_method(self, declarator_element_method: ast.DeclaratorElementMethod) -> None:
        declarator_element_method.accept_next(self)
        declarator_element_method.accept_parameter_clause(self)
        declarator_element_method.accept_cv_qualifiers(self)
        declarator_element_method.accept_ref_qualifier(self)
        declarator_element_method.accept_exception_specifier(self)
        declarator_element_method.accept_attributes(self)
        declarator_element_method.accept_trailing_return_type(self)

    def visit_abstract_declarator_list(self, abstract_declarator_list: ast.AbstractDeclaratorList) -> None:
        abstract_declarator_list.accept_element(self)

    def visit_declarator_list(self, declarator_list: ast.DeclaratorList) -> None:
        declarator_list.accept_element(self)

    def visit_ambiguous_abstract_declarator(self,
                                            ambiguous_abstract_declarator: ast.AmbiguousAbstractDeclarator) -> None:
        ambiguous_abstract_declarator.accept_first(self)

    def visit_type_id_declarator(self, type_id_declarator: ast.TypeIdDeclarator) -> None:
        type_id_declarator.accept_type_specifier_seq(self)
        type_id_declarator.accept_declarator(self)

    def visit_ambiguous_type_id(self, ambiguous_type_id: ast.AmbiguousTypeId) -> None:
        ambiguous_type_id.accept_first(self)

    def visit_type_id_pack(self, type_id_pack: ast.TypeIdPack) -> None:
        type_id_pack.accept_type_pack(self)

    def visit_initializer_list(self, initializer_list: ast.InitializerList) -> None:
        initializer_list.accept_expressions(self)

    def visit_ambiguous_initializer_list(self, ambiguous_initializer_list: ast.AmbiguousInitializerList) -> None:
        ambiguous_initializer_list.accept_first(self)

    def visit_id_expression(self, id_expression: ast.IdExpression) -> None:
        id_expression.accept_reference(self)

    def visit_ambiguous_expression(self, ambiguous_expression: ast.AmbiguousExpression) -> None:
        ambiguous_expression.accept_first(self)

    def visit_unary_expression(self, unary_expression: ast.UnaryExpression) -> None:
        unary_expression.accept_operand(self)

    def visit_binary_expression(self, binary_expression: ast.BinaryExpression) -> None:
        binary_expression.accept_left_operand(self)
        binary_expression.accept_right_operand(self)

    def visit_postfix_expression(self, postfix_expression: ast.PostfixExpression) -> None:
        postfix_expression.accept_operand(self)

    def visit_sizeof_expression(self, sizeof_expression: ast.SizeofExpression) -> None:
        sizeof_expression.accept_operand(self)

    def visit_sizeof_type_expression(self, sizeof_type_expression: ast.SizeofTypeExpression) -> None:
        sizeof_type_expression.accept_type(self)

    def visit_alignof_expression(self, alignof_expression: ast.AlignofExpression) -> None:
        alignof_expression.accept_type(self)

    def visit_noexcept_expression(self, noexcept_expression: ast.NoexceptExpression) -> None:
        noexcept_expression.accept_operand(self)

    def visit_call_expression(self, call_expression: ast.CallExpression) -> None:
        call_expression.accept_method(self)
        call_expression.accept_arguments(self)

    def visit_subscript_expression(self, subscript_expression: ast.SubscriptExpression) -> None:
        subscript_expression.accept_operand(self)
        subscript_expression.accept_subscript(self)

    def visit_cast_expression(self, cast_expression: ast.CastExpression) -> None:
        cast_expression.accept_target_type(self)
        cast_expression.accept_operand(self)

    def visit_cxx_cast_expression(self, cxx_cast_expression: ast.CxxCastExpression) -> None:
        cxx_cast_expression.accept_target_type(self)
        cxx_cast_expression.accept_operand(self)

    def visit_conditional_expression(self, conditional_expression: ast.ConditionalExpression) -> None:
        conditional_expression.accept_condition(self)
        conditional_expression.accept_expression_true(self)
        conditional_expression.accept_expression_false(self)

    def visit_member_access_expression(self, member_access_expression: ast.MemberAccessExpression) -> None:
        member_access_expression.accept_expression(self)
        member_access_expression.accept_member_expression(self)

    def visit_member_access_ptr_expression(self, member_access_ptr_expression: ast.MemberAccessPtrExpression) -> None:
        member_access_ptr_expression.accept_expression(self)
        member_access_ptr_expression.accept_member_expression(self)

    def visit_member_ptr_expression(self, member_ptr_expression: ast.MemberPtrExpression) -> None:
        member_ptr_expression.accept_expression(self)
        member_ptr_expression.accept_member_expression(self)

    def visit_type_id_expression(self, type_id_expression: ast.TypeIdExpression) -> None:
        type_id_expression.accept_operand(self)

    def visit_type_id_expression_type(self, type_id_expression_type: ast.TypeIdExpressionType) -> None:
        type_id_expression_type.accept_type(self)

    def visit_simple_cast_expression(self, simple_cast_expression: ast.SimpleCastExpression) -> None:
        simple_cast_expression.accept_type(self)
        simple_cast_expression.accept_expression(self)

    def visit_new_expression(self, new_expression: ast.NewExpression) -> None:
        new_expression.accept_placement(self)
        new_expression.accept_initializer(self)
        new_expression.accept_type(self)

    def visit_delete_expression(self, delete_expression: ast.DeleteExpression) -> None:
        delete_expression.accept_operand(self)

    def visit_throw_expression(self, throw_expression: ast.ThrowExpression) -> None:
        throw_expression.accept_operand(self)

    def visit_yield_expression(self, yield_expression: ast.YieldExpression) -> None:
        yield_expression.accept_operand(self)

    def visit_await_expression(self, await_expression: ast.AwaitExpression) -> None:
        await_expression.accept_operand(self)

    def visit_fold_expression_left(self, fold_expression_left: ast.FoldExpressionLeft) -> None:
        fold_expression_left.accept_expression(self)

    def visit_fold_expression_right(self, fold_expression_right: ast.FoldExpressionRight) -> None:
        fold_expression_right.accept_expression(self)

    def visit_fold_expression_both(self, fold_expression_both: ast.FoldExpressionBoth) -> None:
        fold_expression_both.accept_expression_left(self)
        fold_expression_both.accept_expression_right(self)

    def visit_parenthesized_expression(self, parenthesized_expression: ast.ParenthesizedExpression) -> None:
        parenthesized_expression.accept_expression(self)

    def visit_braced_init_list(self, braced_init_list: ast.BracedInitList) -> None:
        braced_init_list.accept_initializers(self)

    def visit_ambiguous_braced_init_list(self, ambiguous_braced_init_list: ast.AmbiguousBracedInitList) -> None:
        ambiguous_braced_init_list.accept_first(self)

    def visit_designated_braced_init_list(self, designated_braced_init_list: ast.DesignatedBracedInitList) -> None:
        designated_braced_init_list.accept_initializers(self)

    def visit_designated_initializer(self, designated_initializer: ast.DesignatedInitializer) -> None:
        designated_initializer.accept_value(self)

    def visit_string_list(self, string_list: ast.StringList) -> None:
        string_list.accept_strings(self)

    def visit_lambda_expression(self, lambda_expression: ast.LambdaExpression) -> None:
        lambda_expression.accept_capture(self)
        lambda_expression.accept_attributes(self)
        lambda_expression.accept_declarator(self)
        lambda_expression.accept_compound_statement(self)

    def visit_template_lambda_expression(self, template_lambda_expression: ast.TemplateLambdaExpression) -> None:
        template_lambda_expression.accept_capture(self)
        template_lambda_expression.accept_template_parameter_list(self)
        template_lambda_expression.accept_constraint(self)
        template_lambda_expression.accept_attributes(self)
        template_lambda_expression.accept_declarator(self)
        template_lambda_expression.accept_compound_statement(self)

    def visit_lambda_capture_list(self, lambda_capture_list: ast.LambdaCaptureList) -> None:
        lambda_capture_list.accept_capture_list(self)

    def visit_simple_capture(self, simple_capture: ast.SimpleCapture) -> None:
        simple_capture.accept_initializer(self)

    def visit_lambda_declarator(self, lambda_declarator: ast.LambdaDeclarator) -> None:
        lambda_declarator.accept_parameter_list(self)
        lambda_declarator.accept_lambda_specifier_seq(self)
        lambda_declarator.accept_noexceot_specification(self)
        lambda_declarator.accept_attribute_list(self)
        lambda_declarator.accept_trailing_return_type(self)
        lambda_declarator.accept_requires_clause(self)

    def visit_reference(self, reference: ast.Reference) -> None:
        reference.accept_names(self)

    def visit_typename_reference(self, typename_reference: ast.TypenameReference) -> None:
        typename_reference.accept_reference(self)

    def visit_pack_expand_reference(self, pack_expand_reference: ast.PackExpandReference) -> None:
        pack_expand_reference.accept_reference(self)

    def visit_template_specifier_id(self, template_specifier_id: ast.TemplateSpecifierId) -> None:
        template_specifier_id.accept_id(self)

    def visit_template_id(self, template_id: ast.TemplateId) -> None:
        template_id.accept_id(self)
        template_id.accept_template_arguments(self)

    def visit_decltype_specifier_id(self, decltype_specifier_id: ast.DecltypeSpecifierId) -> None:
        decltype_specifier_id.accept_decltype_specifier(self)

    def visit_template_argument_list(self, template_argument_list: ast.TemplateArgumentList) -> None:
        template_argument_list.accept_arguments(self)

    def visit_ambiguous_template_argument_list(
            self, ambiguous_template_argument_list: ast.AmbiguousTemplateArgumentList
    ) -> None:
        ambiguous_template_argument_list.accept_first(self)

    def visit_conversion_operator_id(self, conversion_operator_id: ast.ConversionOperatorId) -> None:
        conversion_operator_id.accept_conversion_type(self)
