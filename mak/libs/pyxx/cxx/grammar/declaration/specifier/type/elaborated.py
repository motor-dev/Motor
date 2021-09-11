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


# TODO: attribute-specifier-seq? ->  ♦
@glrp.rule(
    'elaborated-type-specifier[split] : attribute-specifier-seq? class-key attribute-specifier-seq? "identifier"'
)
@glrp.rule(
    'elaborated-type-specifier[split] : attribute-specifier-seq? class-key attribute-specifier-seq? nested-name-specifier "template"? "identifier"'
)
@glrp.rule(
    'elaborated-type-specifier[split] : attribute-specifier-seq? class-key attribute-specifier-seq? simple-template-id'
)
@glrp.rule(
    'elaborated-type-specifier[split] : attribute-specifier-seq? class-key attribute-specifier-seq? nested-name-specifier "template"?  simple-template-id'
)
@glrp.rule('elaborated-type-specifier : elaborated-enum-specifier')
@cxx98
def elaborated_type_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


# TODO: enum-key & attribute not allowed
@glrp.rule('elaborated-enum-specifier[split] : enum-key attribute-specifier-seq? "identifier"')
@glrp.rule(
    'elaborated-enum-specifier[split] : enum-key attribute-specifier-seq? nested-name-specifier template? "identifier"'
)
@cxx98
def elaborated_enum_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from .....parser import CxxParser