"""
concept-definition:
    concept concept-name attribute-specifier-seq? = constraint-expression ;

concept-name:
    identifier
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx20
from ....ast.declarations import ConceptDefinition, ErrorDeclaration


@glrp.rule('concept-definition : "concept" "identifier" attribute-specifier-seq? "=" constraint-expression ";"')
@cxx20
def concept_definition_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ConceptDefinition(p[2], p[1].text(), p[4])


@glrp.rule('concept-definition : "concept" "#error" "=" constraint-expression ";"')
@glrp.rule('concept-definition : "concept" "#error" ";"')
@cxx20
def concept_definition_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorDeclaration()
