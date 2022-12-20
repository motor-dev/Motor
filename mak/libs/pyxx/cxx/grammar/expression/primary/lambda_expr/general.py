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
from .....parse import cxx11, cxx17, cxx20, cxx23
from ......ast.lambdas import LambdaExpression, TemplateLambdaExpression, LambdaSpecifiers, LambdaDeclarator
from motor_typing import TYPE_CHECKING


@glrp.rule('lambda-expression : lambda-introducer attribute-specifier-seq? lambda-declarator compound-statement')
@cxx11
def lambda_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LambdaExpression(p[0], p[1], p[2], p[3])


@glrp.rule(
    'lambda-expression : lambda-introducer "<" template-parameter-list "#>"  requires-clause? attribute-specifier-seq? lambda-declarator compound-statement'
)
@cxx20
def lambda_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TemplateLambdaExpression(p[0], p[2], p[4], p[5], p[6], p[7])


@glrp.rule('lambda-introducer : "[" lambda-capture? "]"')
@cxx11
def lambda_introducer_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1]


@glrp.rule(
    'lambda-declarator : lambda-specifier-seq noexcept-specification? attribute-specifier-seq? trailing-return-type?'
)
@cxx11
def lambda_declarator_noparams_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LambdaDeclarator(None, p[0], p[1], p[2], p[3], None)


@glrp.rule('lambda-declarator : noexcept-specification attribute-specifier-seq? trailing-return-type?')
@cxx11
def lambda_declarator_noexcept_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LambdaDeclarator(None, [], p[0], p[1], p[2], None)


@glrp.rule('lambda-declarator : trailing-return-type?')
@cxx11
def lambda_declarator_return_type_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LambdaDeclarator(None, [], None, [], p[0], None)


@glrp.rule(
    'lambda-declarator : "(" parameter-declaration-clause ")" lambda-specifier-seq? noexcept-specification? attribute-specifier-seq? trailing-return-type?'
)
@cxx11
def lambda_declarator_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LambdaDeclarator(p[1], p[3], p[4], p[5], p[6], None)


@glrp.rule(
    'lambda-declarator : "(" parameter-declaration-clause ")" lambda-specifier-seq? noexcept-specification? attribute-specifier-seq? trailing-return-type? requires-clause'
)
@cxx20
def lambda_declarator_requires_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LambdaDeclarator(p[1], p[3], p[4], p[5], p[6], p[7])


@glrp.rule('lambda-specifier : "mutable"')
@cxx11
def lambda_specifier_mutable_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LambdaSpecifiers.MUTABLE


@glrp.rule('lambda-specifier : "constexpr"')
@cxx17
def lambda_specifier_constexpr_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LambdaSpecifiers.CONSTEXPR


@glrp.rule('lambda-specifier : "consteval"')
@cxx20
def lambda_specifier_consteval_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LambdaSpecifiers.CONSTEVAL


@glrp.rule('lambda-specifier : "static"')
@cxx23
def lambda_specifier_static_cxx23(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LambdaSpecifiers.STATIC


@glrp.rule('lambda-specifier-seq : lambda-specifier')
@glrp.rule('lambda-specifier-seq? : lambda-specifier')
@cxx11
def lambda_specifier_seq_end_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return [p[0]]


@glrp.rule('lambda-specifier-seq : lambda-specifier lambda-specifier-seq')
@glrp.rule('lambda-specifier-seq? : lambda-specifier lambda-specifier-seq')
@cxx11
def lambda_specifier_seq_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[1]
    result.insert(0, p[0])


@glrp.rule('lambda-specifier-seq? :')
@cxx11
def lambda_specifier_seq_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return []


if TYPE_CHECKING:
    from typing import Any
    from .....parse import CxxParser