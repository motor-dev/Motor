import sys
import io
import re
import argparse
import glrp
from typing import Dict, Callable, Tuple, Any, List, Optional, TYPE_CHECKING


def diagnostic(func: "Callable[Concatenate[Logger, Tuple[int, int], T], Dict[str, Any]]") \
        -> "Callable[Concatenate[Logger, Tuple[int, int], T], None]":
    def call(
            self: "Logger",
            position: Tuple[int, int],
            *args: "T.args",
            **kwargs: "T.kwargs"
    ) -> None:
        if call in self._expected_diagnostics:
            self._expected_diagnostics.remove(call)
        format_values = func(self, position, *args, **kwargs)
        message = getattr(self.LANG, func.__name__, func.__doc__)
        assert isinstance(message, str)
        self._msg_position('note', position, message.format(**format_values))

    setattr(Logger, func.__name__, call)
    return call


def warning(flag_name: str, enabled: bool = False, enabled_in: Optional[List[str]] = None) \
        -> Callable[
            ["Callable[Concatenate[Logger, Tuple[int, int], T], Dict[str, Any]]"],
            "Callable[Concatenate[Logger, Tuple[int, int], T], bool]"]:
    def inner(func: "Callable[Concatenate[Logger, Tuple[int, int], T], Dict[str, Any]]") \
            -> "Callable[Concatenate[Logger, Tuple[int, int], T], bool]":

        def call(
                self: "Logger",
                position: Tuple[int, int],
                *args: "T.args",
                **kw_args: "T.kwargs"
        ) -> bool:

            if not getattr(self._arguments, flag_name):
                return False

            format_values = func(self, position, *args, **kw_args)
            self._warning_count += 1
            if self._warning_count == 1 and self._arguments.warn_error:
                c0002(self, position)
            message = getattr(self.LANG, func.__name__, func.__doc__)
            assert isinstance(message, str)
            self._msg_position(
                'warning', position,
                message.format(**format_values) + ' [-W{}]'.format(flag_name)
            )
            return True

        setattr(call, 'flag_name', flag_name)
        setattr(call, 'enabled', enabled)
        setattr(call, 'enabled_in', enabled_in or [])

        setattr(Logger, func.__name__, call)
        return call

    return inner


def error(func: "Callable[Concatenate[Logger, Tuple[int, int], T], Dict[str, Any]]") \
        -> "Callable[Concatenate[Logger, Tuple[int, int], T], None]":
    def call(
            self: "Logger",
            position: Tuple[int, int],
            *args: "T.args",
            **kw_args: "T.kwargs"
    ) -> None:
        self._error_count += 1
        format_values = func(self, position, *args, **kw_args)
        message = getattr(self.LANG, func.__name__, func.__doc__)
        assert isinstance(message, str)
        self._msg_position('error', position, message.format(**format_values))

    call.__name__ = func.__name__
    setattr(Logger, func.__name__, call)
    return call


