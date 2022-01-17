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
from ...parser import cxx98, cxx11, cxx20
from motor_typing import TYPE_CHECKING
from . import parameter
from . import name
from . import explicit
from . import concept
from . import constraint
from . import guide


@glrp.rule('template-declaration : attribute-specifier-seq? "extern"? template-head declaration')
@cxx98
def template_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-declaration : attribute-specifier-seq? "extern"? template-head concept-definition')
@cxx20
def template_declaration_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-head : "template" "<" template-parameter-list ">"')
@cxx98
def template_head(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-head : "template" "<" template-parameter-list ">" requires-clause')
@cxx20
def template_head_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('template-parameter-list : template-parameter')
@glrp.rule('template-parameter-list : template-parameter-list "," template-parameter')
@cxx98
def template_parameter_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('requires-clause : "requires" constraint-logical-or-expression')
@cxx20
def requires_clause_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('constraint-logical-or-expression : constraint-logical-and-expression')
@glrp.rule('constraint-logical-or-expression : constraint-logical-or-expression "||" constraint-logical-and-expression')
@cxx20
def constraint_logical_or_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('constraint-logical-and-expression : constraint-primary-expression')
@glrp.rule(
    'constraint-logical-and-expression : constraint-logical-and-expression [prec:left,1]"&&" constraint-primary-expression'
)
@cxx20
def constraint_logical_and_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('constraint-primary-expression : "integer-literal"')
@glrp.rule('constraint-primary-expression : "character-literal"')
@glrp.rule('constraint-primary-expression : "floating-literal"')
@glrp.rule('constraint-primary-expression : "string-literal"')
@glrp.rule('constraint-primary-expression : "this"')
@glrp.rule('constraint-primary-expression : "true"')
@glrp.rule('constraint-primary-expression : "false"')
@glrp.rule('constraint-primary-expression : "(" expression ")"')
@glrp.rule('constraint-primary-expression : constraint-id-expression')
@glrp.rule('constraint-primary-expression : "user-defined-integer-literal"')
@glrp.rule('constraint-primary-expression : "user-defined-character-literal"')
@glrp.rule('constraint-primary-expression : "user-defined-floating-literal"')
@glrp.rule('constraint-primary-expression : "user-defined-string-literal"')
@cxx20
def constraint_primary_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('constraint-id-expression : constraint-unqualified-id')
@glrp.rule('constraint-id-expression : constraint-qualified-id')
@cxx20
def constraint_id_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('constraint-unqualified-id : "identifier"')
@glrp.rule('constraint-unqualified-id : template-id')
@cxx20
def constraint_unqualified_id_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('constraint-qualified-id : nested-name-specifier "template"? constraint-unqualified-id')
@cxx20
def constraint_qualified_id_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('identifier? : identifier')
@glrp.rule('identifier? : ')
@cxx98
def identifier_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser