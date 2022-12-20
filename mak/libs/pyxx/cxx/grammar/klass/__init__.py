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
from ...parse import cxx98, cxx11
from ....ast.klass import ClassSpecifier
from ....ast.reference import TemplateId, Id, Reference
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
    return ClassSpecifier(p[0][0], p[0][1], p[0][2], p[0][3], p[0][4], p[2])


@glrp.rule('class-head : class-key attribute-specifier-seq? class-head-name base-clause?')
@cxx98
def class_head(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (p[0], p[1], p[2], False, p[3])


@glrp.rule('class-head : class-key attribute-specifier-seq? base-clause?')
@cxx98
def class_head_unnamed(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (p[0], p[1], None, False, p[2])


@glrp.rule('class-head : class-key attribute-specifier-seq? class-head-name class-virt-specifier base-clause?')
@cxx11
def class_head_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return (p[0], p[1], p[2], p[3], p[4])


#@glrp.rule('class-head-name : class-name')
@glrp.rule('class-head-name : "identifier" [split:id_nontemplate]')
@cxx98
def class_head_name(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Reference([(False, Id(p[0].value))])


@glrp.rule('class-head-name : template-name "<" template-argument-list? "#>"')
@cxx98
def class_head_name_template(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Reference([(False, TemplateId(p[0], p[2]))])


@glrp.rule('class-head-name : nested-name-specifier template? "identifier" [split:id_nontemplate]')
@cxx98
def class_head_name_nested(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Reference(p[0] + [(p[1], Id(p[2].value))])


@glrp.rule('class-head-name : nested-name-specifier template? template-name "<" template-argument-list? "#>"')
@cxx98
def class_head_name_nested_template(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return Reference(p[0] + [(p[1], TemplateId(p[2], p[4]))])


@glrp.rule('class-virt-specifier : [split:final_keyword]"final"')
@cxx11
def class_virt_specifier_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return True


@glrp.rule('class-key : "class"')
@glrp.rule('class-key : "struct"')
@glrp.rule('class-key : "union"')
@cxx98
def class_key(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0].text()


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser