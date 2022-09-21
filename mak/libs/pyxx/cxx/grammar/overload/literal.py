"""
literal-operator-id:
    operator string-literal identifier
    operator user-defined-string-literal
"""

import glrp
from ...parser import cxx11
from motor_typing import TYPE_CHECKING


@glrp.rule('literal-operator-id : "operator" "string-literal" "identifier"')
@glrp.rule('literal-operator-id : "operator" user-defined-string-literal')
@cxx11
def literal_operator_id_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser