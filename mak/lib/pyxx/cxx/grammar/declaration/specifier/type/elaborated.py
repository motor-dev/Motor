"""
elaborated-type-specifier:
    class-key attribute-specifier-seq? nested-name-specifier? identifier
    class-key simple-template-id
    class-key nested-name-specifier template? simple-template-id
    elaborated-enum-specifier

elaborated-enum-specifier:
    enum nested-name-specifier? identifier
"""

import glrp
from typing import Any, Dict, Tuple
from .....parse import CxxParser, cxx98
from ......ast.type import ElaboratedClassTypeSpecifier, ElaboratedEnumTypeSpecifier

from ......messages import error, Logger


@error
def invalid_attribute_elaborated_enum_specifier(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """an attribute cannot appear in an elaborated enum specifier"""
    return locals()


# amendment: make elaborated-type-specifier look like class-head
# @glrp.rule('elaborated-type-specifier : class-key attribute-specifier-seq? "identifier"')
# @glrp.rule('elaborated-type-specifier : class-key attribute-specifier-seq? nested-name-specifier "identifier"')
# @glrp.rule('elaborated-type-specifier : class-key simple-template-id')
# @glrp.rule('elaborated-type-specifier : class-key nested-name-specifier template? simple-template-id')
@glrp.rule('elaborated-type-specifier : class-key attribute-specifier-seq? class-head-name [split:final_identifier]')
@cxx98
def elaborated_type_specifier_class(self: CxxParser, p: glrp.Production) -> Any:
    return ElaboratedClassTypeSpecifier(p[0], p[1], p[2])


@glrp.rule('elaborated-type-specifier : elaborated-enum-specifier')
@cxx98
def elaborated_type_specifier(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


# TODO: enum-key not allowed
# @glrp.rule('elaborated-enum-specifier : enum attribute-specifier-seq? identifier')
@glrp.rule('elaborated-enum-specifier : enum-key attribute-specifier-seq? enum-head-name')
@cxx98
def elaborated_enum_specifier(self: CxxParser, p: glrp.Production) -> Any:
    if p[1]:
        invalid_attribute_elaborated_enum_specifier(self.logger, p[1][0].position)
    position, is_scoped = p[0]
    position = (position[0], p[2].position[1])
    return ElaboratedEnumTypeSpecifier(position, is_scoped, p[2])
