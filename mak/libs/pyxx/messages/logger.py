import sys
import io
import argparse
import glrp
from typing import TypeVar, cast, Dict, Callable, Tuple, Union, Any, List, Optional

T = TypeVar('T', bound='Callable[..., Dict[str, Any]]')


def diagnostic(func: T) -> T:
    def call(
            self: 'Logger', position: Tuple[int, int], *args: Union[str, int],
            **kw_args: Union[str, int]
    ) -> None:
        if call in self._expected_diagnostics:
            self._expected_diagnostics.remove(cast(T, call))
        format_values = func(self, position, *args, **kw_args)
        message = getattr(self.LANG, func.__name__, func.__doc__)
        assert isinstance(message, str)
        self._msg_position('note', position, message.format(**format_values))

    setattr(Logger, func.__name__, call)
    return cast(T, call)


def warning(flag_name: str, enabled: bool = False, enabled_in: List[str] = []) -> Callable[[T], T]:
    def inner(func: T) -> T:

        def call(
                self: 'Logger', position: Tuple[int, int], *args: Union[str, int],
                **kw_args: Union[str,
                int]
        ) -> bool:
            if not getattr(self._arguments, flag_name):
                return False
            format_values = func(self, position, *args, **kw_args)
            self._warning_count += 1
            if self._warning_count == 1 and self._arguments.warn_error:
                C0002(self, position)
            message = getattr(self.LANG, func.__name__, func.__doc__)
            assert isinstance(message, str)
            self._msg_position(
                'warning', position,
                message.format(**format_values) + ' [-W{}]'.format(flag_name)
            )
            return True

        setattr(call, 'flag_name', flag_name)
        setattr(call, 'enabled', enabled)
        setattr(call, 'enabled_in', enabled_in)

        setattr(Logger, func.__name__, call)
        return cast(T, call)

    return inner


def error(func: T) -> T:
    def call(
            self: 'Logger', position: Tuple[int, int], *args: Union[str, int],
            **kw_args: Union[str, int]
    ) -> None:
        self._error_count += 1
        format_values = func(self, position, *args, **kw_args)
        message = getattr(self.LANG, func.__name__, func.__doc__)
        assert isinstance(message, str)
        self._msg_position('error', position, message.format(**format_values))

    call.__name__ = func.__name__
    setattr(Logger, func.__name__, call)
    return cast(T, call)


class Logger(glrp.Logger):
    LANG = None

    IDE_FORMAT = {
        'msvc':
            '{color_filename}{filename}{color_off}({line:d},{column:d}) : {color_error_type}{error_type}{color_off}: {color_message}{message}{color_off}\n',
        'unix':
            '{color_filename}{filename}{color_off}:{line:d}:{column:d}: {color_error_type}{error_type}{color_off}: {color_message}{message}{color_off}\n',
        'vi':
            '{color_filename}{filename}{color_off} +{line:d}:{column:d}: {color_error_type}{error_type}{color_off}: {color_message}{message}{color_off}\n',
    }

    @classmethod
    def init_diagnostic_flags(self, group: argparse._ArgumentGroup) -> None:
        group.add_argument(
            "-e",
            "--diagnostics-format",
            dest="diagnostics_format",
            choices=('msvc', 'unix', 'vi'),
            help="Select diagnostics format to match IDE.",
            default='unix'
        )
        group.add_argument(
            "-Werror", dest="warn_error", help="Treat warning as errors", default=False, action="store_true"
        )
        for m in self.__dict__.values():
            flag = getattr(m, 'flag_name', None)
            if flag is not None:
                group.add_argument('-W{}'.format(flag), dest=flag, help=argparse.SUPPRESS, action='store_true',
                                   default=getattr(m, 'enabled'))
                group.add_argument('-Wno-{}'.format(flag), dest=flag, help=argparse.SUPPRESS, action='store_false')

    def __init__(self, arguments: argparse.Namespace) -> None:
        glrp.Logger.__init__(self, io.open(sys.stderr.fileno(), 'w', encoding='utf-8', closefd=False))
        self._lexer = None  # type: Optional[glrp.Lexer]
        self._arguments = arguments
        self._warning_count = 0
        self._error_count = 0
        self._diagnostics_format = Logger.IDE_FORMAT[getattr(arguments, 'diagnostics_format')]
        self._expected_diagnostics = []  # type: List[Callable[..., Dict[str, Any]]]

    def set_lexer(self, lexer: glrp.Lexer) -> None:
        self._lexer = lexer

    def _msg_position(self, error_type: str, position: Tuple[int, int], message: str) -> None:
        assert self._lexer is not None
        if self._error_color:
            (color_error_type, color_filename, color_message, color_caret,
             color_off) = self.COLOR_PATTERN.get(error_type, self.DEFAULT_COLOR_PATTERN)
        else:
            color_error_type = ''
            color_filename = ''
            color_message = ''
            color_caret = ''
            color_off = ''

        filename, (line, column), (end_line, end_column) = self._lexer.text_position(position)
        context = self._lexer.context(position)

        self._out_file.write(self._diagnostics_format.format(**locals()))
        if len(context) == 1:
            self._out_file.write(context[0])
            self._out_file.write(
                '\n%s%s%s%s\n' % (' ' * (column - 1), color_caret, '^' + '~' * (end_column - column - 1), color_off)
            )
        else:
            for text in context[:-1]:
                self._out_file.write(text)
                self._out_file.write(
                    '\n%s%s%s%s\n' % (' ' * (column - 1), color_caret, '^' + '~' * (len(text) - column), color_off)
                )
                column = 1
            self._out_file.write(context[-1])
            self._out_file.write('\n%s%s%s\n' % (color_caret, '^' * (end_column - 1), color_off))

    def push_expected_diagnostics(self, diagnostics: List[Callable[..., Dict[str, Any]]]) -> None:
        self._expected_diagnostics += diagnostics

    def pop_expected_diagnostics(self) -> bool:
        result = bool(self._expected_diagnostics)
        self._expected_diagnostics = []
        return result


@error
def C0000(self: Logger, position: Tuple[int, int], token: str) -> Dict[str, Any]:
    """syntax error at token '{token}'"""
    return locals()


@error
def C0001(self: Logger, position: Tuple[int, int], token: str, current_rules: str) -> Dict[str, Any]:
    """syntax error at token '{token}' when trying to parse {current_rules}"""
    return locals()


@error
def C0002(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """warning treated as error"""
    return locals()
