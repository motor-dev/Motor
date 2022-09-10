"""
typedef-name:
    identifier
    simple-template-id
"""

import glrp
from ....parser import cxx98, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('typedef-name[prec:right,1][split:typedef_name] : "identifier"')
@cxx98
def typedef_name(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('typedef-name[prec:right,1][split:typedef_template_id] : simple-template-id')
@cxx20
def typedef_name_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser