"""
fold-expression:
    ( cast-expression fold-operator ... )
    ( ... fold-operator cast-expression )
    ( cast-expression fold-operator ... fold-operator cast-expression )

fold-operator: one of
+   -   *   /   %   ^   &   |   <<  >>
+=  -=  *=  /=  %=  ^=  &=  |=  <<= >>= =
==  !=  <   >   <=  >=  &&  ||  ,   .*  ->*
"""

import glrp
from ....parser import cxx17, cxx17_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('fold-expression : "(" cast-expression-proxy fold-operator "..." ")"')
@glrp.rule('fold-expression : "(" "..." fold-operator cast-expression ")"')
@glrp.rule('fold-expression : "(" cast-expression-proxy fold-operator "..." fold-operator cast-expression ")"')
@cxx17
def fold_expression_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('cast-expression-proxy : cast-expression [split:fold_expression]')
@cxx17
def cast_expression_proxy_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('cast-expression-proxy')
@cxx17_merge
def ambiguous_cast_expression_template_operator(self, template_operator, nontemplate_operator):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('cast-expression-proxy')
@cxx17_merge
def ambiguous_cast_expression_template_literal(self, template_literal, nontemplate_literal):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.rule('fold-operator : "+"')
@glrp.rule('fold-operator : "-"')
@glrp.rule('fold-operator : "*"')
@glrp.rule('fold-operator : "/"')
@glrp.rule('fold-operator : "%"')
@glrp.rule('fold-operator : "^"')
@glrp.rule('fold-operator : "&"')
@glrp.rule('fold-operator : "|"')
@glrp.rule('fold-operator : "<<"')
@glrp.rule('fold-operator : ">>"')
@glrp.rule('fold-operator : "+="')
@glrp.rule('fold-operator : "-="')
@glrp.rule('fold-operator : "*="')
@glrp.rule('fold-operator : "/="')
@glrp.rule('fold-operator : "%="')
@glrp.rule('fold-operator : "^="')
@glrp.rule('fold-operator : "&="')
@glrp.rule('fold-operator : "|="')
@glrp.rule('fold-operator : "<<="')
@glrp.rule('fold-operator : ">>="')
@glrp.rule('fold-operator : "="')
@glrp.rule('fold-operator : "=="')
@glrp.rule('fold-operator : "!="')
@glrp.rule('fold-operator : "<"')
@glrp.rule('fold-operator : ">"')
@glrp.rule('fold-operator : "<="')
@glrp.rule('fold-operator : ">="')
@glrp.rule('fold-operator : "&&"')
@glrp.rule('fold-operator : "||"')
@glrp.rule('fold-operator : ","')
@glrp.rule('fold-operator : ".*"')
@glrp.rule('fold-operator : "->*"')
@cxx17
def fold_operator_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ....parser import CxxParser
