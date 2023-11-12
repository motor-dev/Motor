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
from typing import Any
from ...parse import CxxParser, cxx98, cxx11
from ....ast.klass import ClassSpecifier
from ....ast.type import ErrorTypeSpecifier
from ....ast.reference import TemplateId, Id, Reference, TemplateSpecifierId, _Id
from . import member
from . import initializer
from . import derived
from . import conversion


# @glrp.rule('class-name : "identifier"')
# @glrp.rule('class-name : simple-template-id')
# @cxx98
# def class_name(self: CxxParser, p: glrp.Production) -> Any:
#    # type: (CxxParser, glrp.Production) -> Any
#    pass


@glrp.rule('class-specifier : class-head "{" member-specification? "}"')
@cxx98
def class_specifier(self: CxxParser, p: glrp.Production) -> Any:
    if p[0][1] is not None:
        position = p[0][0]
        if p[0][3] is not None:
            position = position[0], p[0][3].position[1]
        return ClassSpecifier(position, p[0][1], p[0][2], p[0][3], p[0][4], p[0][5], p[2])
    else:
        return ErrorTypeSpecifier(p[0][0])


@glrp.rule('class-head : class-key attribute-specifier-seq? class-head-name base-clause?')
@cxx98
def class_head(self: CxxParser, p: glrp.Production) -> Any:
    return (p[0][0], p[0][1], p[1], p[2], False, p[3])


@glrp.rule('class-head : class-key attribute-specifier-seq? base-clause?')
@cxx98
def class_head_unnamed(self: CxxParser, p: glrp.Production) -> Any:
    return (p[0][0], p[0][1], p[1], None, False, p[2])


@glrp.rule('class-head : class-key attribute-specifier-seq? class-head-name class-virt-specifier base-clause?')
@cxx11
def class_head_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return (p[0][0], p[0][1], p[1], p[2], p[3], p[4])


@glrp.rule('class-head : class-key "#error"')
@cxx98
def class_head_error(self: CxxParser, p: glrp.Production) -> Any:
    return p[0][0], None


# @glrp.rule('class-head-name : class-name')
@glrp.rule('class-head-name : "identifier" [split:id_nontemplate]')
@cxx98
def class_head_name(self: CxxParser, p: glrp.Production) -> Any:
    return Reference([Id(p[0].position, p[0].value)])


@glrp.rule('class-head-name : template-name "<" template-argument-list? "#>"')
@cxx98
def class_head_name_template(self: CxxParser, p: glrp.Production) -> Any:
    return Reference([TemplateId(p[3].position[1], p[0], p[2])])


@glrp.rule('class-head-name : nested-name-specifier template? "identifier" [split:id_nontemplate]')
@cxx98
def class_head_name_nested(self: CxxParser, p: glrp.Production) -> Any:
    id = Id(p[2].position, p[2].value)  # type: _Id
    if p[1]:
        id = TemplateSpecifierId(p[1].position, id)
    return Reference(p[0] + [id])


@glrp.rule('class-head-name : nested-name-specifier template? template-name "<" template-argument-list? "#>"')
@cxx98
def class_head_name_nested_template(self: CxxParser, p: glrp.Production) -> Any:
    id = TemplateId(p[5].position[1], p[2], p[4])  # type: _Id
    if p[1]:
        id = TemplateSpecifierId(p[1].position, id)
    return Reference(p[0] + [id])


@glrp.rule('class-virt-specifier : [split:final_keyword]"final"')
@cxx11
def class_virt_specifier_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return True


@glrp.rule('class-key : "class"')
@glrp.rule('class-key : "struct"')
@glrp.rule('class-key : "union"')
@cxx98
def class_key(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].position, p[0].text()
