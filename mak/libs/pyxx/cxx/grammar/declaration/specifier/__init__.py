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


@glrp.rule('decl-specifier-pre : storage-class-specifier')
@glrp.rule('decl-specifier-pre : defining-type-specifier-pre')
@glrp.rule('decl-specifier-pre : function-specifier')
@glrp.rule('decl-specifier-pre : "friend"')
@glrp.rule('decl-specifier-pre : "typedef"')
@glrp.rule('decl-specifier-pre : "inline"')
@glrp.rule('decl-specifier-pre : "decl-specifier-macro"')
@glrp.rule('decl-specifier-def : defining-type-specifier-def')
@glrp.rule('decl-specifier-tail : storage-class-specifier')
@glrp.rule('decl-specifier-tail : defining-type-specifier-tail')
@glrp.rule('decl-specifier-tail : function-specifier')
@glrp.rule('decl-specifier-tail : "friend"')
@glrp.rule('decl-specifier-tail : "typedef"')
@glrp.rule('decl-specifier-tail : "inline"')
@glrp.rule('decl-specifier-tail : "decl-specifier-macro"')
@cxx98
def decl_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-pre : "constexpr"')
@glrp.rule('decl-specifier-tail : "constexpr"')
@cxx11
def decl_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-pre : "consteval"')
@glrp.rule('decl-specifier-pre : "constinit"')
@glrp.rule('decl-specifier-tail : "consteval"')
@glrp.rule('decl-specifier-tail : "constinit"')
@cxx20
def decl_specifier_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-seq : decl-specifier-pre decl-specifier-seq')
@glrp.rule('decl-specifier-seq : decl-specifier-def decl-specifier-seq-tail')
@cxx98
def decl_specifier_seq(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('decl-specifier-seq-tail : attribute-specifier-seq?')
@glrp.rule('decl-specifier-seq-tail : decl-specifier-tail attribute-specifier-seq? decl-specifier-seq-tail')
@cxx98
def decl_specifier_seq_tail(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('decl-specifier-seq')
@cxx98_merge
def ambiguous_decl_specifier_seq(self, ambiguous_simple_type_specifier, ambiguous_nested_name_specifier):
    # type: (CxxParser, Any, Any) -> Any
    # Should this actually happen? seems like an incorrect merge graph allowing reduction on ::
    pass


@glrp.merge('decl-specifier-seq')
@cxx98_merge
def ambiguous_decl_specifier_seq_2(self, ambiguous_template_type_name, class_template_id):
    # type: (CxxParser, Any, Any) -> Any
    # Should this actually happen? seems like an incorrect merge graph allowing reduction on ::
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser