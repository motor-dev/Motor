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
from ....parser import cxx98, cxx11, cxx20
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


#@glrp.rule('decl-specifier-seq : decl-specifier attribute-specifier-seq?')
@glrp.rule('decl-specifier-seq[split] : decl-specifier')
@glrp.rule('decl-specifier-seq : decl-specifier attribute-specifier-seq')
@glrp.rule('decl-specifier-seq : decl-specifier decl-specifier-seq')
@cxx98
def decl_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser