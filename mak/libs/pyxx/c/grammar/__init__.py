from . import declarations
from . import expressions
from . import external_definitions
from . import statements

import glrp
from ..parser import c89
from motor_typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..parser import CParser