"""
conversion-function-id:
    operator conversion-type-id

conversion-type-id:
    type-specifier-seq conversion-declarator?

conversion-declarator:
    ptr-operator conversion-declarator?
"""

import glrp
from ...parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('conversion-function-id : operator conversion-type-id')
@cxx98
def conversion_function_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('conversion-type-id : type-specifier-seq')
@glrp.rule('conversion-type-id : type-specifier-seq conversion-declarator')
@cxx98
def conversion_type_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('conversion-declarator : ptr-operator conversion-declarator?')
@cxx98
def conversion_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('conversion-declarator? : ptr-operator conversion-declarator?')
@glrp.rule('conversion-declarator? : ')
@cxx98
def conversion_declarator_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser