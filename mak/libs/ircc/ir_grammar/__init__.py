from . import lex

from .ir_translation_unit import *
from .ir_header import *
from .ir_declaration import *
from .ir_attributes import *
from .ir_metadata import *
from .ir_comdat import *
from .ir_type import *
from .ir_method import *
from .ir_variable import *
from .ir_value import *
from .ir_expr import *
from .ir_instruction import *
from .ir_opcodes import *

from motor_typing import TYPE_CHECKING


def p_empty(p):
    # type: (YaccProduction) -> None
    """
        empty :
    """
    p[0] = None


def p_error(p):
    # type: (YaccProduction) -> None
    """
        error :
    """
    assert False, 'this function is replaced at runtime, it should never be called'


tokens = lex.tokens
keywords = lex.keywords    # type: Tuple[str, ...]

if TYPE_CHECKING:
    from typing import Tuple
    from ply.yacc import YaccProduction