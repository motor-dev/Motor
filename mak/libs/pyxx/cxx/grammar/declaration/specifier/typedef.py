"""
typedef-name:
    identifier
    simple-template-id
"""

import glrp
from ....parse import cxx98, cxx20
from motor_typing import TYPE_CHECKING

#@glrp.rule('typedef-name : "identifier"')
#@cxx98
#def typedef_name(self: CxxParser, p: glrp.Production) -> Any:
#    # type: (CxxParser, glrp.Production) -> Any
#    pass
#
#
#@glrp.rule('typedef-name : simple-template-id')
#@cxx20
#def typedef_name_cxx20(self: CxxParser, p: glrp.Production) -> Any:
#    # type: (CxxParser, glrp.Production) -> Any
#    pass

if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser