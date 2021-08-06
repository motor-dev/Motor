from . import declarations
from . import expressions
from . import external_definitions
from . import statements

import glrp
from ..parser import c89
from be_typing import TYPE_CHECKING


@c89
@glrp.rule('state-splitter : ')
def state_splitter(self, p):
    # type: (CParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ..parser import CParser