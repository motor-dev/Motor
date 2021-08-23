"""
simple-requirement:
    expression ;
"""

import glrp
from .....parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('simple-requirement : expression ";"')
@cxx20
def simple_requirement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser
