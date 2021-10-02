"""
nested-requirement:
    requires constraint-expression ;
"""

import glrp
from .....parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('nested-requirement : [prec:left,1]"requires" constraint-expression ";"')
@cxx20
def nested_requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser
