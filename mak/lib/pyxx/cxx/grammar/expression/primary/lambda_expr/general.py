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
from typing import Any
from .....parse import CxxParser, cxx11, cxx17, cxx20, cxx23
from ......ast.lambdas import LambdaExpression, TemplateLambdaExpression, LambdaSpecifiers, LambdaDeclarator
from ......ast.expressions import ErrorExpression


@glrp.rule('constant-expression : lambda-introducer attribute-specifier-seq? lambda-declarator compound-statement')
@glrp.rule('constant-expression# : lambda-introducer attribute-specifier-seq? lambda-declarator compound-statement')
@cxx11
def lambda_expression_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    if p[0] is not None and p[2] is not None:
        return LambdaExpression(p[0], p[1], p[2], p[3])
    else:
        return ErrorExpression()


@glrp.rule('constant-expression : lambda-introducer "#error" compound-statement')
@glrp.rule('constant-expression# : lambda-introducer "#error" compound-statement')
@cxx11
def lambda_expression_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule(
    'constant-expression : lambda-introducer "<" template-parameter-list "#>"  requires-clause? attribute-specifier-seq? lambda-declarator compound-statement'
)
@glrp.rule(
    'constant-expression# : lambda-introducer "<" template-parameter-list "#>"  requires-clause? attribute-specifier-seq? lambda-declarator compound-statement'
)
@cxx20
def lambda_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    if p[0] is not None and p[6] is not None:
        return TemplateLambdaExpression(p[0], p[2], p[4], p[5], p[6], p[7])
    else:
        return ErrorExpression()


@glrp.rule('constant-expression : lambda-introducer "<" template-parameter-list "#>" "#error" compound-statement')
@glrp.rule('constant-expression# : lambda-introducer "<" template-parameter-list "#>" "#error" compound-statement')
@cxx20
def lambda_expression_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('lambda-introducer : [prec:left,16]"[" lambda-capture? "]"')
@cxx11
def lambda_introducer_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('lambda-introducer : [prec:left,16]"[" "#error" "]"')
@cxx11
def lambda_introducer_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule(
    'lambda-declarator : lambda-specifier-seq noexcept-specification? attribute-specifier-seq? trailing-return-type?'
)
@cxx11
def lambda_declarator_noparams_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaDeclarator(None, p[0], p[1], p[2], p[3], None)


@glrp.rule('lambda-declarator : noexcept-specification attribute-specifier-seq? trailing-return-type?')
@cxx11
def lambda_declarator_noexcept_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaDeclarator(None, [], p[0], p[1], p[2], None)


@glrp.rule('lambda-declarator : trailing-return-type?')
@cxx11
def lambda_declarator_return_type_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaDeclarator(None, [], None, [], p[0], None)


@glrp.rule(
    'lambda-declarator : "(" parameter-declaration-clause ")" lambda-specifier-seq? noexcept-specification? attribute-specifier-seq? trailing-return-type?'
)
@cxx11
def lambda_declarator_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaDeclarator(p[1], p[3], p[4], p[5], p[6], None)


@glrp.rule(
    'lambda-declarator : "(" parameter-declaration-clause ")" lambda-specifier-seq? noexcept-specification? attribute-specifier-seq? trailing-return-type? requires-clause'
)
@cxx20
def lambda_declarator_requires_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaDeclarator(p[1], p[3], p[4], p[5], p[6], p[7])


@glrp.rule(
    'lambda-declarator : "(" "#error" ")" lambda-specifier-seq? noexcept-specification? attribute-specifier-seq? trailing-return-type?'
)
@cxx11
def lambda_declarator_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule(
    'lambda-declarator : "(" "#error" ")" lambda-specifier-seq? noexcept-specification? attribute-specifier-seq? trailing-return-type? requires-clause'
)
@cxx20
def lambda_declarator_requires_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('lambda-specifier : "mutable"')
@cxx11
def lambda_specifier_mutable_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaSpecifiers.MUTABLE


@glrp.rule('lambda-specifier : "constexpr"')
@cxx17
def lambda_specifier_constexpr_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaSpecifiers.CONSTEXPR


@glrp.rule('lambda-specifier : "consteval"')
@cxx20
def lambda_specifier_consteval_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaSpecifiers.CONSTEVAL


@glrp.rule('lambda-specifier : "static"')
@cxx23
def lambda_specifier_static_cxx23(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaSpecifiers.STATIC


@glrp.rule('lambda-specifier-seq : lambda-specifier')
@glrp.rule('lambda-specifier-seq? : lambda-specifier')
@cxx11
def lambda_specifier_seq_end_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return [p[0]]


@glrp.rule('lambda-specifier-seq : lambda-specifier lambda-specifier-seq')
@glrp.rule('lambda-specifier-seq? : lambda-specifier lambda-specifier-seq')
@cxx11
def lambda_specifier_seq_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    result = p[1]
    result.insert(0, p[0])
    return result


@glrp.rule('lambda-specifier-seq? :')
@cxx11
def lambda_specifier_seq_opt_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return []
