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
from .....parser import cxx98
from motor_typing import TYPE_CHECKING


# amendment: make elaborated-type-specifier look like class-head
#@glrp.rule('elaborated-type-specifier : class-key attribute-specifier-seq? nested-name-specifier? identifier')
#@glrp.rule('elaborated-type-specifier : class-key simple-template-id')
#@glrp.rule('elaborated-type-specifier : class-key nested-name-specifier template? simple-template-id')
@glrp.rule('elaborated-type-specifier : class-key attribute-specifier-seq? class-head-name')
@glrp.rule('elaborated-type-specifier : elaborated-enum-specifier')
@cxx98
def elaborated_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


# TODO: enum-key & attribute not allowed
@glrp.rule('elaborated-enum-specifier : enum-key attribute-specifier-seq? enum-head-name')
#@glrp.rule(
#    'elaborated-enum-specifier : enum-key attribute-specifier-seq? nested-name-specifier template? enum-head-name'
#)
@cxx98
def elaborated_enum_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser