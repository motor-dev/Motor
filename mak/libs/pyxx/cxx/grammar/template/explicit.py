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
@glrp.rule(
    'explicit-specialization : attribute-specifier-seq? "extern"? "template" [action:split_rightshift]"<" ">" declaration'
)
@cxx98
def explicit_specialization(self, p):
    # type: (CxxParser, glrp.Production) -> None
    # TODO: extern? not allowed
    # TODO: attribute-specifier-seq? not allowed
    pass


# amendment: @glrp.rule('explicit-instantiation : "extern"? "template" declaration')
@glrp.rule('explicit-instantiation : attribute-specifier-seq? "extern"? "template" declaration')
@cxx98
def explicit_instantiation(self, p):
    # type: (CxxParser, glrp.Production) -> None
    # TODO: attribute-specifier-seq? not allowed
    pass


@glrp.rule('"extern"? : "extern"')
@glrp.rule('"extern"? : ')
@cxx98
def extern_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser