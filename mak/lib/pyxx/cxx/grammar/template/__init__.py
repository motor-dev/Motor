"""
template-declaration:
    template-head declaration
    template-head concept-definition

template-head:
    template < template-parameter-list > requires-clause?

template-parameter-list:
    template-parameter
    template-parameter-list , template-parameter

requires-clause:
    requires constraint-logical-or-expression

constraint-logical-or-expression:
    constraint-logical-and-expression
    constraint-logical-or-expression || constraint-logical-and-expression

constraint-logical-and-expression:
    primary-expression
    constraint-logical-and-expression && primary-expression
"""

import glrp
from typing import Any, List
from ...parse import CxxParser, cxx98, cxx11, cxx20, cxx98_merge
from ....ast.template import TemplateDeclaration
from ....ast.expressions import BinaryExpression, IdExpression, ThisExpression, TypeTraitExpression, NullPtrExpression, \
    ParenthesizedExpression, ErrorExpression
from ....ast.literals import IntegerLiteral, UserDefinedIntegerLiteral, CharacterLiteral, UserDefinedCharacterLiteral, \
    FloatingLiteral, UserDefinedFloatingLiteral, BooleanLiteral, StringList
from ....ast.reference import Reference, Id, TemplateSpecifierId
from ....ast.constraints import RequiresClause
from . import parameter
from . import name
from . import explicit
from . import concept
from . import constraint
from . import guide


