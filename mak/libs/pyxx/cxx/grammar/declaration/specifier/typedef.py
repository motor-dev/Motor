"""
typedef-name:
    identifier
    simple-template-id
"""

import glrp
from ....parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('typedef-name[prec:right,1][split:typedef_name] : "identifier"')
@glrp.rule('typedef-name[prec:right,1][split:typedef_template_id] : simple-template-id')
@cxx98
def typedef_name(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser