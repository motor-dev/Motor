"""
explicit-specialization:
    template < > declaration

explicit-instantiation:
    extern? template declaration
"""

import glrp
from typing import Any, Dict, Tuple
from ...parse import CxxParser, cxx98
from ....ast.declarations import ExplicitSpecialization, ExplicitInstantiation
from ....messages import error, Logger


@error
def invalid_attribute_explicit_specialization(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """an attribute cannot appear before an explicit specialization"""
    return locals()


@error
def invalid_attribute_explicit_instantiation(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """an attribute cannot appear before an explicit instantiation"""
    return locals()


@error
def explicit_specialization_multiple_entities(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """an explicit specialization can only declare a single entity"""
    return locals()


@error
def explicit_instantiation_multiple_entities(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """an explicit instantiation can only declare a single entity"""
    return locals()


# amendment: @glrp.rule('explicit-specialization : "template" "<" ">" declaration')
@glrp.rule('explicit-specialization : attribute-specifier-seq? begin-declaration "template" "<" "#>" declaration')
@cxx98
def explicit_specialization(self: CxxParser, p: glrp.Production) -> Any:
    for attribute in p[0]:
        if not attribute.is_extended():
            invalid_attribute_explicit_specialization(self.logger, attribute.position)
            break
    if p[5].declared_entity_count() > 1:
        explicit_specialization_multiple_entities(self.logger, p[5].declared_entity_position(1))
    p[5].add_attributes(p[0])
    return ExplicitSpecialization(p[5])


# amendment: @glrp.rule('explicit-instantiation : "extern"? "template" declaration')
@glrp.rule('explicit-instantiation : attribute-specifier-seq? begin-declaration "template" declaration')
@cxx98
def explicit_instantiation(self: CxxParser, p: glrp.Production) -> Any:
    if p[0]:
        invalid_attribute_explicit_instantiation(self.logger, p[0][0].position)
    if p[3].declared_entity_count() > 1:
        explicit_instantiation_multiple_entities(self.logger, p[3].declared_entity_position(1))
    return ExplicitInstantiation(p[3], False)


@glrp.rule(
    'explicit-instantiation : attribute-specifier-seq? begin-declaration decl-specifier-seq-continue "extern" "template" declaration'
)
@cxx98
def explicit_instantiation_extern(self: CxxParser, p: glrp.Production) -> Any:
    if p[0]:
        invalid_attribute_explicit_instantiation(self.logger, p[0][0].position)
    return ExplicitInstantiation(p[5], True)
