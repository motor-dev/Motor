"""
init-declarator-list:
    init-declarator
    init-declarator-list , init-declarator

init-declarator:
    declarator initializer?
    declarator requires-clause
"""

import glrp
from ....parser import cxx98, cxx20, cxx98_merge
from motor_typing import TYPE_CHECKING
from . import declarator
from . import name
from . import function


@glrp.rule('init-declarator-list : init-declarator')
@glrp.rule('init-declarator-list : init-declarator-list "," init-declarator')
@cxx98
def init_declarator_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('init-declarator-list? : init-declarator')
@glrp.rule('init-declarator-list? : init-declarator-list "," init-declarator')
@glrp.rule('init-declarator-list? : ')
@cxx98
def init_declarator_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('init-declarator : begin-declarator-no-initializer declarator')
@glrp.rule('init-declarator : begin-declarator-initializer declarator initializer')
@cxx98
def init_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('init-declarator : begin-declarator-no-initializer declarator requires-clause')
@cxx20
def init_declarator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('begin-declarator-no-initializer: [split:declarator_no_initializer]')
@glrp.rule('begin-declarator-initializer: [split:declarator_initializer]')
@cxx98
def begin_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('init-declarator')
@cxx98_merge
def ambiguous_init_declarator(self, declarator_no_initializer, declarator_initializer):
    # type: (CxxParser, Any, Any) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser