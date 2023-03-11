from ..tree import Variable


def p_variable_array(p):
    """
        variable_array : LEFT_BRACKET value RIGHT_BRACKET
    """
    p[0] = '%s%s%s' % (p[1], p[2], p[3])


def p_variable_array_list_opt(p):
    """
        variable_array_list_opt : variable_array variable_array_list_opt
                                |
    """
    if len(p) > 1:
        p[0] = '%s%s' % (p[1], p[2])
    else:
        p[0] = ''


def p_variable_initial_value_opt(p):
    """
        variable_initial_value_opt : ASSIGN value
                                   | ASSIGN LEFT_BRACE RIGHT_BRACE
                                   | ASSIGN LEFT_BRACE value value_list_opt RIGHT_BRACE
                                   |
    """


def p_variable_value_list_opt(p):
    """
        value_list_opt : COMMA value value_list_opt
                       |
    """


def p_variable_decl(p):
    """
        variable_decl : attribute_left_list method_return_type ID variable_array_list_opt variable_initial_value_opt
    """
    p[0] = Variable(p[3], p[2] + p[4])
    p[0].add_attributes(p[1][0])
    p[0].add_tags(p[1][1])


def p_variable_decl_method(p):
    """
        variable_decl : attribute_left_list method_return_type LEFT_PARENTHESIS MULTIPLY ID RIGHT_PARENTHESIS LEFT_PARENTHESIS skip_parameters RIGHT_PARENTHESIS
    """


def p_variable_expr(p):
    """
        expr : variable_decl SEMICOLON
    """
    p.parser.stack[-1].add_property(p[1])
