from .. import cl_ast


def p_struct_keyword(p):
    """
        struct_keyword : STRUCT
                       | UNION
                       | ENUM
                       | CLASS
    """
    p[0] = p[1]
    p.set_position(0, 1)


def p_struct_declaration(p):
    """
        struct_header : struct_keyword type_name
                      | struct_keyword object_name
    """
    template_stack = []
    for container in p.lexer.scopes[::-1]:
        if not isinstance(container, cl_ast.templates.Template):
            break
        template_stack.append(container)
    try:
        cl_ast.templates.resolve(p[2], template_stack)
    except cl_ast.templates.ResolutionError as e:
        p.lexer._error(str(e), e.position)
        raise SyntaxError()
    if p[2].qualified:
        if p[2].target:
            if p[2].target.get_token_type() == 'STRUCT_ID':
                p[0] = (p[2].target, None)
            elif p[2].target.get_token_type() == 'TEMPLATE_STRUCT_ID':
                # retrieve right specialization
                cls = p[2].target.specializations[0][1]
                p[0] = (cls, None)
            else:
                if len(p[2].name) > 1:
                    p.lexer._error('qualified name %s does not name a struct' % '::'.join(p[2].name),
                                   p[2].position)
                else:
                    p.lexer._error('name %s does not name a struct' % '::'.join(p[2].name),
                                   p[2].position)
                p.lexer._note('previously declared here', p[2].target.position)
                raise SyntaxError()
        else:
            if len(p[2].name) > 1:
                p.lexer._error('qualified name %s does not name a struct' % '::'.join(p[2].name),
                               p[2].position)
            else:
                p.lexer._error('name %s does not name a struct' % '::'.join(p[2].name),
                               p[2].position)
            raise SyntaxError()
    elif p[2].target:
        # optimistically use provided declaration, but if definition, it will be overriden
        if p[2].target.get_token_type() == 'STRUCT_ID':
            p[0] = (p[2].target, cl_ast.types.Struct(p.lexer.scopes[-1], p[2].position, p[1], p[2].name[0]))
        elif p[2].target and p[2].target.get_token_type() == 'TEMPLATE_STRUCT_ID':
            p[0] = (p[2].target.specializations[0][1], cl_ast.types.Struct(p.lexer.scopes[-1], p[2].position,
                                                                           p[1], p[2].name[0]))
        else:
            # Previously declared object is not a type
            p[0] = (None, cl_ast.types.Struct(p.lexer.scopes[-1], p[2].position, p[1], p[2].name[0]))
    else:
        # No previously delcared type, declare one here
        p[0] = (None, cl_ast.types.Struct(p.lexer.scopes[-1], p[2].position, p[1], p[2].name[0]))
    p.set_position_absolute(0, p[2].position)


def p_struct_push(p):
    """
        struct_push :
    """
    p[0] = p[-2][1] or p[-2][0]
    p[0].define(p[-1])
    if p[-2][1]:
        p.lexer.scopes[-1].add(p[0])
    p.lexer.push_scope(p[0])


def p_struct_pop(p):
    """
        struct_pop :
    """
    p.lexer.pop_scope()


def p_struct_parent_visibility(p):
    """
        struct_parent_visibility_opt : PUBLIC
                                     | PROTECTED
                                     | PRIVATE
                                     |
    """
    if len(p) > 1:
        p[0] = p[1]


def p_struct_parent(p):
    """
        struct_parent_opt : COLON struct_parent_visibility_opt type_name
                          |
    """
    if len(p) > 1:
        if p[3].dependent:
            p[0] = cl_ast.types.DependentTypeName(p.lexer.scopes[-1], p[3].position, p[3])
        else:
            p[0] = p[3].target


def p_struct_parent_error(p):
    """
        struct_parent_opt : COLON struct_parent_visibility_opt object_name
    """
    p.lexer._error('expected class name', p[3].position)


def p_struct_begin(p):
    """
        struct_begin : struct_header struct_parent_opt struct_push LBRACE
                     | struct_header error struct_push LBRACE
    """
    p[0] = p[3]
    p.set_position(0, 1)


def p_struct_definition(p):
    """
        struct_definition : struct_begin struct_declaration_list RBRACE struct_pop
    """
    p[0] = p[1]
    p.set_position(0, 1)


def p_struct_header_anonymous(p):
    """
        struct_header_anonymous : struct_keyword LBRACE
    """
    p[0] = cl_ast.types.Struct(p.lexer.scopes[-1], p.position(1), p[1], None)
    p[0].define(None)
    p.set_position(0, 1)
    p.lexer.scopes[-1].add(p[0])
    p.lexer.push_scope(p[0])


def p_struct_definition_anonymous(p):
    """
        struct_definition : struct_header_anonymous struct_declaration_list RBRACE struct_pop
    """
    p[0] = p[1]
    p.set_position(0, 1)


def p_type_struct_declaration(p):
    """
        typedecl : struct_header
    """
    p[0] = p[1][0] or p[1][1]
    p.set_position(0, 1)
    p.lexer.scopes[-1].add(p[0])


def p_type_struct_definition(p):
    """
        typedecl : struct_definition
    """
    p[0] = p[1]
    p.set_position(0, 1)


def p_struct_declaration_list(p):
    """
        struct_declaration_list : external_declaration struct_declaration_list
                                | struct_declaration struct_declaration_list
    """
    pass


def p_struct_declaration_list_end(p):
    """
        struct_declaration_list :
    """
    pass


def p_struct_declaration_scope(p):
    """
        struct_declaration : PUBLISHED COLON
                           | PUBLIC COLON
                           | PROTECTED COLON
                           | PRIVATE COLON
                           | FRIEND struct_header SEMI
    """
    pass

