"""
literal-operator-id:
    operator string-literal identifier
    operator user-defined-string-literal
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx11
from ....ast.reference import LiteralOperatorId


@glrp.rule('literal-operator-id : "operator" "string-literal" "identifier"')
@cxx11
def literal_operator_id_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    position = p[0].position[0], p[2].position[1]
    return LiteralOperatorId(position, p[2].text())


@glrp.rule('literal-operator-id : "operator" user-defined-string-literal')
@cxx11
def literal_operator_user_defined_literal_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    position = p[0].position[0], p[1].position[1]
    return LiteralOperatorId(position, p[1].value[1])
