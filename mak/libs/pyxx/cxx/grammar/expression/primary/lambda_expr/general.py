"""
lambda-expression:
    lambda-introducer attribute-specifier-seq? lambda-declarator compound-statement
    lambda-introducer < template-parameter-list > requires-clause? attribute-specifier-seq? lambda-declarator compound-statement

lambda-introducer:
    [ lambda-capture? ]

lambda-declarator:
    lambda-specifier-seq noexcept-specifier? attribute-specifier-seq? trailing-return-type? 
    noexcept-specifier attribute-specifier-seq? trailing-return-type?
    trailing-return-type?
    ( parameter-declaration-clause ) lambda-specifier-seq? noexcept-specifier? attribute-specifier-seq? trailing-return-type? requires-clause?

lambda-specifier:
    consteval
    constexpr
    mutable
    static

lambda-specifier-seq:
    lambda-specifier
    lambda-specifier lambda-specifier-seq 
"""

import glrp
from .....parser import cxx11, cxx17, cxx20, cxx23
from motor_typing import TYPE_CHECKING


@glrp.rule('lambda-expression : lambda-introducer attribute-specifier-seq? lambda-declarator compound-statement')
@cxx11
def lambda_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'lambda-expression : lambda-introducer [action:begin_template_list]"<" template-parameter-list "%>"  requires-clause? attribute-specifier-seq? lambda-declarator compound-statement'
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


@glrp.rule(
    'lambda-declarator : lambda-specifier-seq noexcept-specification? attribute-specifier-seq? trailing-return-type?'
)
@glrp.rule('lambda-declarator : noexcept-specification attribute-specifier-seq? trailing-return-type?')
@glrp.rule('lambda-declarator : trailing-return-type?')
@glrp.rule(
    'lambda-declarator : "(" parameter-declaration-clause ")" lambda-specifier-seq? noexcept-specification? attribute-specifier-seq? trailing-return-type?'
)
@cxx11
def lambda_declarator_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'lambda-declarator : "(" parameter-declaration-clause ")" lambda-specifier-seq? noexcept-specification? attribute-specifier-seq? trailing-return-type? requires-clause'
)
@cxx20
def lambda_declarator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('lambda-specifier : "mutable"')
@cxx11
def lambda_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('lambda-specifier : "constexpr"')
@cxx17
def lambda_specifier_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('lambda-specifier : "consteval"')
@cxx20
def lambda_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('lambda-specifier : "static"')
@cxx23
def lambda_specifier_cxx23(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('lambda-specifier-seq : lambda-specifier')
@glrp.rule('lambda-specifier-seq : lambda-specifier lambda-specifier-seq')
@cxx11
def lambda_specifier_seq_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('lambda-specifier-seq? :')
@glrp.rule('lambda-specifier-seq? : lambda-specifier-seq')
@cxx11
def lambda_specifier_seq_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser