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


@glrp.rule('decl-specifier-1 : storage-class-specifier')
@glrp.rule('decl-specifier-1 : defining-type-specifier-1')
@glrp.rule('decl-specifier-1 : function-specifier')
@glrp.rule('decl-specifier-1 : "friend"')
@glrp.rule('decl-specifier-1 : "typedef"')
@glrp.rule('decl-specifier-1 : "inline"')
@glrp.rule('decl-specifier-1 : "decl-specifier-macro"')
@glrp.rule('decl-specifier-2 : defining-type-specifier-2')
@glrp.rule('decl-specifier-3 : storage-class-specifier')
@glrp.rule('decl-specifier-3 : defining-type-specifier-3')
@glrp.rule('decl-specifier-3 : function-specifier')
@glrp.rule('decl-specifier-3 : "friend"')
@glrp.rule('decl-specifier-3 : "typedef"')
@glrp.rule('decl-specifier-3 : "inline"')
@glrp.rule('decl-specifier-3 : "decl-specifier-macro"')
@cxx98
def decl_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-1 : "constexpr"')
@glrp.rule('decl-specifier-3 : "constexpr"')
@cxx11
def decl_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-1 : "consteval"')
@glrp.rule('decl-specifier-1 : "constinit"')
@glrp.rule('decl-specifier-3 : "consteval"')
@glrp.rule('decl-specifier-3 : "constinit"')
@cxx20
def decl_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('decl-specifier-seq-proxy')
@cxx98_merge
def ambiguous_decl_specifier_seq(
    self, ambiguous_nested_name_specifier, ambiguous_type_specifier, ambiguous_defining_type_specifier_2
):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('decl-specifier-seq')
@cxx98_merge
def ambiguous_decl_specifier_seq_2(self, ambiguous_class_head_name, class_name):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    # Should never reach; option #2  has a lower precedence than option #1, but it can't be detected
    # during the merge tree construction
    pass


@glrp.rule('decl-specifier-seq : decl-specifier-seq-proxy')
@cxx98
def decl_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-seq-proxy : decl-specifier-1 decl-specifier-seq-proxy')
@glrp.rule('decl-specifier-seq-proxy : decl-specifier-2 decl-specifier-seq-tail')
@cxx98
def decl_specifier_seq_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-seq-tail : attribute-specifier-seq?')
@glrp.rule('decl-specifier-seq-tail : decl-specifier-3 decl-specifier-seq-tail')
@cxx98
def decl_specifier_seq_tail(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-seq? : decl-specifier-seq')
@glrp.rule('decl-specifier-seq? :')
@cxx11
def decl_specifier_seq_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ....parser import CxxParser