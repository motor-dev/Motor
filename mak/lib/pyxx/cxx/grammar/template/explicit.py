"""
explicit-specialization:
    template < > declaration

explicit-instantiation:
    extern? template declaration
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx98
from ....ast.declarations import ExplicitSpecialization, ExplicitInstantiation


# amendment: @glrp.rule('explicit-specialization : "template" "<" ">" declaration')
@glrp.rule('explicit-specialization : attribute-specifier-seq? begin-declaration "template" "<" "#>" declaration')
@cxx98
def explicit_specialization(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: extern? not allowed
    # TODO: attribute-specifier-seq? not allowed
    return ExplicitSpecialization(p[5])


@glrp.rule(
    'explicit-specialization : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" "template" "<" "#>" declaration'
)
@cxx98
def explicit_specialization_extern(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: extern? not allowed
    # TODO: attribute-specifier-seq? not allowed
    return ExplicitSpecialization(p[7])


# amendment: @glrp.rule('explicit-instantiation : "extern"? "template" declaration')
@glrp.rule('explicit-instantiation : attribute-specifier-seq? begin-declaration "template" declaration')
@cxx98
def explicit_instantiation(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return ExplicitInstantiation(p[3], False)


@glrp.rule(
    'explicit-instantiation : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" "template" declaration'
)
@cxx98
def explicit_instantiation_extern(self: CxxParser, p: glrp.Production) -> Any:
    # TODO: attribute-specifier-seq? not allowed
    return ExplicitInstantiation(p[5], True)
