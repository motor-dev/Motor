"""
primary-expression:
    literal
    this
    ( expression )
    id-expression
    lambda-expression
    fold-expression
    requires-expression
"""

import glrp
from ....parser import cxx98, cxx11, cxx17, cxx20, cxx98_merge
from motor_typing import TYPE_CHECKING
from . import id
from . import lambda_expr
from . import fold
from . import requires


@glrp.rule('primary-expression : "integer-literal"')
@glrp.rule('primary-expression : "character-literal"')
@glrp.rule('primary-expression : "floating-literal"')
@glrp.rule('primary-expression : string-literal-list')
@glrp.rule('primary-expression : "this"')
@glrp.rule('primary-expression : "true"')
@glrp.rule('primary-expression : "false"')
@glrp.rule('primary-expression : primary-expression-proxy')
@glrp.rule('primary-expression : id-expression')
@glrp.rule('primary-expression : "type-trait-macro"')
@glrp.rule('primary-expression : "type-trait-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def primary_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('primary-expression-proxy : "(" begin-expression expression ")"')
@cxx98
def primary_expression_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('primary-expression : "user-defined-integer-literal"')
@glrp.rule('primary-expression : "user-defined-character-literal"')
@glrp.rule('primary-expression : "user-defined-floating-literal"')
@glrp.rule('primary-expression : lambda-expression')
@glrp.rule('primary-expression : "nullptr"')
@cxx11
def primary_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('string-literal-list : "string-literal" string-literal-list?')
@glrp.rule('string-literal-list? : "string-literal" string-literal-list?')
@cxx98
def string_literal_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('string-literal-list : "user-defined-string-literal" string-literal-list?')
@glrp.rule('string-literal-list? : "user-defined-string-literal" string-literal-list?')
@cxx11
def string_literal_list_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('string-literal-list? : ')
@cxx98
def string_literal_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('primary-expression-proxy : fold-expression')
@cxx17
def primary_expression_proxy_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('primary-expression : requires-expression')
@cxx20
def primary_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('primary-expression-proxy')
@cxx98_merge
def ambiguous_primary_expression(self, expression, fold_expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser