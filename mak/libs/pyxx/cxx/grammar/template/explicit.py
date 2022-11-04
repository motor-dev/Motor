"""
explicit-specialization:
    template < > declaration

explicit-instantiation:
    extern? template declaration
"""

import glrp
from ...parser import cxx98
from motor_typing import TYPE_CHECKING


# amendment: @glrp.rule('explicit-specialization : "template" "<" ">" declaration')
@glrp.rule('explicit-specialization : attribute-specifier-seq? begin-declaration "template" "<" "#>" declaration')
@glrp.rule(
    'explicit-specialization : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" "template" "<" "#>" declaration'
)
@cxx98
def explicit_specialization(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    # TODO: extern? not allowed
    # TODO: attribute-specifier-seq? not allowed
    pass


# amendment: @glrp.rule('explicit-instantiation : "extern"? "template" declaration')
@glrp.rule('explicit-instantiation : attribute-specifier-seq? begin-declaration "template" declaration')
@glrp.rule(
    'explicit-instantiation : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" "template" declaration'
)
@cxx98
def explicit_instantiation(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    # TODO: attribute-specifier-seq? not allowed
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser