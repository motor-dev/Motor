"""
concept-definition:
    concept concept-name = constraint-expression ;

concept-name:
    identifier
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx20
from ....ast.declarations import ConceptDefinition, ErrorDeclaration


@glrp.rule('concept-definition : "concept" "identifier" "=" constraint-expression ";"')
@cxx20
def concept_definition_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ConceptDefinition(p[1].text(), p[3])


@glrp.rule('concept-definition : "concept" "#error" "=" constraint-expression ";"')
@glrp.rule('concept-definition : "concept" "#error" ";"')
@cxx20
def concept_definition_errorcxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorDeclaration()


#@glrp.rule('concept-name : "identifier"')
#@cxx20
#def concept_name_cxx20(self: CxxParser, p: glrp.Production) -> Any:
#    # type: (CxxParser, glrp.Production) -> Any
#    pass
