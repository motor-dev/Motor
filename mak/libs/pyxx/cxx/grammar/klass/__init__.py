"""
class-name:
    identifier
    simple-template-id

class-specifier:
    class-head { member-specification? }

class-head:
    class-key attribute-specifier-seq? class-head-name class-virt-specifier? base-clause?
    class-key attribute-specifier-seq? base-clause?

class-head-name:
    nested-name-specifier? class-name

class-virt-specifier:
    final

class-key:
    class
    struct
    union
"""

import glrp
from ...parser import cxx98, cxx11
from motor_typing import TYPE_CHECKING
from . import member
from . import initializer
from . import derived
from . import conversion

#@glrp.rule('class-name : "identifier"')
#@glrp.rule('class-name : simple-template-id')
#@cxx98
#def class_name(self, p):
#    # type: (CxxParser, glrp.Production) -> Any
#    pass


@glrp.rule('class-specifier : class-head "{" member-specification? "}"')
@cxx98
def class_specifier(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('class-head : class-key attribute-specifier-seq? class-head-name base-clause?')
@glrp.rule('class-head : class-key attribute-specifier-seq? base-clause?')
@cxx98
def class_head(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('class-head : class-key attribute-specifier-seq? class-head-name class-virt-specifier base-clause?')
@cxx11
def class_head_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


# TODO: template? not allowed
#@glrp.rule('class-head-name : class-name')
@glrp.rule('class-head-name : "identifier" [split:id_nontemplate]')
@glrp.rule('class-head-name : template-name [action:begin_template_list]"<" template-argument-list? "%>"')
@glrp.rule('class-head-name : nested-name-specifier template? "identifier" [split:id_nontemplate]')
@glrp.rule(
    'class-head-name : nested-name-specifier template? template-name [action:begin_template_list]"<" template-argument-list? "%>"'
)
@cxx98
def class_head_name(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('class-virt-specifier : "final"')
@cxx11
def class_virt_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('class-key : "class"')
@glrp.rule('class-key : "struct"')
@glrp.rule('class-key : "union"')
@cxx98
def class_key(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser