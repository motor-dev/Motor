"""
unqualified-id:
    identifier
    operator-function-id
    conversion-function-id
    literal-operator-id
    ~ type-name
    ~ decltype-specifier
    template-id
"""

import glrp
from .....parser import cxx98, cxx11
from motor_typing import TYPE_CHECKING


@glrp.rule('unqualified-id[prec:right,1] : "identifier"')
@glrp.rule('unqualified-id : operator-function-id')
@glrp.rule('unqualified-id : conversion-function-id')
@glrp.rule('unqualified-id : "~" destructor-disambiguation type-name')
@glrp.rule('unqualified-id : template-id')
@cxx98
def unqualified_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('unqualified-id : literal-operator-id')
@glrp.rule('unqualified-id : "~" destructor-disambiguation decltype-specifier')
@cxx11
def unqualified_id_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('destructor-disambiguation :')
@cxx98
def destructor_disambiguation(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser