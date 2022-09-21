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
from motor_typing import TYPE_CHECKING
from . import simple
from . import elaborated
from . import decltype
from . import placeholder


@glrp.rule('type-specifier : simple-type-specifier')
@glrp.rule('type-specifier : elaborated-type-specifier')
@glrp.rule('type-specifier : typename-specifier')
@glrp.rule('type-specifier : cv-qualifier')
@cxx98
def type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('type-specifier-seq : type-specifier attribute-specifier-seq? [split:type_specifier_seq_end]')
@glrp.rule(
    'type-specifier-seq : type-specifier attribute-specifier-seq? type-specifier-seq-continue type-specifier-seq'
)
@cxx98
def type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('defining-type-specifier : type-specifier')
@glrp.rule('defining-type-specifier : class-specifier')
@glrp.rule('defining-type-specifier : enum-specifier')
@cxx98
def defining_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule(
    'defining-type-specifier-seq : defining-type-specifier attribute-specifier-seq? [split:defining_type_specifier_seq_end]'
)
@glrp.rule(
    'defining-type-specifier-seq : defining-type-specifier attribute-specifier-seq? defining-type-specifier-seq-continue defining-type-specifier-seq'
)
@cxx98
def defining_type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('type-specifier-seq-continue : [split:type_specifier_seq_continue]')
@cxx98
def type_specifier_seq_continue(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('defining-type-specifier-seq-continue : [split:defining_type_specifier_seq_continue]')
@cxx98
def defining_type_specifier_seq_continue(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser