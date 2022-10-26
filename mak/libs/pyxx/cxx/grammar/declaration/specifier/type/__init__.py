"""
type-specifier:
    simple-type-specifier
    elaborated-type-specifier
    typename-specifier
    cv-qualifier

type-specifier-seq:
    type-specifier attribute-specifier-seq?
    type-specifier type-specifier-seq

defining-type-specifier:
    type-specifier
    class-specifier
    enum-specifier

defining-type-specifier-seq:
    defining-type-specifier attribute-specifier-seq?
    defining-type-specifier defining-type-specifier-seq
"""

import glrp
from .....parser import cxx98
from ......ast.types import TypeSpecifierSeq, DefiningTypeSpecifierSeq
from motor_typing import TYPE_CHECKING
from . import simple
from . import elaborated
from . import decltype
from . import placeholder


@glrp.rule('type-specifier-1 : cv-qualifier')
@glrp.rule('type-specifier-2 : simple-type-specifier-2')
@glrp.rule('type-specifier-2 : elaborated-type-specifier')
@glrp.rule('type-specifier-2 : typename-specifier')
@glrp.rule('type-specifier-3 : cv-qualifier')
@glrp.rule('type-specifier-3 : simple-type-specifier-3')
@cxx98
def type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('type-specifier-seq : type-specifier-1 type-specifier-seq')
@glrp.rule('type-specifier-seq : type-specifier-2 type-specifier-seq-tail')
@glrp.rule('type-specifier-seq-tail : type-specifier-3 type-specifier-seq-tail')
@cxx98
def type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[1]
    result.add(p[0])
    return result


@glrp.rule('type-specifier-seq-tail : attribute-specifier-seq?')
@cxx98
def type_specifier_seq_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeSpecifierSeq(p[0])


@glrp.rule('defining-type-specifier-1 : type-specifier-1')
@glrp.rule('defining-type-specifier-2 : type-specifier-2')
@glrp.rule('defining-type-specifier-2 : class-specifier')
@glrp.rule('defining-type-specifier-2 : enum-specifier')
@glrp.rule('defining-type-specifier-3 : type-specifier-3')
@cxx98
def defining_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('defining-type-specifier-seq : defining-type-specifier-1 defining-type-specifier-seq')
@glrp.rule('defining-type-specifier-seq : defining-type-specifier-2 defining-type-specifier-seq-tail')
@glrp.rule('defining-type-specifier-seq-tail : defining-type-specifier-3 defining-type-specifier-seq-tail')
@cxx98
def defining_type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[1]
    result.add(p[0])
    return result


@glrp.rule('defining-type-specifier-seq-tail : attribute-specifier-seq?')
@cxx98
def defining_type_specifier_seq_end(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DefiningTypeSpecifierSeq(p[0])


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser