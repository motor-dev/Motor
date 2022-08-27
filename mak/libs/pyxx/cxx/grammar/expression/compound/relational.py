"""
relational-expression:
    compare-expression
    relational-expression < compare-expression
    relational-expression > compare-expression
    relational-expression <= compare-expression
    relational-expression >= compare-expression
"""

import glrp
from ....parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('relational-expression : compare-expression')
@glrp.rule('relational-expression : relational-expression "<" compare-expression')
@glrp.rule('relational-expression : relational-expression [prec:right,0]">" compare-expression')
@glrp.rule('relational-expression : relational-expression "<=" compare-expression')
@glrp.rule('relational-expression : relational-expression ">=" compare-expression')
@cxx98
def relational_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('relational-expression')
@cxx98_merge
def ambiguous_relational_expression_template_operator(self, template_operator, nontemplate_operator):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('relational-expression')
@cxx98_merge
def ambiguous_relational_expression_template_literal(self, template_literal, nontemplate_literal):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ....parser import CxxParser