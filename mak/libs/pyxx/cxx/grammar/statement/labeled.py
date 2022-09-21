"""
labeled-statement:
    attribute-specifier-seq? identifier : statement
    attribute-specifier-seq? case constant-expression : statement
    attribute-specifier-seq? default : statement
"""

import glrp
from ...parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('labeled-statement : begin-expression-statement attribute-specifier-seq? "identifier" ":" statement')
@glrp.rule(
    'labeled-statement : begin-expression-statement attribute-specifier-seq? "case" constant-expression ":" statement'
)
@glrp.rule('labeled-statement : begin-expression-statement attribute-specifier-seq? "default" ":" statement')
@cxx98
def labeled_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser