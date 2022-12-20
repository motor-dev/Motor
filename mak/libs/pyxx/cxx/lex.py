import glrp
import decimal
from motor_typing import TYPE_CHECKING

decimal.getcontext().prec = 24

_identifier = r'[a-zA-Z_][a-zA-Z_0-9]*'

_nonzero_digit = '[1-9]'
_digit = '[0-9]'
_octal_digit = '[0-7]'
_hexadecimal_digit = '[0-9a-fA-F]'
_hexadecimal_prefix = '(?:0[xX])'

_decimal_constant = '(?:%(_nonzero_digit)s%(_digit)s*)' % locals()
_octal_constant = '(?:0%(_octal_digit)s*)' % locals()
_hexadecimal_constant = '(?:%(_hexadecimal_prefix)s%(_hexadecimal_digit)s+)' % locals()
_binary_constant = '(?:0[bB][01]+)'
_unsigned_suffix = '[uU]'
_long_suffix = '[lL]'
_long_long_suffix = '(?:(?:ll)|(?:LL))'
_integer_suffix = '(?:(?:%(_unsigned_suffix)s%(_long_suffix)s?)|(?:%(_unsigned_suffix)s%(_long_long_suffix)s)|(?:%(_long_suffix)s%(_unsigned_suffix)s?)|(?:%(_long_long_suffix)s%(_unsigned_suffix)s?))' % locals(
)
_integer_literal = '(?:%(_decimal_constant)s|%(_hexadecimal_constant)s|%(_binary_constant)s|%(_octal_constant)s)%(_integer_suffix)s?' % locals(
)

_floating_suffix = '(?:f|l|F|L|(?:df)|(?:dd)|(?:dl)|(?:DF)|(?:DD)|(?:DL))'

_fractional_constant = r'(?:(?:[0-9]*\.[0-9]+)|(?:[0-9]+\.))'
_exponent_part = r'(?:[eE][+\-]?[0-9]+)'
_decimal_floating_constant = '(?:(?:%(_fractional_constant)s%(_exponent_part)s?%(_floating_suffix)s?)|(?:[0-9]+%(_exponent_part)s%(_floating_suffix)s?))' % locals(
)

_hexadecimal_fractional_constant = '(?:(?:%(_hexadecimal_digit)s*\\.%(_hexadecimal_digit)s+)|(?:%(_hexadecimal_digit)s+\\.))' % locals(
)
_binary_exponent_part = r'(?:[pP][+\-]?[0-9]+)'
_hexadecimal_floating_constant = '(?:(?:%(_hexadecimal_prefix)s%(_hexadecimal_fractional_constant)s%(_binary_exponent_part)s%(_floating_suffix)s?)|(?:%(_hexadecimal_prefix)s%(_hexadecimal_digit)s+%(_binary_exponent_part)s%(_floating_suffix)s))' % locals(
)

_floating_literal = '%(_decimal_floating_constant)s|%(_hexadecimal_floating_constant)s' % locals()

_encoding_prefix = '(?:(?:u8?)|U|L)'
_simple_escape_sequence = r'(?:\\[\'"\?\\abfnrtv])'
_octal_escape_sequence = '(?:\\\\%(_octal_digit)s%(_octal_digit)s?%(_octal_digit)s?)' % locals()
_hexadecimal_escape_sequence = '(?:\\\\x%(_hexadecimal_digit)s+)' % locals()
_hexadecimal_quad = '%(_hexadecimal_digit)s%(_hexadecimal_digit)s%(_hexadecimal_digit)s%(_hexadecimal_digit)s' % locals(
)
_universal_character_name = '(?:(?:\\\\u%(_hexadecimal_quad)s)|(?:\\\\U%(_hexadecimal_quad)s%(_hexadecimal_quad)s))' % locals(
)
_escape_sequence = '(?:%(_simple_escape_sequence)s|%(_octal_escape_sequence)s|%(_hexadecimal_escape_sequence)s|%(_universal_character_name)s)' % locals(
)
_c_char = '(?:[^\\\'\\\\\\n]|%(_escape_sequence)s)' % locals()
_c_char_sequence = '%(_c_char)s+' % locals()
_character_literal = '%(_encoding_prefix)s?\\\'%(_c_char_sequence)s\\\'' % locals()

_s_char = '(?:[^"\\n]|%(_escape_sequence)s)' % locals()
_string_literal = '(?:%(_encoding_prefix)s?"%(_s_char)s*")' % locals()

_user_defined_integer_literal = '(?:%(_decimal_constant)s%(_identifier)s)|(?:%(_hexadecimal_constant)s%(_identifier)s)|(?:%(_octal_constant)s%(_identifier)s)|(?:%(_binary_constant)s%(_identifier)s)' % locals(
)

_user_defined_floating_literal = '(?:%(_fractional_constant)s%(_exponent_part)s?%(_identifier)s)|(?:[0-9]+%(_exponent_part)s%(_identifier)s)|(?:%(_hexadecimal_prefix)s%(_hexadecimal_fractional_constant)s%(_binary_exponent_part)s%(_identifier)s)|(?:%(_hexadecimal_prefix)s%(_hexadecimal_digit)s+%(_binary_exponent_part)s%(_identifier)s)' % locals(
)

_user_defined_string_literal = '%(_string_literal)s%(_identifier)s' % locals()

_user_defined_character_literal = '%(_character_literal)s%(_identifier)s' % locals()

_keywords = (
                           #'and',
                           #'and_eq',
    'asm',
    'auto',
                           #'bitand',
                           #'bitor',
    'bool',
    'break',
    'case',
    'catch',
    'char',
    'class',
                           #'compl',
    'const',
    'const_cast',
    'continue',
    'default',
    'delete',
    'do',
    'double',
    'dynamic_cast',
    'else',
    'enum',
    'explicit',
    'extern',
    'false',
    'float',
    'for',
    'friend',
    'goto',
    'if',
    'inline',
    'int',
    'long',
    'mutable',
    'namespace',
    'new',
                           #'not',
                           #'not_eq',
    'operator',
                           #'or',
                           #'or_eq',
    'private',
    'protected',
    'public',
    'register',
    'reinterpret_cast',
    'return',
    'short',
    'signed',
    'sizeof',
    'static',
    'static_cast',
    'struct',
    'switch',
    'template',
    'this',
    'throw',
    'true',
    'try',
    'typedef',
    'typeid',
    'typename',
    'union',
    'unsigned',
    'using',
    'virtual',
    'void',
    'volatile',
    'wchar_t',
    'while',
                           #'xor',
                           #'xor_eq',
    '__int128',
)                          # type: Tuple[str,...]

_keywords_cxx11 = (
    'alignas',
    'alignof',
    'char16_t',
    'char32_t',
    'constexpr',
    'decltype',
    'final',
    'noexcept',
    'nullptr',
    'override',
    'static_assert',
    'thread_local',
)                      # type: Tuple[str,...]

_keywords_cxx20 = (
    'char8_t',
    'concept',
    'consteval',
    'constinit',
    'co_await',
    'co_return',
    'co_yield',
    'export',
    'import',
    'module',
    'requires',
)                      # type: Tuple[str,...]

_keywords_transactional = (
    'atomic_cancel',
    'atomic_commit',
    'atomic_noexcept',
    'synchronized',
)                              # tupe: Tuple[str,...]

_keywords_reflection = ('reflexpr', )  # tupe: Tuple[str,...]

_keywords_cxx23 = _keywords_transactional + _keywords_reflection


