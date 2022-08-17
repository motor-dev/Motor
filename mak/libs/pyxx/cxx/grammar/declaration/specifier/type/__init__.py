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
from .....parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING
from . import simple
from . import elaborated
from . import decltype
from . import placeholder


@glrp.rule('type-specifier-1 : cv-qualifier')
@glrp.rule('type-specifier-2 : simple-type-specifier[split:ambiguous_simple_type_specifier]')
@glrp.rule('type-specifier-2 : elaborated-type-specifier')
@glrp.rule('type-specifier-2 : typename-specifier[split:ambiguous_simple_type_specifier]')
@glrp.rule('type-specifier-3 : simple-type-specifier-3')
@glrp.rule('type-specifier-3 : elaborated-type-specifier')
@glrp.rule('type-specifier-3 : typename-specifier')
@glrp.rule('type-specifier-3 : cv-qualifier')
@cxx98
def type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('type-specifier-seq : type-specifier-1 type-specifier-seq')
@glrp.rule('type-specifier-seq : type-specifier-2 type-specifier-seq-tail')
@glrp.rule('type-specifier-seq-tail : attribute-specifier-seq?')
@glrp.rule('type-specifier-seq-tail : type-specifier-3 type-specifier-seq-tail')
@cxx98
def type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier-1 : type-specifier-1')
@glrp.rule('defining-type-specifier-2 : class-specifier')
@glrp.rule('defining-type-specifier-2 : enum-specifier')
@glrp.rule('defining-type-specifier-2 : type-specifier-2')
@glrp.rule('defining-type-specifier-3 : class-specifier')
@glrp.rule('defining-type-specifier-3 : enum-specifier')
@glrp.rule('defining-type-specifier-3 : type-specifier-3')
@cxx98
def defining_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier-seq : defining-type-specifier-1 defining-type-specifier-seq')
@glrp.rule('defining-type-specifier-seq : defining-type-specifier-2 defining-type-specifier-seq-tail')
@cxx98
def defining_type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier-seq-tail : attribute-specifier-seq?')
@glrp.rule('defining-type-specifier-seq-tail : defining-type-specifier-3 defining-type-specifier-seq-tail')
@cxx98
def defining_type_specifier_seq_tail(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('type-specifier-2')
@cxx98_merge
def ambiguous_type_specifier(self, ambiguous_simple_type_specifier, ambiguous_nested_name_specifier):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('type-specifier-seq')
@cxx98_merge
def ambiguous_type_specifier_seq(self, ambiguous_class_head_name, class_name):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    # Should never reach; option #2  has a lower precedence than option #1, but it can't be detected
    # during the merge tree construction
    pass


@glrp.merge('defining-type-specifier-2')
@cxx98_merge
def ambiguous_defining_type_specifier_2(self, ambiguous_nested_name_specifier, ambiguous_type_specifier):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('defining-type-specifier-seq')
@cxx98_merge
def ambiguous_defining_type_specifier_seq(self, ambiguous_class_head_name, class_name):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    # Should never reach; option #2  has a lower precedence than option #1, but it can't be detected
    # during the merge tree construction
    pass


if TYPE_CHECKING:
    from typing import Optional
    from .....parser import CxxParser