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
from .....parse import cxx98
from ......ast.type import ElaboratedClassTypeSpecifier, ElaboratedEnumTypeSpecifier
from motor_typing import TYPE_CHECKING


# amendment: make elaborated-type-specifier look like class-head
#@glrp.rule('elaborated-type-specifier : class-key attribute-specifier-seq? "identifier"')
#@glrp.rule('elaborated-type-specifier : class-key attribute-specifier-seq? nested-name-specifier "identifier"')
#@glrp.rule('elaborated-type-specifier : class-key simple-template-id')
#@glrp.rule('elaborated-type-specifier : class-key nested-name-specifier template? simple-template-id')
@glrp.rule('elaborated-type-specifier : class-key attribute-specifier-seq? class-head-name [split:final_identifier]')
@cxx98
def elaborated_type_specifier_class(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ElaboratedClassTypeSpecifier(p[0], p[1], p[2])


@glrp.rule('elaborated-type-specifier : elaborated-enum-specifier')
@cxx98
def elaborated_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


# TODO: enum-key & attribute not allowed
#@glrp.rule('elaborated-enum-specifier : enum attribute-specifier-seq? identifier')
@glrp.rule('elaborated-enum-specifier : enum-key attribute-specifier-seq? enum-head-name')
@cxx98
def elaborated_enum_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ElaboratedEnumTypeSpecifier(p[0], p[1], p[2])


if TYPE_CHECKING:
    from typing import Any
    from .....parse import CxxParser