class Cxx98Lexer(glrp.Lexer):
    keywords = _keywords
    tokens = _keywords + (
        'alignof-macro', 'virt-specifier-macro', 'virt-specifier-macro-function', 'access-specifier-macro',
        'access-specifier-macro-function', 'decl-specifier-macro', 'decl-specifier-macro-function',
        'attribute-specifier-macro', 'attribute-specifier-macro-function', 'storage-class-specifier-macro',
        'storage-class-specifier-macro-function', 'decltype-macro', 'type-trait-macro', 'type-trait-macro-function',
        'string-literal-macro', 'string-literal-macro-function', '%>'
    )

    def __init__(self):
        # type: () -> None
        glrp.Lexer.__init__(self)
        self._macros = {
            '__alignof__': 'alignof-macro',
            '__attribute__': 'attribute-specifier-macro-function',
            '__attribute': 'attribute-specifier-macro-function',
            '__declspec': 'attribute-specifier-macro-function',
            '__asm': 'attribute-specifier-macro-function',
            '__asm__': 'attribute-specifier-macro-function',
            '__restrict': 'attribute-specifier-macro',
            '__extension__': 'attribute-specifier-macro',
            '__typeof': 'decltype-macro',
            '__inline': 'decl-specifier-macro',
            '__inline__': 'decl-specifier-macro',
            '__has_unique_object_representations': 'type-trait-macro-function',
            '__has_virtual_destructor': 'type-trait-macro-function',
            '__is_abstract': 'type-trait-macro-function',
            '__is_aggregate': 'type-trait-macro-function',
            '__is_array': 'type-trait-macro-function',
            '__is_assignable': 'type-trait-macro-function',
            '__is_base_of': 'type-trait-macro-function',
            '__is_bounded_array': 'type-trait-macro-function',
            '__is_class': 'type-trait-macro-function',
            '__is_compound': 'type-trait-macro-function',
            '__is_const': 'type-trait-macro-function',
            '__is_constructible': 'type-trait-macro-function',
            '__is_convertible': 'type-trait-macro-function',
            '__is_destructible': 'type-trait-macro-function',
            '__is_empty': 'type-trait-macro-function',
            '__is_final': 'type-trait-macro-function',
            '__is_floating_point': 'type-trait-macro-function',
            '__is_function': 'type-trait-macro-function',
            '__is_fundamental': 'type-trait-macro-function',
            '__is_integral': 'type-trait-macro-function',
            '__is_interface_class': 'type-trait-macro-function',
            '__is_literal_type': 'type-trait-macro-function',
            '__is_lvalue_reference': 'type-trait-macro-function',
            '__is_member_object_pointer': 'type-trait-macro-function',
            '__is_member_function_pointer': 'type-trait-macro-function',
            '__is_member_pointer': 'type-trait-macro-function',
            '__is_nothrow_assignable': 'type-trait-macro-function',
            '__is_nothrow_constructible': 'type-trait-macro-function',
            '__is_nothrow_destructible': 'type-trait-macro-function',
            '__is_nullptr': 'type-trait-macro-function',
            '__is_object': 'type-trait-macro-function',
            '__is_pod': 'type-trait-macro-function',
            '__is_polymorphic': 'type-trait-macro-function',
            '__is_rvalue_reference': 'type-trait-macro-function',
            '__is_same': 'type-trait-macro-function',
            '__is_same_as': 'type-trait-macro-function',
            '__is_scoped_enum': 'type-trait-macro-function',
            '__is_sealed': 'type-trait-macro-function',
            '__is_standard_layout': 'type-trait-macro-function',
            '__is_trivial': 'type-trait-macro-function',
            '__is_trivially_assignable': 'type-trait-macro-function',
            '__is_trivially_constructible': 'type-trait-macro-function',
            '__is_trivially_copyable': 'type-trait-macro-function',
            '__is_trivially_destructible': 'type-trait-macro-function',
            '__is_trivially_relocatable': 'type-trait-macro-function',
            '__is_unbounded_array': 'type-trait-macro-function',
            '__is_union': 'type-trait-macro-function',
            '__is_unsigned': 'type-trait-macro-function',
            '__is_volatile': 'type-trait-macro-function',
            '__reference_binds_to_temporary': 'type-trait-macro-function'
        }

    @glrp.token(r'[ \t\n]+', 'whitespace', warn=False)
    def _00_skip(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        return None

    # arithmetic operators
    @glrp.token(r'\+', '+')
    @glrp.token(r'-')
    @glrp.token(r'\*', '*')
    @glrp.token(r'/')
    @glrp.token(r'%')
    @glrp.token(r'\|', '|')
    @glrp.token(r'&')
    @glrp.token(r'~')
    @glrp.token(r'\^', '^')
    @glrp.token(r'!')
    @glrp.token(r'<')
    # assignment operators
    @glrp.token(r'=')
    @glrp.token(r'\?', '?')
    @glrp.token(r',')
    @glrp.token(r'\.', '.')
    @glrp.token(r';')
    @glrp.token(r':')
    @glrp.token(r'\[', '[')
    @glrp.token(r'\{', '{')
    @glrp.token(r'\(', '(')
    @glrp.token(r'\]', ']')
    @glrp.token(r'\}', '}')
    @glrp.token(r'\)', ')')
    def _01_tok(self, token):
        # type: (glrp.Token) -> glrp.Token
        return token

    @glrp.token(r'>')
    def _01_angle_bracket(self, token):
        # type: (glrp.Token) -> glrp.Token
        try:
            if self._lexdata[token._end_position] == '>':
                self.set_token_type(token, '%>')
            return token
        except IndexError:
            return token

    @glrp.token(r'<<')
    @glrp.token(r'\|\|', '||')
    @glrp.token(r'&&')
    @glrp.token(r'<=')
    @glrp.token(r'>=')
    @glrp.token(r'==')
    @glrp.token(r'!=')
    @glrp.token(r'\*=', '*=')
    @glrp.token(r'/=')
    @glrp.token(r'%=')
    @glrp.token(r'\+=', '+=')
    @glrp.token(r'-=')
    @glrp.token(r'&=')
    @glrp.token(r'\|=', '|=')
    @glrp.token(r'\^=', '^=')
    @glrp.token(r'\+\+', '++')
    @glrp.token(r'--')
    @glrp.token(r'->')
    @glrp.token(r'\.\*', '.*')
    @glrp.token(r'::')
    def _02_tok(self, token):
        # type: (glrp.Token) -> glrp.Token
        return token

    @glrp.token(r'<<=')
    @glrp.token(r'>>=')
    @glrp.token(r'->\*', '->*')
    @glrp.token(r'\.\.\.', '...')
    def _03_tok(self, token):
        # type: (glrp.Token) -> glrp.Token
        return token

    @glrp.token(r'\#(?:[^\\\n]|(?:\\.)|(?:\\\n))*', 'preprocessor', warn=False)
    def _03_preprocessor(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        #if t.value.find('include') != -1:
        #    t.lexer.includes.append(t.value)
        return None

    @glrp.token(
        r'\#[ \t\v\r]*line(?:[ \t\v\r]+\d+)*(?:[ \t\v\r]+"[^\n"]*")?[ \t\v\r]*\n', 'preprocessor_line', warn=False
    )
    def _04_preprocessor_line(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        #if t.value.find('include') != -1:
        #    t.lexer.includes.append(t.value)
        tokens = t.text()[1:].split()
        self._lineno = 1 + int(tokens[1])
        if len(tokens) > 2:
            self._filename = tokens[-1][1:-1]
        return None

    @glrp.token(
        r'\#[ \t\v\r]\d+(?:[ \t\v\r]+"[^\n"]*"(?:[ \t\v\r]+\d+)*)?[ \t\v\r]*\n', 'preprocessor_line_2', warn=False
    )
    def _04_preprocessor_line_2(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        #if t.value.find('include') != -1:
        #    t.lexer.includes.append(t.value)
        tokens = t.text()[1:].split()
        self._lineno = 1 + int(tokens[0])
        if len(tokens) > 1:
            self._filename = tokens[1][1:-1]
        return None

    @glrp.token(r'/\*[\!\*](.|\n)*?\*/', 'doxycomment-block')
    @glrp.token(r'//[/\!](?:[^\\\n]|(?:\\.)|(?:\\\n))*', 'doxycomment-line')
    def _05_documentation(self, token):
        # type: (glrp.Token) -> glrp.Token
        return token

    @glrp.token(r'/\*(.|\n)*?\*/', 'block-comment', warn=False)
    @glrp.token(r'//(?:[^\\\n]|(?:\\.)|(?:\\\n))*', 'line-comment', warn=False)
    def _06_comment(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        return None

    @glrp.token(_identifier, '%identifier')
    def _07_identifier(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        t.value = self.text(t)
        if t.value in self.keywords:
            self.set_token_type(t, t.value)
        else:
            try:
                macro_type = self._macros[t.value]
            except KeyError:
                pass
            else:
                self.set_token_type(t, macro_type)
        return t

    @glrp.token(_integer_literal, 'integer-literal')
    def _08_integer_literal(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        t.value = t.text()
        return t

    @glrp.token(_floating_literal, 'floating-literal')
    def _10_floating_literal(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        t.value = t.text()
        return t

    @glrp.token(_string_literal, 'string-literal')
    def _12_string_literal(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        text = self.text(t)
        t.value = text[1:-1]
        return t

    @glrp.token(_character_literal, 'character-literal')
    def _12_character_literal(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        text = self.text(t)
        t.value = text[1:-1]
        return t


class Cxx03Lexer(Cxx98Lexer):
    pass


class Cxx11Lexer(Cxx03Lexer):
    tokens = Cxx03Lexer.tokens + ('[[', ) + _keywords_cxx11
    keywords = Cxx03Lexer.keywords + _keywords_cxx11

    def _token(self, track_blanks=False):
        # type: (bool) -> Generator[glrp.Token, None, None]
        # override token to concatenate [ [ into [[
        # preserving comments and other items between the [ symbols
        queue = []     # type: List[glrp.Token]
        bracket_id = self.get_token_id('[')
        generator = Cxx03Lexer._token(self, track_blanks)
        while True:
            if queue:
                yield queue.pop(0)
            try:
                token = next(generator)
            except StopIteration:
                break
            else:
                if token._id == bracket_id:
                    try:
                        next_token = next(generator)
                    except StopIteration:
                        yield token
                    else:
                        if next_token._id == bracket_id:
                            next_token._skipped_tokens = token._skipped_tokens + [token] + next_token._skipped_tokens
                            self.set_token_type(next_token, '[[')
                            yield next_token
                        else:
                            queue.append(next_token)
                            yield token
                else:
                    yield token

    @glrp.token(_user_defined_integer_literal, 'user-defined-integer-literal')
    def _09_user_integer_literal(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        t.value = (self.text(t), '')   # TODO
        return t

    @glrp.token(_user_defined_floating_literal, 'user-defined-floating-literal')
    def _11_user_floating_literal(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        t.value = (self.text(t), '')   # TODO
        return t

    @glrp.token(_user_defined_character_literal, 'user-defined-character-literal')
    def _13_user_defined_character_literal(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        t.value = (self.text(t), '')   # TODO
        return t

    @glrp.token(_user_defined_string_literal, 'user-defined-string-literal')
    def _13_user_defined_string_literal(self, t):
        # type: (glrp.Token) -> Optional[glrp.Token]
        value = self.text(t)
        end_string = value.rfind('"')
        literal_id = value[end_string + 1:]
        text = value[1:end_string]
        t.value = (text, literal_id)
        return t


class Cxx14Lexer(Cxx11Lexer):
    pass


class Cxx17Lexer(Cxx14Lexer):
    pass


class Cxx20Lexer(Cxx17Lexer):
    tokens = Cxx17Lexer.tokens + _keywords_cxx20 + ('type-trait-macro', 'type-trait-macro-function')
    keywords = Cxx17Lexer.keywords + _keywords_cxx20

    @glrp.token(r'<=>')
    def _03_tok_spaceship(self, token):
        # type: (glrp.Token) -> glrp.Token
        return token


class Cxx23Lexer(Cxx20Lexer):
    tokens = Cxx20Lexer.tokens + _keywords_cxx23
    keywords = Cxx20Lexer.keywords + _keywords_cxx23


if TYPE_CHECKING:
    from motor_typing import List, Optional, Tuple, Generator, Set