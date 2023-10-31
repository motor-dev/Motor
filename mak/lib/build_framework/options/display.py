import sys
import waflib.Configure
import waflib.Context
import waflib.Logs
import logging

from typing import Optional

legacy_log_emit_override = waflib.Logs.log_handler.emit_override

status_line = None


def log_handler_emit(handler: waflib.Logs.log_handler, record: logging.LogRecord) -> None:
    if status_line is not None:
        newline_count = record.msg.count('\n')
        if newline_count > 1 or len(record.msg) > waflib.Logs.get_term_cols():
            sys.stdout.write('\0337\033[999B\r\033[K\0338')
        legacy_log_emit_override(handler, record)
        if handler.terminator == '\n' or newline_count:
            sys.stdout.write('\033[2K\033D\033M\0337\033[999B\r%s\0338' % status_line)
    else:
        legacy_log_emit_override(handler, record)


if sys.platform == "win32":
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
setattr(waflib.Logs.log_handler, 'emit_override', log_handler_emit)


@waflib.Configure.conf
def set_status_line(_: waflib.Context.Context, line: str) -> None:
    global status_line
    if status_line is None:
        sys.stdout.write('\033D\033M')
    status_line = line
    sys.stdout.write('\0337\033[999B\r%s\0338' % status_line)


def clear_status_line(_: waflib.Context.Context) -> None:
    global status_line
    if status_line is not None:
        status_line = None
        sys.stdout.write('\0337\033[999B\r\033[K\0338')


@waflib.Configure.conf
def progress_line(context: waflib.Context.Context, idx: int, total: int, col1: str, col2: str) -> Optional[str]:
    """
    Computes a progress bar line displayed when running ``waf -p``

    :returns: progress bar line
    :rtype: string
    """
    if not sys.stdout.isatty():
        return None

    right = '[%s%s%s]' % (col1, context.timer, col2)
    cols = waflib.Logs.get_term_cols() - len(right) + len(col2) + len(col1)
    cmd = context.cmd[:cols]

    ratio = ((cols * idx * 8) // total)
    full_length = ratio // 8

    if idx == total:
        bar = '\x1b[30;42m' + cmd + '\x1b[32;100m' + ('\u2588' * (full_length - len(cmd))) + '\x1b[0m'
    elif full_length >= len(cmd):
        subpixel = ' \u258f\u258e\u258d\u258c\u258b\u258a\u2589'
        bar = '\x1b[30;42m' + cmd + '\x1b[32;100m' + ('\u2588' * (full_length - len(cmd))) + subpixel[
            ratio % 8] + (' ' * (cols - full_length - 1)) + '\x1b[0m'
    else:
        subpixel = ' \u258f\u258e\u258d\u258c\u258b\u258a\u2589'
        bar = '\x1b[30;42m' + cmd[:full_length] + '\x1b[32;100m' + subpixel[
            ratio % 8] + '\x1b[37;100m' + cmd[full_length + 1:] + (' ' * (cols - len(cmd))) + '\x1b[0m'
    msg = waflib.Logs.indicator % ('', bar, right)

    return msg
