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
from typing import Any, Dict, List, Tuple
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
from ....messages import error, Logger


@error
def invalid_attribute_template(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """an attribute cannot appear before a template declaration"""
    return locals()


@error
def template_declaration_multiple_entities(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """a template declaration can only declare a single entity"""
    return locals()


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
    for attribute in p[0]:
        if not attribute.is_extended():
            invalid_attribute_template(self.logger, attribute.position)
            break
    if p[3].declared_entity_count() > 1:
        template_declaration_multiple_entities(self.logger, p[3].declared_entity_position(1))
    p[3].add_attributes(p[0])
    return TemplateDeclaration(p[2][0], p[2][1], p[2][2], False, p[3])


@glrp.rule(
    'template-declaration : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" template-head declaration'
)
@cxx98
def template_declaration_extern(self: CxxParser, p: glrp.Production) -> Any:
    for attribute in p[0]:
        if not attribute.is_extended():
            invalid_attribute_template(self.logger, attribute.position)
            break
    if p[5].declared_entity_count() > 1:
        template_declaration_multiple_entities(self.logger, p[5].declared_entity_position(1))
    p[5].add_attributes(p[0])
    return TemplateDeclaration(p[4][0], p[4][1], p[4][2], True, p[5])


@glrp.rule('template-declaration : attribute-specifier-seq? begin-declaration template-head concept-definition')
@cxx20
def template_declaration_concept_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    for attribute in p[0]:
        if not attribute.is_extended():
            invalid_attribute_template(self.logger, attribute.position)
            break
    p[3].add_attributes(p[0])
    return TemplateDeclaration(p[2][0], p[2][1], p[2][2], False, p[3])


@glrp.rule(
    'template-declaration : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" template-head concept-definition'
)
@cxx20
def template_declaration_concept_extern_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    for attribute in p[0]:
        if not attribute.is_extended():
            invalid_attribute_template(self.logger, attribute.position)
            break
    p[5].add_attributes(p[0])
    return TemplateDeclaration(p[4][0], p[4][1], p[4][2], True, p[5])


@glrp.rule('template-head : "template" "<" template-parameter-list "#>"')
@cxx98
def template_head(self: CxxParser, p: glrp.Production) -> Any:
    return ((p[0].position[0], p[3].position[1]), p[2], None)


@glrp.rule('template-head : "template" "<" template-parameter-list "#>" requires-clause')
@cxx20
def template_head_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ((p[0].position[0], p[3].position[1]), p[2], p[4])


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


@glrp.rule('requires-clause : "requires" constraint-logical-expression')
@glrp.rule('requires-clause? : "requires" constraint-logical-expression')
@cxx20
def requires_clause_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return RequiresClause(p[1])


@glrp.rule('requires-clause? :')
@cxx20
def requires_clause_opt_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return None


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
