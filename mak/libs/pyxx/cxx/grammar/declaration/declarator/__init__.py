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
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('init-declarator : begin-declarator-no-initializer declarator')
@glrp.rule('init-declarator : begin-declarator-initializer [no-merge-warning]declarator initializer')
@cxx98
def init_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('init-declarator : begin-declarator-no-initializer declarator requires-clause')
@cxx20
def init_declarator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-declarator-no-initializer: [split:declarator_no_initializer]')
@glrp.rule('begin-declarator-initializer: [split:declarator_initializer]')
@cxx98
def begin_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('init-declarator')
@cxx98_merge
def ambiguous_init_declarator_initializer(self, continue_declarator_list, end_declarator_list):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    # end_declarator_list should always mark the end of recursion, and continue_declarator_list should always be None here.
    assert continue_declarator_list is None
    return end_declarator_list


@glrp.merge('init-declarator')
@cxx98_merge
def ambiguous_init_declarator(self, declarator_no_initializer, declarator_initializer):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser