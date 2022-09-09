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


@glrp.rule('type-specifier-pre : cv-qualifier')
@glrp.rule('type-specifier-def : simple-type-specifier-def')
@glrp.rule('type-specifier-def : elaborated-type-specifier')
@glrp.rule('type-specifier-def : typename-specifier')
@glrp.rule('type-specifier-tail : simple-type-specifier-tail')
@glrp.rule('type-specifier-tail : cv-qualifier')
@cxx98
def type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('type-specifier-seq : type-specifier-pre type-specifier-seq')
@glrp.rule('type-specifier-seq : type-specifier-def type-specifier-seq-tail')
@cxx98
def type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('type-specifier-seq-tail : attribute-specifier-seq?')
@glrp.rule('type-specifier-seq-tail : type-specifier-tail type-specifier-seq-tail')
@cxx98
def type_specifier_seq_tail(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier-pre : type-specifier-pre')
@glrp.rule('defining-type-specifier-def : type-specifier-def')
@glrp.rule('defining-type-specifier-def : class-specifier')
@glrp.rule('defining-type-specifier-def : enum-specifier')
@glrp.rule('defining-type-specifier-tail : type-specifier-tail')
@cxx98
def defining_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier-seq : defining-type-specifier-pre defining-type-specifier-seq')
@glrp.rule('defining-type-specifier-seq : defining-type-specifier-def defining-type-specifier-seq-tail')
@cxx98
def defining_type_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('defining-type-specifier-seq-tail : attribute-specifier-seq?')
@glrp.rule('defining-type-specifier-seq-tail : defining-type-specifier-tail defining-type-specifier-seq-tail')
@cxx98
def defining_type_specifier_seq_tail(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('type-specifier-seq')
@cxx98_merge
def ambiguous_type_specifier_seq(self, ambiguous_simple_type_specifier, ambiguous_nested_name_specifier):
    # type: (CxxParser, Any, Any) -> Any
    # Not a conflict;
    pass


@glrp.merge('type-specifier-seq')
@cxx98_merge
def ambiguous_type_specifier_seq_2(self, ambiguous_template_type_name, class_template_id):
    # type: (CxxParser, Any, Any) -> Any
    # Not a conflict;
    pass


@glrp.merge('defining-type-specifier-seq')
@cxx98_merge
def ambiguous_defining_type_specifier_seq(self, ambiguous_simple_type_specifier, ambiguous_nested_name_specifier):
    # type: (CxxParser, Any, Any) -> Any
    # Not a conflict;
    pass


@glrp.merge('defining-type-specifier-seq')
@cxx98_merge
def ambiguous_defining_type_specifier_seq_2(self, ambiguous_template_type_name, class_template_id):
    # type: (CxxParser, Any, Any) -> Any
    # Not a conflict;
    pass


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser