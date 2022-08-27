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


@glrp.rule('type-specifier : simple-type-specifier[split:typename_specifier]')
@glrp.rule('type-specifier : elaborated-type-specifier')
@glrp.rule('type-specifier : typename-specifier[split:typename_specifier]')
@glrp.rule('type-specifier : cv-qualifier')
@cxx98
def type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('type-specifier-end[split:end_type_specifier_seq] : type-specifier')
@glrp.rule('type-specifier-continue[split:continue_type_specifier_seq] : type-specifier')
@cxx98
def type_specifier_end_continue(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('type-specifier-seq : type-specifier-end attribute-specifier-seq?')
@glrp.rule('type-specifier-seq : type-specifier-continue type-specifier-seq')
@cxx98
def type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier : type-specifier')
@glrp.rule('defining-type-specifier : class-specifier')
@glrp.rule('defining-type-specifier : enum-specifier')
@cxx98
def defining_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier-end[split:end_defining_type_specifier_seq] : defining-type-specifier')
@glrp.rule('defining-type-specifier-continue[split:continue_defining_type_specifier_seq] : defining-type-specifier')
@cxx98
def defining_type_specifier_end_continue(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier-seq : defining-type-specifier-end attribute-specifier-seq?')
@glrp.rule('defining-type-specifier-seq : defining-type-specifier-continue defining-type-specifier-seq')
@cxx98
def defining_type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('type-specifier')
@cxx98_merge
def ambiguous_type_specifier(self, ambiguous_simple_type_specifier, typename_specifier):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('type-specifier-continue')
@cxx98_merge
def ambiguous_type_specifier_continue(self, class_template_id, class_name, ambiguous_class_head_name):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('type-specifier-end')
@cxx98_merge
def type_specifier_end_class_template_id(self, class_template_id):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    pass


@glrp.merge('type-specifier-end')
@cxx98_merge
def type_specifier_end_class_name(self, class_name):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    pass


@glrp.merge('type-specifier-end')
@cxx98_merge
def type_specifier_end_ambiguous_class_head_name(self, ambiguous_class_head_name):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    pass


@glrp.merge('type-specifier-seq')
@cxx98_merge
def ambiguous_type_specifier_seq(
    self, end_type_specifier_seq, type_specifier_end_class_template_id, type_specifier_end_class_name,
    type_specifier_end_ambiguous_class_head_name, continue_type_specifier_seq, ambiguous_type_specifier_continue
):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('defining-type-specifier-continue')
@cxx98_merge
def ambiguous_defining_type_specifier_continue(self, class_template_id, class_name, ambiguous_class_head_name):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('defining-type-specifier-end')
@cxx98_merge
def defining_type_specifier_end_class_template_id(self, class_template_id):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    pass


@glrp.merge('defining-type-specifier-end')
@cxx98_merge
def defining_type_specifier_end_class_name(self, class_name):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    pass


@glrp.merge('defining-type-specifier-end')
@cxx98_merge
def defining_type_specifier_end_ambiguous_class_head_name(self, ambiguous_class_head_name):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    pass


@glrp.merge('defining-type-specifier-seq')
@cxx98_merge
def ambiguous_defining_type_specifier_seq(
    self, end_defining_type_specifier_seq, defining_type_specifier_end_class_template_id,
    defining_type_specifier_end_class_name, defining_type_specifier_end_ambiguous_class_head_name,
    continue_defining_type_specifier_seq, ambiguous_defining_type_specifier_continue
):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


#@glrp.merge('type-specifier')
#@cxx98_merge
#def ambiguous_type_specifier_class(self, ambiguous_class_head_name, class_name):
#    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
#    pass

if TYPE_CHECKING:
    from typing import Optional
    from .....parser import CxxParser