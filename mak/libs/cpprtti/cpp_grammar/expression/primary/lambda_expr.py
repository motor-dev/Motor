"""
lambda-expression: 	 
      lambda-introducer lambda-declaratoropt compound-statement     C++0x
lambda-introducer: 	 
      [ lambda-captureopt ]     C++0x
lambda-capture: 	 
      capture-default     C++0x
      capture-list     C++0x
      capture-default , capture-list     C++0x
capture-default: 	 
      &     C++0x
      =     C++0x
capture-list: 	 
      capture ...opt     C++0x
      capture-list , capture ...opt     C++0x
capture: 	 
      identifier     C++0x
      & identifier     C++0x
      this     C++0x
lambda-declarator: 	 
      ( parameter-declaration-clause ) mutableopt exception-specificationopt attribute-specifier-seqopt trailing-return-typeopt     C++0x
"""

from be_typing import TYPE_CHECKING


def p_lambda_expression(p):
    # type: (YaccProduction) -> None
    """
        lambda-expression : lambda-introducer lambda-declarator? compound-statement
    """


def p_lambda_introducer(p):
    # type: (YaccProduction) -> None
    """
        lambda-introducer : LBRACKET lambda-capture? RBRACKET
    """


def p_lambda_capture(p):
    # type: (YaccProduction) -> None
    """
        lambda-capture : capture-default
                       | capture-list
                       | capture-default COMMA capture-list
    """


def p_capture_default(p):
    # type: (YaccProduction) -> None
    """
        capture-default : OP_AND
                        | OP_EQUALS
    """


def p_capture_list(p):
    # type: (YaccProduction) -> None
    """
        capture-list : capture ELLIPSIS?
                     | capture-list COMMA capture ELLIPSIS?
    """


def p_capture(p):
    # type: (YaccProduction) -> None
    """
        capture : IDENTIFIER
                | OP_AND IDENTIFIER
                | KW_THIS
    """


def p_lambda_declarator(p):
    # type: (YaccProduction) -> None
    """
        lambda-declarator : LPAREN parameter-declaration-clause RPAREN KW_MUTABLE? exception-specification? attribute-specifier-seq? trailing-return-type?
    """


if TYPE_CHECKING:
    from ply.yacc import YaccProduction