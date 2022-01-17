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


@glrp.rule('type-specifier : simple-type-specifier[split:declaration]')
@glrp.rule('type-specifier : elaborated-type-specifier')
@glrp.rule('type-specifier : typename-specifier[split:declaration]')
@glrp.rule('type-specifier : cv-qualifier')
@cxx98
def type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('type-specifier-seq : type-specifier end-type-specifier-seq attribute-specifier-seq?')
@glrp.rule('type-specifier-seq : type-specifier continue-type-specifier-seq type-specifier-seq')
@cxx98
def type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('end-type-specifier-seq[split:end_type_specifier_seq] :')
@cxx98
def end_type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('continue-type-specifier-seq[split:continue_type_specifier_seq] :')
@cxx98
def continue_type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier : type-specifier')
@glrp.rule('defining-type-specifier : class-specifier')
@glrp.rule('defining-type-specifier : enum-specifier')
@cxx98
def defining_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier-seq : defining-type-specifier end-type-specifier-seq attribute-specifier-seq?')
# TODO: attribute-specifier-seq? not allowed
@glrp.rule(
    'defining-type-specifier-seq : defining-type-specifier continue-type-specifier-seq defining-type-specifier-seq'
)
@cxx98
def defining_type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser