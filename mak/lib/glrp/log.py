from typing import Any, Text, TextIO


class Logger:
    COLOR_LIST = {
        'BOLD': '\x1b[01;1m',
        'FAINT': '\x1b[02;37m',
        'BLACK': '\x1b[30m',
        'RED': '\x1b[31m',
        'GREEN': '\x1b[32m',
        'YELLOW': '\x1b[33m',
        'BLUE': '\x1b[34m',
        'PINK': '\x1b[35m',
        'CYAN': '\x1b[36m',
        'WHITE': '\x1b[37m',
        'BBLACK': '\x1b[01;30m',
        'BRED': '\x1b[01;31m',
        'BGREEN': '\x1b[01;32m',
        'BYELLOW': '\x1b[01;33m',
        'BBLUE': '\x1b[01;34m',
        'BPINK': '\x1b[01;35m',
        'BCYAN': '\x1b[01;36m',
        'BWHITE': '\x1b[01;37m',
        'NORMAL': '\x1b[0m',
    }

    DEFAULT_COLOR_PATTERN = (
        COLOR_LIST['BWHITE'], COLOR_LIST['BWHITE'], COLOR_LIST['NORMAL'], COLOR_LIST['BGREEN'], COLOR_LIST['NORMAL']
    )

    COLOR_PATTERN = {
        'note':
            (
                COLOR_LIST['BBLACK'], COLOR_LIST['BWHITE'], COLOR_LIST['NORMAL'], COLOR_LIST['BGREEN'],
                COLOR_LIST['NORMAL']
            ),
        'info':
            (
                COLOR_LIST['BWHITE'], COLOR_LIST['BWHITE'], COLOR_LIST['NORMAL'], COLOR_LIST['BGREEN'],
                COLOR_LIST['NORMAL']
            ),
        'warning':
            (
                COLOR_LIST['BYELLOW'], COLOR_LIST['BWHITE'], COLOR_LIST['NORMAL'], COLOR_LIST['BGREEN'],
                COLOR_LIST['NORMAL']
            ),
        'error':
            (
                COLOR_LIST['BRED'], COLOR_LIST['BWHITE'], COLOR_LIST['BOLD'], COLOR_LIST['BGREEN'],
                COLOR_LIST['NORMAL']
            ),
    }

    def __init__(self, out_file: TextIO, force_colors: bool = False) -> None:
        self._out_file = out_file
        self._error_color = force_colors or out_file.isatty()

    def _msg(self, error_type: str, message: Text) -> None:
        if self._error_color:
            (color_error_type, color_filename, color_message, color_caret,
             color_off) = self.COLOR_PATTERN.get(error_type, self.DEFAULT_COLOR_PATTERN)
            self._out_file.write(
                u'\r\x1b[2K{color_error_type}{error_type}{color_off}: {color_message}{message}{color_off}\n'.format(
                    **locals()
                )
            )
        else:
            color_error_type = ''
            color_filename = ''
            color_message = ''
            color_caret = ''
            color_off = ''

            self._out_file.write(u'{color_message}{message}{color_off}\n'.format(**locals()))

    def diagnostic(self, filename: str, line: int, message: Text, *args: Any) -> None:
        if args:
            message = message % args
        self._out_file.write(u'%s:%d: %s\n' % (filename, line, message))

    def note(self, message: Text, *args: Any) -> None:
        if args:
            self._msg('note', message % args)
        else:
            self._msg('note', message)

    def info(self, message: Text, *args: Any) -> None:
        if args:
            self._msg('info', message % args)
        else:
            self._msg('info', message)

    def warning(self, message: Text, *args: Any) -> None:
        if args:
            self._msg('warning', message % args)
        else:
            self._msg('warning', message)

    def error(self, message: Text, *args: Any) -> None:
        if args:
            self._msg('error', message % args)
        else:
            self._msg('error', message)
