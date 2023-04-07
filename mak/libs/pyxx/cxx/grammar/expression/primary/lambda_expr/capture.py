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
from typing import Any
from .....parse import CxxParser, cxx11
from ......ast.lambdas import LambdaCaptureDefaultCopy, LambdaCaptureDefaultReference, LambdaCaptureList, SimpleCapture, ThisCapture


@glrp.rule('lambda-capture? : capture-default')
@cxx11
def lambda_capture_capture_default_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return (p[0], None)


@glrp.rule('lambda-capture? : capture-list')
@cxx11
def lambda_capture_capture_list_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return (None, LambdaCaptureList(p[0]))


@glrp.rule('lambda-capture? : capture-default "," capture-list')
@cxx11
def lambda_capture_capture_default_list_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return (p[0], LambdaCaptureList(p[2]))


@glrp.rule('lambda-capture? : ')
@cxx11
def lambda_capture_opt_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return (None, None)


@glrp.rule('capture-default : "&"')
@cxx11
def capture_default_reference_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaCaptureDefaultReference()


@glrp.rule('capture-default : "="')
@cxx11
def capture_default_copy_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return LambdaCaptureDefaultCopy()


@glrp.rule('capture-list : capture')
@cxx11
def capture_list_end_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return [p[0]]


@glrp.rule('capture-list : capture-list "," capture')
@cxx11
def capture_list_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(p[2])
    return result


@glrp.rule('capture : simple-capture')
@glrp.rule('capture : init-capture')
@cxx11
def capture_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('simple-capture : "identifier"  "..."?')
@cxx11
def simple_capture_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCapture(p[0].text(), False, p[1], None)


@glrp.rule('simple-capture : "&" "identifier" "..."?')
@cxx11
def simple_capture_ref_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCapture(p[1].text(), True, p[2], None)


@glrp.rule('simple-capture :"this"')
@cxx11
def this_capture_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ThisCapture(False)


@glrp.rule('simple-capture :"*" "this"')
@cxx11
def this_capture_copy_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ThisCapture(True)


@glrp.rule('init-capture : "identifier" initializer')
@cxx11
def init_capture_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCapture(p[0].text(), False, False, p[1])


@glrp.rule('init-capture : "..." "identifier" initializer')
@cxx11
def init_capture_pack_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCapture(p[1].text(), False, True, p[2])


@glrp.rule('init-capture : "&" "identifier" initializer')
@cxx11
def init_capture_ref_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCapture(p[1].text(), True, False, p[2])


@glrp.rule('init-capture : "&" "..." "identifier" initializer')
@cxx11
def init_capture_ref_pack_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCapture(p[2].text(), True, True, p[3])