class Logger(glrp.Logger):
    LANG = None

    IDE_FORMAT = {
        'msvc':
            '{color_filename}{filename}{color_off}({line:d},{column:d}) : '
            '{color_error_type}{error_type}{color_off}: {color_message}{message}{color_off}\n',
        'unix':
            '{color_filename}{filename}{color_off}:{line:d}:{column:d}: '
            '{color_error_type}{error_type}{color_off}: {color_message}{message}{color_off}\n',
        'vi':
            '{color_filename}{filename}{color_off} +{line:d}:{column:d}: '
            '{color_error_type}{error_type}{color_off}: {color_message}{message}{color_off}\n',
    }

    @classmethod
    def init_diagnostic_flags(cls, argument_context: argparse.ArgumentParser) -> None:
        group = argument_context.add_argument_group('Diagnostics options')
        group.add_argument(
            "-e",
            "--diagnostics-format",
            dest="diagnostics_format",
            choices=('msvc', 'unix', 'vi'),
            help="Select diagnostics format to match IDE.",
            default='unix'
        )
        group.add_argument(
            "-c",
            "--diagnostics-color",
            dest="diagnostics_color",
            help="Enable color diagnostics",
            default=False,
            action='store_true'
        )
        group.add_argument(
            "-Werror", dest="warn_error", help="Treat warning as errors", default=False, action="store_true"
        )
        seen = set()
        for m in cls.__dict__.values():
            flag = getattr(m, 'flag_name', None)
            if flag is not None and flag not in seen:
                seen.add(flag)
                group.add_argument('-W{}'.format(flag), dest=flag, help=argparse.SUPPRESS, action='store_true',
                                   default=getattr(m, 'enabled'))
                group.add_argument('-Wno-{}'.format(flag), dest=flag, help=argparse.SUPPRESS, action='store_false')

    def __init__(self, arguments: argparse.Namespace) -> None:
        glrp.Logger.__init__(self, io.open(sys.stderr.fileno(), 'w', encoding='utf-8', closefd=False),
                             arguments.diagnostics_color)
        self._lexer = None  # type: Optional[glrp.Lexer]
        self._arguments = arguments
        self._warning_count = 0
        self._error_count = 0
        self._expected_diagnostics = []  # type: List[Callable[..., Any]]
        self._diagnostics_format = Logger.IDE_FORMAT[getattr(arguments, 'diagnostics_format')]

    @property
    def error_count(self) -> int:
        return self._error_count

    def set_lexer(self, lexer: glrp.Lexer) -> None:
        self._lexer = lexer

    def _msg_position(self, error_type: str, position: Tuple[int, int], message: str) -> None:
        def replace_tab(start: str, middle: str, end: str, single_char: str, in_text: str) -> str:
            def start_column(index: int) -> int:
                result = 0
                for char in in_text[:index]:
                    if char == '\t':
                        result = result + 4 - result % 4
                    else:
                        result += 1
                return result

            def perform_replace(match: re.Match[str]) -> str:
                s, e = match.span()
                tab_start = start_column(s)
                tab_length = 4 - tab_start % 4 + 4 * (e - s - 1)
                if tab_length == 1:
                    return single_char
                else:
                    return '%s%s%s' % (
                        start, middle * (tab_length - 2), end,
                    )

            return re.sub('\t+', perform_replace, in_text)

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
        original_context = context
        if self._error_color:
            context = [
                re.sub(r'(\ +)',
                       lambda x: (self.COLOR_LIST['FAINT'] + ('\u00b7' * len(x.group())) +
                                  self.COLOR_LIST[
                                      'NORMAL']),
                       replace_tab(self.COLOR_LIST['FAINT'] + '\u2576', '\u2500',
                                   '\u2574' + self.COLOR_LIST['NORMAL'],
                                   self.COLOR_LIST['FAINT'] + '-' + self.COLOR_LIST['NORMAL'],
                                   c)) for c in original_context
            ]

        self._out_file.write(self._diagnostics_format.format(**locals()))
        for i, (text, original_text) in enumerate(zip(context[:-1], original_context[:-1])):
            self._out_file.write(
                '%s%5d \u2502%s%s' % (self.COLOR_LIST['CYAN'], line + i, text, self.COLOR_LIST['NORMAL']))
            range_highlight_start = replace_tab(' ', ' ', ' ', ' ',
                                                re.sub(r'[^ \t]', ' ', original_text[:column - 1]))
            range_highlight_end = replace_tab('~', '~', '~', '~',
                                              re.sub(r'[^\t]', '~', original_text[column:]))
            self._out_file.write(
                '\n%s      \u2502%s%s%s^%s%s\n' % (
                    self.COLOR_LIST['CYAN'], self.COLOR_LIST['NORMAL'], range_highlight_start, color_caret,
                    range_highlight_end, color_off)
            )
            column = 1
        self._out_file.write('%s%5d \u2502%s%s' % (
            self.COLOR_LIST['CYAN'], line + len(context) - 1, context[-1], self.COLOR_LIST['NORMAL']))
        range_highlight_start = replace_tab(' ', ' ', ' ', ' ',
                                            re.sub(r'[^ \t]', ' ', original_context[-1][:column - 1]))
        range_highlight_end = replace_tab('~', '~', '~', '~',
                                          re.sub(r'[^\t]', '~', original_context[-1][column - 1:end_column - 1]))
        self._out_file.write(
            '\n%s      \u2502%s%s%s^%s%s\n' % (
                self.COLOR_LIST['CYAN'], self.COLOR_LIST['NORMAL'], range_highlight_start, color_caret,
                range_highlight_end[:-1], color_off,)
        )

    def push_expected_diagnostics(self, diagnostics: List[Callable[..., Any]]) -> None:
        self._expected_diagnostics += diagnostics

    def pop_expected_diagnostics(self) -> bool:
        result = bool(self._expected_diagnostics)
        self._expected_diagnostics = []
        return result


@error
def c0002(self: Logger, position: Tuple[int, int]) -> Dict[str, Any]:
    """warning treated as error"""
    return locals()


if TYPE_CHECKING:
    from typing_extensions import ParamSpec, Concatenate

    T = ParamSpec('T')
