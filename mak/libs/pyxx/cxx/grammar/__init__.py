from . import basic
from . import expression
from . import statement
from . import declaration
from . import module
from . import klass
from . import overload
from . import template
from . import exception

import glrp
from typing import Set
from ..parse import CxxParser
from ...messages import C0000, C0001


@glrp.error_handler
def p_error(parser: CxxParser, token: glrp.Token, parsing_rules: Set[str]) -> None:
    if parsing_rules:
        C0001(parser.logger, token.position, parser.symbol_name(token), ', '.join(sorted(parsing_rules)))
    else:
        C0000(parser.logger, token.position, parser.symbol_name(token))
