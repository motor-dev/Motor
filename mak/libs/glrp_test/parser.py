import glrp
from motor_typing import TYPE_CHECKING


class Parser1(glrp.Parser):

    class Lexer(glrp.Lexer):

        @glrp.token(r'a', 'a')
        @glrp.token(r'b', 'b')
        @glrp.token(r'c', 'c')
        @glrp.token(r'd', 'd')
        def tok(self, token):
            # type: (glrp.Token) -> glrp.Token
            return token

    @glrp.rule("prog : A prog")
    @glrp.rule("prog : A")
    def p_prog(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.merge('A')
    def merged_A(self, ab, b):
        # type: (Optional[int], Optional[int]) -> Optional[int]
        return ab

    @glrp.rule("A : a B c")
    @glrp.rule("A : a a B c")
    @glrp.rule("A : a a a B c")
    @glrp.rule("A : a B d")
    @glrp.rule("A : a a B d")
    #@glrp.rule("A : a a a B ")
    #@glrp.rule("A : B c")
    def p_A(self, p):
        # type: (glrp.Production) -> None
        pass

    #@glrp.rule("B [prec:right,0][split:aab]: a a b")
    @glrp.rule("B [prec:right,0][split:aab]: a a b")
    @glrp.rule("B [prec:right,0][split:ab]: a b")
    @glrp.rule("B [prec:right,0][split:b]: b")
    def p_B(self, p):
        # type: (glrp.Production) -> None
        pass

    def __init__(self):
        # type: ()->None
        self.lexer = self.__class__.Lexer()
        glrp.Parser.__init__(self, self.lexer, 'prog', '.', '.', mode=1)


class Parser2(glrp.Parser):

    class Lexer(glrp.Lexer):

        @glrp.token(r'identifier', 'identifier')
        @glrp.token(r'typename', 'typename')
        @glrp.token(r';', ';')
        @glrp.token(r'\(', '(')
        @glrp.token(r'\)', ')')
        @glrp.token(r'\+', '+')
        @glrp.token(r'\=', '=')
        def tok(self, token):
            # type: (glrp.Token) -> glrp.Token
            return token

    @glrp.rule("prog :")
    @glrp.rule("prog : prog stmt")
    def p_prog(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("stmt : expr ';'")
    @glrp.rule("stmt : decl")
    def p_stmt(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("expr : 'identifier'")
    @glrp.rule("expr : 'typename' '(' expr ')'")
    @glrp.rule("expr : expr '+' expr")
    @glrp.rule("expr : expr '=' expr")
    def p_expr(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("decl : 'typename' declarator")
    @glrp.rule("decl : 'typename' declarator '=' expr")
    def p_decl(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("declarator : 'identifier'")
    @glrp.rule("declarator : '(' declarator ')'")
    def p_declarator(self, p):
        # type: (glrp.Production) -> None
        pass

    def __init__(self):
        # type: ()->None
        self.lexer = self.__class__.Lexer()
        glrp.Parser.__init__(self, self.lexer, 'prog', '.', '.', mode=1)


class Parser3(glrp.Parser):

    class Lexer(glrp.Lexer):

        @glrp.token(r'if', 'if')
        @glrp.token(r'else', 'else')
        @glrp.token(r'\(', '(')
        @glrp.token(r'\)', ')')
        @glrp.token(r'\{', '{')
        @glrp.token(r'\}', '}')
        @glrp.token(r'\;', ';')
        @glrp.token(r'identifier', 'identifier')
        def tok(self, token):
            # type: (glrp.Token) -> glrp.Token
            return token

    @glrp.rule("prog : stmt")
    def p_prog(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("stmt : expr ';'")
    @glrp.rule("stmt : if_stmt")
    def p_stmt(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("expr : 'identifier'")
    def p_expr(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("if_stmt : 'if' '(' expr ')' stmt")
    @glrp.rule("if_stmt : 'if' '(' expr ')' stmt 'else' stmt")
    def p_if_stmt(self, p):
        # type: (glrp.Production) -> None
        pass

    def __init__(self):
        # type: ()->None
        self.lexer = self.__class__.Lexer()
        glrp.Parser.__init__(self, self.lexer, 'prog', '.', '.', mode=1)


class Parser4(glrp.Parser):

    class Lexer(glrp.Lexer):

        @glrp.token(r'id', 'id')
        @glrp.token(r'\,', ',')
        def tok(self, token):
            # type: (glrp.Token) -> glrp.Token
            return token

    @glrp.rule("s : a id")
    def p_s(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("a : expr")
    def p_a(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("expr : ")
    @glrp.rule("expr : expr 'id' ','")
    def p_expr(self, p):
        # type: (glrp.Production) -> None
        pass

    def __init__(self):
        # type: ()->None
        self.lexer = self.__class__.Lexer()
        glrp.Parser.__init__(self, self.lexer, 's', '.', '.', mode=1)


class Parser5(glrp.Parser):

    class Lexer(glrp.Lexer):

        @glrp.token(r'id', 'identifier')
        @glrp.token('::')
        @glrp.token(',')
        @glrp.token(';')
        @glrp.token('-')
        @glrp.token(r'\$', '$')
        @glrp.token('%')
        @glrp.token('template')
        def tok(self, token):
            # type: (glrp.Token) -> glrp.Token
            return token

    @glrp.rule("prog : prog comma_opt percent_opt dollar_opt id_expression")
    @glrp.rule("prog : id_expression")
    def prog(self, p):
        pass

    @glrp.rule("id_expression : qualified_id")
    @glrp.rule("id_expression : unqualified_id")
    def id_expression(self, p):
        pass

    @glrp.rule("unqualified_id : template_opt identifier")
    def unqualified_id(self, p):
        pass

    @glrp.rule("template_opt : template")
    @glrp.rule("template_opt : ")
    def template_opt(self, p):
        pass

    @glrp.rule("qualified_id : nested_name_specifier unqualified_id")
    @glrp.rule("qualified_id : '::' nested_name_specifier unqualified_id")
    def qualified_id(self, p):
        pass

    @glrp.rule("sign : dollar_opt percentw??_opt")
    def sign(self, p):
        pass

    @glrp.rule("dollar_opt :")
    @glrp.rule("dollar_opt : '$'")
    def dollar_opt(self, p):
        pass

    @glrp.rule("percent_opt :")
    @glrp.rule("percent_opt : '%'")
    def percent_opt(self, p):
        pass

    @glrp.rule("comma_opt : ','")
    @glrp.rule("comma_opt : semi_opt dash_opt")
    def comma_opt(self, p):
        pass

    @glrp.rule("semi_opt : ';'")
    @glrp.rule("semi_opt :")
    def semi_opt(self, p):
        pass

    @glrp.rule("dash_opt : '-'")
    @glrp.rule("dash_opt :")
    def dash_opt(self, p):
        pass

    @glrp.rule("nested_name_specifier : template_opt identifier [split:scope]'::'")
    def nested_name_specifier(self, p):
        pass

    def __init__(self):
        # type: ()->None
        self.lexer = self.__class__.Lexer()
        glrp.Parser.__init__(self, self.lexer, 'prog', '.', '.', mode=1)


class Parser6(glrp.Parser):

    class Lexer(glrp.Lexer):

        @glrp.token(r'identifier', 'identifier')
        @glrp.token(r';', ';')
        @glrp.token(r'\[', '[')
        @glrp.token(r'\]', ']')
        def tok(self, token):
            # type: (glrp.Token) -> glrp.Token
            return token

    @glrp.rule("prog :")
    @glrp.rule("prog : prog stmt")
    def p_prog(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("stmt : expr ';'")
    @glrp.rule("stmt : decl")
    def p_stmt(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("expr : 'identifier'[split:expr]")
    @glrp.rule("expr : 'expr' [split:array]'[' expr? ']'")
    @glrp.rule("expr : 'expr' annotation")
    def p_expr(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("decl : 'identifier' [split:decl]';'")
    def p_decl(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("annotation : [split:annotation]'[' '[' 'identifier' ']' ']'")
    def p_annotation(self, p):
        # type: (glrp.Production) -> None
        pass

    def __init__(self):
        # type: ()->None
        self.lexer = self.__class__.Lexer()
        glrp.Parser.__init__(self, self.lexer, 'prog', '.', '.', mode=1)


class Parser7(glrp.Parser):

    class Lexer(glrp.Lexer):

        @glrp.token(r'identifier', 'identifier')
        @glrp.token(r'\(', '(')
        @glrp.token(r'\)', ')')
        def tok(self, token):
            # type: (glrp.Token) -> glrp.Token
            return token

    @glrp.rule("prog : type-id declarator")
    @glrp.rule("prog : type-id abstract-declarator")
    def p_prog(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.merge('type-id')
    def merge_type_id(self, end_type_id, continue_type_id):
        print('merge')
        return end_type_id

    @glrp.rule('type-id : type-specifier-seq [split:end_type_id]')
    def p_type_id(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("type-specifier-seq : type-specifier-seq type-specifier")
    @glrp.rule("type-specifier-seq : type-specifier")
    def p_type_specifier_seq(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("type-specifier : [split:continue_type_id] identifier")
    def p_type_specifier(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("declarator: identifier")
    @glrp.rule("declarator: '(' declarator ')'")
    def p_declarator(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule("abstract-declarator : ")
    @glrp.rule("abstract-declarator : '(' ')'")
    def p_abstract_declarator(self, p):
        # type: (glrp.Production) -> None
        pass

    def __init__(self):
        # type: ()->None
        self.lexer = self.__class__.Lexer()
        glrp.Parser.__init__(self, self.lexer, 'prog', '.', '.', mode=1)


class Parser8(glrp.Parser):

    class Lexer(glrp.Lexer):

        @glrp.token(r'identifier')
        @glrp.token(r'::')
        @glrp.token(r'<')
        @glrp.token(r'>')
        def tok(self, token):
            # type: (glrp.Token) -> glrp.Token
            return token

    @glrp.rule("prog : prog qualified-name")
    @glrp.rule("prog : ")
    def p_prog(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule('qualified-name : "::" name-qualifier "::" concept-name "<" ">"')
    def p_qname(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule('name-qualifier : namespace-name "<" ">"')
    @glrp.rule('name-qualifier : name-qualifier "::" namespace-name "<" ">"')
    def p_name_qualifier(self, p):
        # type: (glrp.Production) -> None
        pass

    @glrp.rule('namespace-name[split:namespace_name] : identifier')
    @glrp.rule('concept-name[split:concept_name] : identifier')
    def p_name(self, p):
        # type: (glrp.Production) -> None
        pass

    def __init__(self):
        # type: ()->None
        self.lexer = self.__class__.Lexer()
        glrp.Parser.__init__(self, self.lexer, 'prog', '.', '.', mode=1)


if TYPE_CHECKING:
    from typing import Optional