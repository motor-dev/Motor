"""
lambda-expression:
    lambda-introducer lambda-declarator compound-statement
    lambda-introducer < template-parameter-list > requires-clause? lambda-declarator compound-statement

lambda-introducer:
    [ lambda-capture? ]

lambda-declarator:
    lambda-specifiers
    ( parameter-declaration-clause ) lambda-specifiers requires-clause?

lambda-specifiers:
    decl-specifier-seq? noexcept-specifier? attribute-specifier-seq? trailing-return-type?
"""

import glrp
from .....parser import cxx11, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('lambda-expression : lambda-introducer lambda-declarator compound-statement')
@glrp.rule(
    'lambda-expression : lambda-introducer [action:split_rightshift]"<" template-parameter-list ">" lambda-declarator compound-statement'
)
@cxx11
def lambda_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'lambda-expression : lambda-introducer [action:split_rightshift]"<" template-parameter-list ">" requires-clause lambda-declarator compound-statement'
)
@cxx20
def lambda_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('lambda-introducer : "[" lambda-capture? "]"')
@cxx11
def lambda_introducer_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('lambda-declarator : lambda-specifiers')
@glrp.rule('lambda-declarator : "(" parameter-declaration-clause ")" lambda-specifiers')
@cxx11
def lambda_declarator_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('lambda-declarator : "(" parameter-declaration-clause ")" lambda-specifiers requires-clause')
@cxx20
def lambda_declarator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'lambda-specifiers : decl-specifier-seq? exception-specification? attribute-specifier-seq? trailing-return-type?'
)
@cxx11
def lambda_specifiers_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser