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
from ....parser import cxx17
from motor_typing import TYPE_CHECKING


@glrp.rule('fold-expression : "(" begin-expression cast-expression fold-operator "..." ")"')
@glrp.rule('fold-expression : "(" "..." fold-operator cast-expression ")"')
@glrp.rule(
    'fold-expression : "(" begin-expression cast-expression fold-operator "..." fold-operator cast-expression ")"'
)
@cxx17
def fold_expression_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('fold-operator : [split:fold_expression]"+"')
@glrp.rule('fold-operator : [split:fold_expression]"-"')
@glrp.rule('fold-operator : [split:fold_expression]"*"')
@glrp.rule('fold-operator : [split:fold_expression]"/"')
@glrp.rule('fold-operator : [split:fold_expression]"%"')
@glrp.rule('fold-operator : [split:fold_expression]"^"')
@glrp.rule('fold-operator : [split:fold_expression]"&"')
@glrp.rule('fold-operator : [split:fold_expression]"|"')
@glrp.rule('fold-operator : [split:fold_expression]"<<"')
@glrp.rule('fold-operator : [split:fold_expression]">>"')
@glrp.rule('fold-operator : [split:fold_expression]"+="')
@glrp.rule('fold-operator : [split:fold_expression]"-="')
@glrp.rule('fold-operator : [split:fold_expression]"*="')
@glrp.rule('fold-operator : [split:fold_expression]"/="')
@glrp.rule('fold-operator : [split:fold_expression]"%="')
@glrp.rule('fold-operator : [split:fold_expression]"^="')
@glrp.rule('fold-operator : [split:fold_expression]"&="')
@glrp.rule('fold-operator : [split:fold_expression]"|="')
@glrp.rule('fold-operator : [split:fold_expression]"<<="')
@glrp.rule('fold-operator : [split:fold_expression]">>="')
@glrp.rule('fold-operator : [split:fold_expression]"="')
@glrp.rule('fold-operator : [split:fold_expression]"=="')
@glrp.rule('fold-operator : [split:fold_expression]"!="')
@glrp.rule('fold-operator : [split:fold_expression]"<"')
@glrp.rule('fold-operator : [split:fold_expression]">"')
@glrp.rule('fold-operator : [split:fold_expression]"<="')
@glrp.rule('fold-operator : [split:fold_expression]">="')
@glrp.rule('fold-operator : [split:fold_expression]"&&"')
@glrp.rule('fold-operator : [split:fold_expression]"||"')
@glrp.rule('fold-operator : [split:fold_expression]","')
@glrp.rule('fold-operator : [split:fold_expression]".*"')
@glrp.rule('fold-operator : [split:fold_expression]"->*"')
@cxx17
def fold_operator_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser
