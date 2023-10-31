"""
function-specifier:
    virtual
    explicit-specifier

explicit-specifier:
    explicit ( constant-expression )
    explicit
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, cxx17, cxx20
from .....ast.declarations import ExplicitSpecifier, FunctionSpecifiers, ErrorSpecifier


@glrp.rule('function-specifier : "virtual"')
@cxx98
def function_specifier_virtual(self: CxxParser, p: glrp.Production) -> Any:
    return FunctionSpecifiers.VIRTUAL


@glrp.rule('function-specifier : explicit-specifier')
@cxx98
def function_specifier_explicit(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('explicit-specifier : "explicit"')
@cxx98
def explicit_specifier(self: CxxParser, p: glrp.Production) -> Any:
    return ExplicitSpecifier(None)


@glrp.rule('explicit-specifier? : "explicit"')
@cxx17
def explicit_specifier_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return ExplicitSpecifier(None)


@glrp.rule('explicit-specifier : "explicit" [prec:left,1]"(" constant-expression ")"')
@glrp.rule('explicit-specifier? : "explicit" [prec:left,1]"(" constant-expression ")"')
@cxx20
def explicit_specifier_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ExplicitSpecifier(p[2])


@glrp.rule('explicit-specifier : "explicit" [prec:left,1]"(" "#error" ")"')
@glrp.rule('explicit-specifier? : "explicit" [prec:left,1]"(" "#error" ")"')
@cxx20
def explicit_specifier_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorSpecifier()


@glrp.rule('explicit-specifier? : ')
@cxx17
def explicit_specifier_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None
