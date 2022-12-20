"""
literal-operator-id:
    operator string-literal identifier
    operator user-defined-string-literal
"""

import glrp
from ...parse import cxx11
from ....ast.reference import LiteralOperatorId
from motor_typing import TYPE_CHECKING


@glrp.rule('literal-operator-id : "operator" "string-literal" "identifier"')
@cxx11
def literal_operator_id_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LiteralOperatorId(p[2].text())


@glrp.rule('literal-operator-id : "operator" user-defined-string-literal')
@cxx11
def literal_operator_user_defined_literal_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return LiteralOperatorId(p[1].value[1])


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser