"""
lambda-capture:
    capture-default
    capture-list
    capture-default , capture-list

capture-default:
    &
    =

capture-list:
    capture
    capture-list , capture

capture:
    simple-capture
    init-capture

simple-capture:
    identifier ...?
    & identifier ...?
    this
    * this

init-capture:
    ...?  identifier initializer
    & ...? identifier initializer
"""

import glrp
from .....parser import cxx11
from motor_typing import TYPE_CHECKING


@glrp.rule('lambda-capture? : capture-default')
@glrp.rule('lambda-capture? : capture-list')
@glrp.rule('lambda-capture? : capture-default "," capture-list')
@glrp.rule('lambda-capture? : ')
@cxx11
def lambda_capture_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('capture-default : "&"')
@glrp.rule('capture-default : "="')
@cxx11
def capture_default_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('capture-list : capture')
@glrp.rule('capture-list : capture-list "," capture')
@cxx11
def capture_list_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('capture : simple-capture')
@glrp.rule('capture : init-capture')
@cxx11
def capture_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('simple-capture : "identifier"  "..."?')
@glrp.rule('simple-capture : "&" "identifier" "..."?')
@glrp.rule('simple-capture :"this"')
@glrp.rule('simple-capture :"*" "this"')
@cxx11
def simple_capture_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('init-capture : "identifier" initializer')
@glrp.rule('init-capture : "..." "identifier" initializer')
@glrp.rule('init-capture : "&" "identifier" initializer')
@glrp.rule('init-capture : "&" "..." "identifier" initializer')
@cxx11
def init_capture_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser