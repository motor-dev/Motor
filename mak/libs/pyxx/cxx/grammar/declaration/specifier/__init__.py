"""
decl-specifier:
    storage-class-specifier
    defining-type-specifier
    function-specifier
    friend
    typedef
    constexpr
    consteval
    constinit
    inline

decl-specifier-seq:
    decl-specifier attribute-specifier-seq?
    decl-specifier decl-specifier-seq
"""

import glrp
from ....parser import cxx98, cxx11, cxx20, cxx98_merge
from motor_typing import TYPE_CHECKING
from . import storage
from . import function
from . import typedef
from . import type


@glrp.rule('decl-specifier : storage-class-specifier')
@glrp.rule('decl-specifier : defining-type-specifier')
@glrp.rule('decl-specifier : function-specifier')
@glrp.rule('decl-specifier : "friend"')
@glrp.rule('decl-specifier : "typedef"')
@glrp.rule('decl-specifier : "inline"')
@glrp.rule('decl-specifier : "decl-specifier-macro"')
@cxx98
def decl_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier : "constexpr"')
@cxx11
def decl_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier : "consteval"')
@glrp.rule('decl-specifier : "constinit"')
@cxx20
def decl_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-end : decl-specifier [split:end_declaration_spec]')
@glrp.rule('decl-specifier-continue : decl-specifier [split:continue_declaration_spec]')
@cxx98
def decl_specifier_seq_proxies(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-seq : decl-specifier-end attribute-specifier-seq?')
@glrp.rule('decl-specifier-seq : decl-specifier-continue decl-specifier-seq')
@cxx98
def decl_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('decl-specifier-seq')
@cxx98_merge
def ambiguous_decl_specifier_seq(
    self, continue_declaration_spec, ambiguous_decl_specifier_continue, end_declaration_spec,
    decl_specifier_end_class_template_id, decl_specifier_end_class_name, decl_specifier_end_ambiguous_class_head_name
):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('decl-specifier-continue')
@cxx98_merge
def ambiguous_decl_specifier_continue(self, class_template_id, class_name, ambiguous_class_head_name):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('decl-specifier-end')
@cxx98_merge
def decl_specifier_end_class_template_id(self, class_template_id):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    pass


@glrp.merge('decl-specifier-end')
@cxx98_merge
def decl_specifier_end_class_name(self, class_name):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    pass


@glrp.merge('decl-specifier-end')
@cxx98_merge
def decl_specifier_end_ambiguous_class_head_name(self, ambiguous_class_head_name):
    # type: (CxxParser, Optional[glrp.Production]) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ....parser import CxxParser