@glrp.rule('"#>" : ">"')
@cxx98
def template_bracket(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('"#>" : "%>"')
@cxx11
def template_bracket_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('template-declaration : attribute-specifier-seq? begin-declaration template-head declaration')
@cxx98
def template_declaration(self: CxxParser, p: glrp.Production) -> Any:
    return TemplateDeclaration(p[0], p[2][0], p[2][1], False, p[3])


@glrp.rule(
    'template-declaration : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" template-head declaration'
)
@cxx98
def template_declaration_extern(self: CxxParser, p: glrp.Production) -> Any:
    return TemplateDeclaration(p[0], p[4][0], p[4][1], True, p[5])


@glrp.rule('template-declaration : attribute-specifier-seq? begin-declaration template-head concept-definition')
@cxx20
def template_declaration_concept_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return TemplateDeclaration(p[0], p[2][0], p[2][1], False, p[3])


@glrp.rule(
    'template-declaration : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" template-head concept-definition'
)
@cxx20
def template_declaration_concept_extern_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return TemplateDeclaration(p[0], p[4][0], p[4][1], True, p[5])


@glrp.rule('template-head : "template" "<" template-parameter-list "#>"')
@cxx98
def template_head(self: CxxParser, p: glrp.Production) -> Any:
    return (p[2], None)


@glrp.rule('template-head : "template" "<" template-parameter-list "#>" requires-clause')
@cxx20
def template_head_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return (p[2], p[4])


@glrp.rule('template-parameter-list : template-parameter')
@cxx98
def template_parameter_list_end(self: CxxParser, p: glrp.Production) -> Any:
    return [[p[0]]]


@glrp.rule('template-parameter-list : template-parameter-list "," template-parameter')
@cxx98
def template_parameter_list(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    for r in result:
        r.append(p[2])
    return result


@glrp.rule('requires-clause : "requires" constraint-logical-or-expression')
@glrp.rule('requires-clause? : "requires" constraint-logical-or-expression')
@cxx20
def requires_clause_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return RequiresClause(p[1])


@glrp.rule('requires-clause? :')
@cxx20
def requires_clause_opt_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('constraint-logical-or-expression : constraint-logical-and-expression')
@cxx20
def constraint_logical_or_expression_end_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('constraint-logical-or-expression : constraint-logical-or-expression "||" constraint-logical-and-expression')
@cxx20
def constraint_logical_or_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule('constraint-logical-and-expression : constraint-primary-expression')
@cxx20
def constraint_logical_and_expression_end_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule(
    'constraint-logical-and-expression : constraint-logical-and-expression [prec:left,1]"&&" constraint-primary-expression'
)
@cxx20
def constraint_logical_and_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule('constraint-primary-expression : "integer-literal"')
@cxx20
def constraint_primary_expression_integer_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return IntegerLiteral(p[0].text())


@glrp.rule('constraint-primary-expression : "character-literal"')
@cxx20
def constraint_primary_expression_character_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return CharacterLiteral(p[0].text())


@glrp.rule('constraint-primary-expression : "floating-literal"')
@cxx20
def constraint_primary_expression_floating_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return FloatingLiteral(p[0].text())


@glrp.rule('constraint-primary-expression : string-literal-list')
@cxx20
def constraint_primary_expression_string_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return StringList(p[0])


@glrp.rule('constraint-primary-expression : "this"')
@cxx20
def constraint_primary_expression_this_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ThisExpression()


@glrp.rule('constraint-primary-expression : "true"')
@cxx20
def constraint_primary_expression_true_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return BooleanLiteral(True)


@glrp.rule('constraint-primary-expression : "false"')
@cxx20
def constraint_primary_expression_false_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return BooleanLiteral(False)


@glrp.rule('constraint-primary-expression : "(" expression ")"')
@cxx20
def constraint_primary_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ParenthesizedExpression(p[1])


@glrp.rule('constraint-primary-expression : "(" "#error" ")"')
@cxx20
def constraint_primary_expression_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constraint-primary-expression : constraint-id-expression')
@cxx20
def constraint_primary_expression_constraint_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return IdExpression(p[0])


@glrp.rule('constraint-primary-expression : "user-defined-integer-literal"')
@cxx20
def constraint_primary_expression_user_defined_integer_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return UserDefinedIntegerLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('constraint-primary-expression : "user-defined-character-literal"')
@cxx20
def constraint_primary_expression_user_defined_character_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return UserDefinedCharacterLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('constraint-primary-expression : "user-defined-floating-literal"')
@cxx20
def constraint_primary_expression_user_defined_floating_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return UserDefinedFloatingLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('constraint-primary-expression : "type-trait-macro"')
@cxx20
def constraint_primary_expression_type_trait_macro_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return TypeTraitExpression(p[0].text(), None)


@glrp.rule('constraint-primary-expression : "type-trait-macro-function" "(" balanced-token-seq? ")"')
@cxx20
def constraint_primary_expression_type_trait_macro_arguments_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return TypeTraitExpression(p[0].text(), p[2])


@glrp.rule('constraint-primary-expression : requires-expression')
@cxx20
def constraint_primary_expression_requires_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return IdExpression(p[0])


@glrp.rule('constraint-primary-expression : "nullptr"')
@cxx20
def constraint_primary_expression_nullptr_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return NullPtrExpression()


@glrp.rule('constraint-id-expression : constraint-unqualified-id')
@cxx20
def constraint_id_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return Reference([p[0]])


@glrp.rule('constraint-id-expression : constraint-qualified-id')
@cxx20
def constraint_id_expression_qualified_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return Reference(p[0])


@glrp.rule('constraint-unqualified-id : "identifier"')
@cxx20
def constraint_unqualified_id_identifier_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return Id(p[0].position, p[0].text())


@glrp.rule('constraint-unqualified-id : template-id')
@cxx20
def constraint_unqualified_id_template_id_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('constraint-qualified-id : nested-name-specifier "template"? constraint-unqualified-id')
@cxx20
def constraint_qualified_id_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    id = p[2]
    if p[1]:
        id = TemplateSpecifierId(p[1].position, id)
    return p[0] + [id]


@glrp.rule('identifier? : identifier')
@cxx98
def identifier_opt(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].text()


@glrp.rule('identifier? : ')
@cxx98
def identifier_opt_empty(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.merge('template-parameter-list')
@cxx98_merge
def ambiguous_template_parameter_list(
        self: CxxParser, ambiguous_template_parameter_list: List[Any], ambiguous_template_parameter: List[Any],
        ambiguous_initializer_clause: List[Any], ambiguous_simple_type_specifier_2: List[Any]
) -> Any:
    return sum(
        ambiguous_template_parameter_list + ambiguous_template_parameter + ambiguous_initializer_clause +
        ambiguous_simple_type_specifier_2, []
    )
