from .. import ast


class StringRef(ast.Visitor):

    def __init__(self) -> None:
        self.result = ''

    def visit_reference(self, reference: ast.Reference) -> None:
        for name in reference.name_list[:-1]:
            name.accept(self)
            self.result += '::'
        reference.name_list[-1].accept(self)

    def visit_typename_reference(self, typename_reference: ast.TypenameReference) -> None:
        self.result += 'typename '
        typename_reference.accept_reference(self)

    def visit_pack_expand_reference(self, pack_expand_reference: ast.PackExpandReference) -> None:
        pack_expand_reference.accept_reference(self)
        self.result += '...'

    def visit_root_id(self, root_id: ast.RootId) -> None:
        pass

    def visit_template_specifier_id(self, template_specifier_id: ast.TemplateSpecifierId) -> None:
        self.result += 'template '
        template_specifier_id.accept_id(self)

    def visit_id(self, identifier: ast.Id) -> None:
        self.result += identifier.name

    def visit_template_id(self, template_id: ast.TemplateId) -> None:
        template_id.accept_id(self)
        self.result += '<'
        template_id.accept_template_arguments(self)
        self.result += '>'

    def visit_decltype_specifier_id(self, decltype_specifier_id: ast.DecltypeSpecifierId) -> None:
        decltype_specifier_id.accept_decltype_specifier(self)

    def visit_template_argument_list(self, template_argument_list: ast.TemplateArgumentList) -> None:
        for argument in template_argument_list.template_arguments[:-1]:
            argument.accept(self)
            self.result += ', '
        template_argument_list.template_arguments[-1].accept(self)

    def visit_ambiguous_template_argument_list(
            self, ambiguous_template_argument_list: ast.AmbiguousTemplateArgumentList
    ) -> None:
        ambiguous_template_argument_list.accept_first(self)

    def visit_destructor_id(self, destructor_id: ast.DestructorId) -> None:
        self.result += '~'
        destructor_id.accept_id(self)

    def visit_operator_id(self, operator_id: ast.OperatorId) -> None:
        self.result += 'operator %s' % operator_id.operator

    def visit_conversion_operator_id(self, conversion_operator_id: ast.ConversionOperatorId) -> None:
        self.result += 'operator '
        conversion_operator_id.accept_conversion_type(self)

    def visit_literal_operator_id(self, literal_operator_id: ast.LiteralOperatorId) -> None:
        self.result += 'operator "" %s' % literal_operator_id.literal_operator

    def visit_template_argument_pack_expand(
            self, template_argument_pack_expand: ast.TemplateArgumentPackExpand
    ) -> None:
        template_argument_pack_expand.accept_argument(self)
        self.result += '...'

    def visit_ambiguous_template_argument(self, ambiguous_template_argument: ast.AmbiguousTemplateArgument) -> None:
        ambiguous_template_argument.accept_first(self)

    def visit_template_argument_constant(self, template_argument_constant: ast.TemplateArgumentConstant) -> None:
        template_argument_constant.accept_constant(self)

    def visit_template_argument_type_id(self, template_argument_type_id: ast.TemplateArgumentTypeId) -> None:
        template_argument_type_id.accept_type_id(self)

    def visit_type_id_declarator(self, type_id_declarator: ast.TypeIdDeclarator) -> None:
        type_id_declarator.accept_type_specifier_seq(self)
        type_id_declarator.accept_declarator(self)

    def visit_ambiguous_type_id(self, ambiguous_type_id: ast.AmbiguousTypeId) -> None:
        ambiguous_type_id.accept_first(self)

    def visit_type_id_pack(self, type_id_pack: ast.TypeIdPack) -> None:
        type_id_pack.accept_type_pack(self)
        self.result += '...'

    def visit_type_specifier_seq(self, type_specifier_seq: ast.TypeSpecifierSeq) -> None:
        all_specifiers = type_specifier_seq.types + type_specifier_seq.qualifiers
        if all_specifiers:
            for type_specifier in all_specifiers[:-1]:
                type_specifier.accept(self)
                self.result += ' '
            all_specifiers[-1].accept(self)

    def visit_cv_qualifier(self, cv_qualifier: ast.CvQualifier) -> None:
        self.result += cv_qualifier.qualifier

    def visit_primitive_type_specifier(self, primitive_type_specifier: ast.PrimitiveTypeSpecifier) -> None:
        self.result += primitive_type_specifier.typename

    def visit_enum_specifier(self, enum_specifier: ast.EnumSpecifier) -> None:
        enum_specifier.accept_name(self)

    def visit_class_specifier(self, class_specifier: ast.ClassSpecifier) -> None:
        assert False

    def visit_elaborated_class_type_specifier(
            self, elaborated_class_type_specifier: ast.ElaboratedClassTypeSpecifier
    ) -> None:
        elaborated_class_type_specifier.accept_name(self)

    def visit_elaborated_enum_type_specifier(
            self, elaborated_enum_type_specifier: ast.ElaboratedEnumTypeSpecifier
    ) -> None:
        elaborated_enum_type_specifier.accept_name(self)

    def visit_auto_type_specifier(self, auto_type_specifier: ast.AutoTypeSpecifier) -> None:
        self.result += 'auto'

    def visit_decltype_type_specifier(self, decltype_type_specifier: ast.DecltypeTypeSpecifier) -> None:
        self.result += '%s(' % decltype_type_specifier.decltype_kw
        decltype_type_specifier.accept_expression(self)
        self.result += ')'

    def visit_decltype_auto_type_specifier(self, decltype_auto_type_specifier: ast.DecltypeAutoTypeSpecifier) -> None:
        self.result += '%s(auto)' % decltype_auto_type_specifier.decltype_kw

    def visit_type_specifier_reference(self, type_specifier_reference: ast.TypeSpecifierReference) -> None:
        type_specifier_reference.accept_reference(self)

    def visit_ambiguous_type_specifier(self, ambiguous_type_specifier: ast.AmbiguousTypeSpecifier) -> None:
        ambiguous_type_specifier.accept_first(self)

    def visit_constrained_type_specifier(self, constrained_type_specifier: ast.ConstrainedTypeSpecifier) -> None:
        constrained_type_specifier.accept_constraint(self)
        self.result += ' '
        constrained_type_specifier.accept_placeholder_type_specifier(self)

    def visit_initializer_list(self, initializer_list: ast.InitializerList) -> None:
        if initializer_list.expressions:
            for expression in initializer_list.expressions[:-1]:
                expression.accept(self)
                self.result += ', '
            initializer_list.expressions[-1].accept(self)

    def visit_ambiguous_initializer_list(self, ambiguous_initializer_list: ast.AmbiguousInitializerList) -> None:
        ambiguous_initializer_list.accept_first(self)

    def visit_id_expression(self, id_expression: ast.IdExpression) -> None:
        id_expression.accept_reference(self)

    def visit_ambiguous_expression(self, ambiguous_expression: ast.AmbiguousExpression) -> None:
        ambiguous_expression.accept_first(self)

    def visit_unary_expression(self, unary_expression: ast.UnaryExpression) -> None:
        self.result += unary_expression.operator
        unary_expression.accept_operand(self)

    def visit_binary_expression(self, binary_expression: ast.BinaryExpression) -> None:
        binary_expression.accept_left_operand(self)
        self.result += ' ' + binary_expression.operator + ' '
        binary_expression.accept_right_operand(self)

    def visit_postfix_expression(self, postfix_expression: ast.PostfixExpression) -> None:
        postfix_expression.accept_operand(self)
        self.result += postfix_expression.operator

    def visit_sizeof_expression(self, sizeof_expression: ast.SizeofExpression) -> None:
        self.result += 'sizeof('
        sizeof_expression.accept_operand(self)
        self.result += ')'

    def visit_sizeof_type_expression(self, sizeof_type_expression: ast.SizeofTypeExpression) -> None:
        self.result += 'sizeof('
        sizeof_type_expression.accept_type(self)
        self.result += ')'

    def visit_sizeof_pack_expression(self, sizeof_pack_expression: ast.SizeofPackExpression) -> None:
        self.result += 'sizeof(%s...)' % sizeof_pack_expression.identifier

    def visit_alignof_expression(self, alignof_expression: ast.AlignofExpression) -> None:
        self.result += '%s(' % alignof_expression.alignof_token
        alignof_expression.accept_type(self)
        self.result += ')'

    def visit_noexcept_expression(self, noexcept_expression: ast.NoexceptExpression) -> None:
        self.result += 'noexcept('
        noexcept_expression.accept_operand(self)
        self.result += ')'

    def visit_call_expression(self, call_expression: ast.CallExpression) -> None:
        call_expression.accept_method(self)
        call_expression.accept_arguments(self)

    def visit_subscript_expression(self, subscript_expression: ast.SubscriptExpression) -> None:
        subscript_expression.accept_operand(self)
        self.result += '['
        subscript_expression.accept_subscript(self)
        self.result += ']'

    def visit_cast_expression(self, cast_expression: ast.CastExpression) -> None:
        self.result += '('
        cast_expression.accept_target_type(self)
        self.result += ')'
        cast_expression.accept_operand(self)

    def visit_cxx_cast_expression(self, cxx_cast_expression: ast.CxxCastExpression) -> None:
        self.result += '%s<' % cxx_cast_expression.cast_type
        cxx_cast_expression.accept_target_type(self)
        self.result += '>('
        cxx_cast_expression.accept_operand(self)
        self.result += ')'

    def visit_conditional_expression(self, conditional_expression: ast.ConditionalExpression) -> None:
        conditional_expression.accept_condition(self)
        self.result += ' ? '
        conditional_expression.accept_expression_true(self)
        self.result += ' : '
        conditional_expression.accept_expression_false(self)

    def visit_member_access_expression(self, member_access_expression: ast.MemberAccessExpression) -> None:
        member_access_expression.accept_expression(self)
        self.result += '.'
        member_access_expression.accept_member_expression(self)

    def visit_member_access_ptr_expression(self, member_access_ptr_expression: ast.MemberAccessPtrExpression) -> None:
        member_access_ptr_expression.accept_expression(self)
        self.result += '->'
        member_access_ptr_expression.accept_member_expression(self)

    def visit_member_ptr_expression(self, member_ptr_expression: ast.MemberPtrExpression) -> None:
        member_ptr_expression.accept_expression(self)
        self.result += member_ptr_expression.access_type
        member_ptr_expression.accept_member_expression(self)

    def visit_type_id_expression(self, type_id_expression: ast.TypeIdExpression) -> None:
        self.result += 'typeid('
        type_id_expression.accept_operand(self)
        self.result += ')'

    def visit_type_id_expression_type(self, type_id_expression_type: ast.TypeIdExpressionType) -> None:
        self.result += 'typeid('
        type_id_expression_type.accept_type(self)
        self.result += ')'

    def visit_simple_cast_expression(self, simple_cast_expression: ast.SimpleCastExpression) -> None:
        simple_cast_expression.accept_type(self)
        self.result += '('
        simple_cast_expression.accept_expression(self)
        self.result += ')'

    def visit_new_expression(self, new_expression: ast.NewExpression) -> None:
        if new_expression.root:
            self.result += '::new'
        else:
            self.result += 'new'
        if new_expression.placement is not None:
            new_expression.accept_placement(self)
        if new_expression.full_type:
            self.result += ' ('
            new_expression.accept_type(self)
            self.result += ')'
        else:
            self.result += ' '
            new_expression.accept_type(self)
        if new_expression.initializer is not None:
            self.result += ' '
            new_expression.accept_initializer(self)

    def visit_delete_expression(self, delete_expression: ast.DeleteExpression) -> None:
        if delete_expression.root:
            if delete_expression.array:
                self.result += '::delete[] '
            else:
                self.result += '::delete '
        else:
            if delete_expression.array:
                self.result += 'delete[] '
            else:
                self.result += 'delete '
        delete_expression.accept_operand(self)

    def visit_throw_expression(self, throw_expression: ast.ThrowExpression) -> None:
        if throw_expression.operand is not None:
            self.result += 'throw '
            throw_expression.accept_operand(self)
        else:
            self.result += 'throw'

    def visit_yield_expression(self, yield_expression: ast.YieldExpression) -> None:
        self.result += 'co_yield '
        yield_expression.accept_operand(self)

    def visit_await_expression(self, await_expression: ast.AwaitExpression) -> None:
        self.result += 'co_await '
        await_expression.accept_operand(self)

    def visit_fold_expression_left(self, fold_expression_left: ast.FoldExpressionLeft) -> None:
        self.result += '('
        fold_expression_left.accept_expression(self)
        self.result += ' %s ...)' % fold_expression_left.operator

    def visit_fold_expression_right(self, fold_expression_right: ast.FoldExpressionRight) -> None:
        self.result += '(... %s ' % fold_expression_right.operator
        fold_expression_right.accept_expression(self)
        self.result += ')'

    def visit_fold_expression_both(self, fold_expression_both: ast.FoldExpressionBoth) -> None:
        self.result += '('
        fold_expression_both.accept_expression_left(self)
        self.result += ' %s ... %s ' % (fold_expression_both.operator_left, fold_expression_both.operator_right)
        fold_expression_both.accept_expression_right(self)
        self.result += ')'

    def visit_parenthesized_expression(self, parenthesized_expression: ast.ParenthesizedExpression) -> None:
        self.result += '('
        parenthesized_expression.accept_expression(self)
        self.result += ')'

    def visit_this_expression(self, this_expression: ast.ThisExpression) -> None:
        self.result += 'this'

    def visit_nullptr_expression(self, nullptr_expression: ast.NullPtrExpression) -> None:
        self.result += 'nullptr'

    def visit_type_trait_expression(self, type_trait_expression: ast.TypeTraitExpression) -> None:
        self.result += '%s' % type_trait_expression.type_trait
        if type_trait_expression.arguments is not None:
            self.result += '('
            for argument in type_trait_expression.arguments:
                if argument.skipped_tokens:
                    self.result += ' '
                self.result += argument.text()
            self.result += ')'

    def visit_pack_expand_expression(self, pack_expand_expression: ast.PackExpandExpression) -> None:
        pack_expand_expression.accept(self)
        self.result += '...'

    def visit_braced_init_list(self, braced_init_list: ast.BracedInitList) -> None:
        self.result += '{'
        if braced_init_list.initializer_list:
            for initializer in braced_init_list.initializer_list[:-1]:
                initializer.accept(self)
                self.result += ', '
            braced_init_list.initializer_list[-1].accept(self)
        self.result += '}'

    def visit_ambiguous_braced_init_list(self, ambiguous_braced_init_list: ast.AmbiguousBracedInitList) -> None:
        ambiguous_braced_init_list.accept_first(self)

    def visit_boolean_literal(self, boolean_literal: ast.BooleanLiteral) -> None:
        if boolean_literal.boolean_value:
            self.result += 'true'
        else:
            self.result += 'false'

    def visit_integer_literal(self, integer_literal: ast.IntegerLiteral) -> None:
        self.result += integer_literal.integer_value

    def visit_user_defined_integer_literal(self, user_defined_integer_literal: ast.UserDefinedIntegerLiteral) -> None:
        self.result += user_defined_integer_literal.integer_value + user_defined_integer_literal.literal_type

    def visit_character_literal(self, character_literal: ast.CharacterLiteral) -> None:
        self.result += "'%s'" % character_literal.character_value

    def visit_user_defined_character_literal(
            self, user_defined_character_literal: ast.UserDefinedCharacterLiteral
    ) -> None:
        self.result += "'%s'%s" % (
            user_defined_character_literal.character_value, user_defined_character_literal.literal_type
        )

    def visit_floating_literal(self, floating_literal: ast.FloatingLiteral) -> None:
        self.result += floating_literal.floating_value

    def visit_user_defined_floating_literal(
            self, user_defined_floating_literal: ast.UserDefinedFloatingLiteral
    ) -> None:
        self.result += user_defined_floating_literal.floating_value + user_defined_floating_literal.literal_type

    def visit_string_literal(self, string_literal: ast.StringLiteral) -> None:
        self.result += '"%s"' % string_literal.string_value

    def visit_user_defined_string_literal(self, user_defined_string_literal: ast.UserDefinedStringLiteral) -> None:
        self.result += '"%s"%s' % (user_defined_string_literal.string_value, user_defined_string_literal.literal_type)

    def visit_string_literal_macro(self, string_literal_macro: ast.StringLiteralMacro) -> None:
        self.result += string_literal_macro.string_value
        if string_literal_macro.macro_parameters is not None:
            self.result += '('
            for argument in string_literal_macro.macro_parameters:
                if argument.skipped_tokens:
                    self.result += ' '
                self.result += argument.text()
            self.result += ')'

    def visit_string_list(self, string_list: ast.StringList) -> None:
        string_list.accept_strings(self)

    def visit_declarator_list(self, declarator_list: ast.DeclaratorList) -> None:
        self.result += ' '
        declarator_list.accept_element(self)

    def visit_abstract_declarator_list(self, abstract_declarator_list: ast.AbstractDeclaratorList) -> None:
        self.result += ' '
        abstract_declarator_list.accept_element(self)

    def visit_declarator_element_id(self, declarator_element_id: ast.DeclaratorElementId) -> None:
        declarator_element_id.accept_name(self)

    def visit_declarator_element_pack_id(self, declarator_element_pack_id: ast.DeclaratorElementPackId) -> None:
        self.result += '...'
        declarator_element_pack_id.accept_name(self)

    def visit_declarator_element_abstract(self, declarator_element_abstract: ast.DeclaratorElementAbstract) -> None:
        pass

    def visit_declarator_element_abstract_pack(
            self, declarator_element_abstract_pack: ast.DeclaratorElementAbstractPack
    ) -> None:
        self.result += '...'

    def visit_declarator_element_group(self, declarator_element_group: ast.DeclaratorElementGroup) -> None:
        self.result += '('
        declarator_element_group.accept_next(self)
        self.result += ')'

    def visit_declarator_element_pointer(self, declarator_element_pointer: ast.DeclaratorElementPointer) -> None:
        if declarator_element_pointer.qualified is not None:
            for is_template, identifier in declarator_element_pointer.qualified:
                if is_template:
                    self.result += 'template '
                identifier.accept(self)
                self.result += '::'
        self.result += '*'
        if declarator_element_pointer.qualifiers is not None:
            for qualifier in declarator_element_pointer.qualifiers:
                qualifier.accept(self)
                self.result += ' '
        declarator_element_pointer.accept_next(self)

    def visit_declarator_element_reference(self, declarator_element_reference: ast.DeclaratorElementReference) -> None:
        self.result += '&'
        declarator_element_reference.accept_next(self)

    def visit_declarator_element_rvalue_reference(
            self, declarator_element_rvalue_reference: ast.DeclaratorElementRValueReference
    ) -> None:
        self.result += '&&'
        declarator_element_rvalue_reference.accept_next(self)

    def visit_declarator_element_array(self, declarator_element_array: ast.DeclaratorElementArray) -> None:
        declarator_element_array.accept_next(self)
        self.result += '['
        declarator_element_array.accept_size(self)
        self.result += ']'

    def visit_declarator_element_method(self, declarator_element_method: ast.DeclaratorElementMethod) -> None:
        declarator_element_method.accept_next(self)
        declarator_element_method.accept_parameter_clause(self)
        for cv_qualifier in declarator_element_method.cv_qualifiers:
            self.result += ' '
            cv_qualifier.accept(self)
        declarator_element_method.accept_ref_qualifier(self)
        declarator_element_method.accept_exception_specifier(self)
        if declarator_element_method.trailing_return_type is not None:
            self.result += ' -> '
            declarator_element_method.accept_trailing_return_type(self)

    def visit_ambiguous_parameter_clause(self, ambiguous_parameter_clause: ast.AmbiguousParameterClause) -> None:
        ambiguous_parameter_clause.accept_first(self)

    def visit_simple_parameter_clause(self, simple_parameter_clause: ast.SimpleParameterClause) -> None:
        self.result += '('
        if simple_parameter_clause.parameter_list:
            if simple_parameter_clause.variadic:
                for parameter in simple_parameter_clause.parameter_list:
                    parameter.accept(self)
                    self.result += ', '
                self.result += '...'
            else:
                for parameter in simple_parameter_clause.parameter_list[:-1]:
                    parameter.accept(self)
                    self.result += ', '
                simple_parameter_clause.parameter_list[-1].accept(self)
        else:
            if simple_parameter_clause.variadic:
                self.result += '...'
        self.result += ')'

    def visit_parameter_declaration(self, parameter_declaration: ast.ParameterDeclaration) -> None:
        if parameter_declaration.this_specifier:
            self.result += 'this '
        parameter_declaration.accept_decl_specifier_seq(self)
        parameter_declaration.accept_declarator(self)
        if parameter_declaration.default_value is not None:
            self.result += ' = '
            parameter_declaration.accept_default_value(self)

    def visit_ref_qualifier(self, ref_qualifier: ast.RefQualifier) -> None:
        self.result += ' %s' % ref_qualifier.qualifier

    def visit_ambiguous_exception_specifier(
            self, ambiguous_exception_specifier: ast.AmbiguousExceptionSpecifier
    ) -> None:
        ambiguous_exception_specifier.accept_first(self)

    def visit_dynamic_exception_specifier(self, dynamic_exception_specifier: ast.DynamicExceptionSpecifier) -> None:
        self.result += ' throw('
        if dynamic_exception_specifier.type_list:
            for type_id in dynamic_exception_specifier.type_list[:-1]:
                type_id.accept(self)
                self.result += ', '
            dynamic_exception_specifier.type_list[-1].accept(self)
        self.result += ')'

    def visit_decl_specifier_seq(self, decl_specifier_seq: ast.DeclSpecifierSeq) -> None:
        specifiers = (decl_specifier_seq.decl_specifiers + decl_specifier_seq.type_specifier_seq.types
                      + decl_specifier_seq.type_specifier_seq.qualifiers)
        for s in specifiers[:-1]:
            s.accept(self)
            self.result += ' '
        specifiers[-1].accept(self)

    def visit_declaration_specifier(self, declaration_specifier: ast.DeclarationSpecifier) -> None:
        self.result += declaration_specifier.decl_specifier

    def visit_declaration_specifier_macro(self, declaration_specifier_macro: ast.DeclarationSpecifierMacro) -> None:
        self.result += declaration_specifier_macro.decl_specifier
        if declaration_specifier_macro.values is not None:
            self.result += '('
            for argument in declaration_specifier_macro.values:
                if argument.skipped_tokens:
                    self.result += ' '
                self.result += argument.text()
            self.result += ')'

    def visit_ambiguous_declaration(self, ambiguous_declaration: ast.AmbiguousDeclaration) -> None:
        ambiguous_declaration.accept_first(self)

    def visit_template_parameter_list(self, template_parameter_list: ast.TemplateParameterList) -> None:
        self.result += '<'
        if template_parameter_list.parameters:
            for parameter in template_parameter_list.parameters[:-1]:
                parameter.accept(self)
                self.result += ', '
            template_parameter_list.parameters[-1].accept(self)
        self.result += '>'

    def visit_ambiguous_template_parameter_list(self,
                                                ambiguous_template_parameter_list: ast.AmbiguousTemplateParameterList) -> None:
        ambiguous_template_parameter_list.accept_first(self)

    def visit_ambiguous_template_parameter(self, ambiguous_template_parameter: ast.AmbiguousTemplateParameter) -> None:
        ambiguous_template_parameter.accept_first(self)

    def visit_template_parameter_type(self, template_parameter_type: ast.TemplateParameterType) -> None:
        self.result += template_parameter_type.keyword
        if template_parameter_type.name is not None:
            self.result += ' '
            self.result += template_parameter_type.name
        if template_parameter_type.default_value is not None:
            self.result += ' = '
            template_parameter_type.accept_default_value(self)
        if template_parameter_type.is_pack:
            self.result += '...'

    def visit_template_parameter_template(self, template_parameter_template: ast.TemplateParameterTemplate) -> None:
        self.result += 'template<'
        if template_parameter_template.template_parameter_list is not None:
            template_parameter_template.template_parameter_list.accept(self)
        self.result += '> '
        if template_parameter_template.requires_clause is not None:
            template_parameter_template.requires_clause.accept(self)
            self.result += ' '
        self.result += template_parameter_template.keyword
        if template_parameter_template.name is not None:
            self.result += ' '
            self.result += template_parameter_template.name
        if template_parameter_template.default_value is not None:
            self.result += '= '
            template_parameter_template.accept_default_value(self)
        if template_parameter_template.is_pack:
            self.result += '...'

    def visit_template_parameter_constant(self, template_parameter_constant: ast.TemplateParameterConstant) -> None:
        template_parameter_constant.accept_parameter_declaration(self)

    def visit_template_parameter_constraint(self,
                                            template_parameter_constraint: ast.TemplateParameterConstraint) -> None:
        template_parameter_constraint.accept_constraint(self)
        if template_parameter_constraint.name is not None:
            self.result += template_parameter_constraint.name
        if template_parameter_constraint.default_value is not None:
            self.result += ' = '
            template_parameter_constraint.accept_default_value(self)
        if template_parameter_constraint.is_pack:
            self.result += '...'
