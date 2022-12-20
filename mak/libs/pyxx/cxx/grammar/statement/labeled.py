"""
labeled-statement:
    attribute-specifier-seq? identifier : statement
    attribute-specifier-seq? case constant-expression : statement
    attribute-specifier-seq? default : statement
"""

import glrp
from ...parse import cxx98
from ....ast.statements import LabeledStatement, CaseStatement, DefaultStatement
from motor_typing import TYPE_CHECKING


@glrp.rule('labeled-statement : attribute-specifier-seq? begin-expression-statement "identifier" ":" statement')
@cxx98
def labeled_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LabeledStatement(p[0], p[2].text(), p[4])


@glrp.rule(
    'labeled-statement : attribute-specifier-seq? begin-expression-statement  "case" constant-expression ":" statement'
)
@cxx98
def labeled_statement_case(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return CaseStatement(p[0], p[3], p[5])


@glrp.rule('labeled-statement : attribute-specifier-seq? begin-expression-statement  "default" ":" statement')
@cxx98
def labeled_statement_default(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DefaultStatement(p[0], p[4])


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser