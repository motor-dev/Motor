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
from typing import Set, Tuple, Dict, Any
from ..parse import CxxParser
from ...messages import error, Logger


@error
def C0000(self: Logger, position: Tuple[int, int], token: str) -> Dict[str, Any]:
    """syntax error at token '{token}'"""
    return locals()


@error
def C0001(self: Logger, position: Tuple[int, int], token: str, current_rules: str) -> Dict[str, Any]:
    """syntax error at token '{token}' when trying to parse {current_rules}"""
    return locals()


@glrp.error_handler
def p_error(parser: CxxParser, token: glrp.Token, parsing_rules: Set[str]) -> None:
    if parsing_rules:
        C0001(parser.logger, token.position, parser.symbol_name(token), "'%s'" % "', '".join(sorted(parsing_rules)))
    else:
        C0000(parser.logger, token.position, "'%s'" % parser.symbol_name(token))
