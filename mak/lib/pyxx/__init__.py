from . import messages, parse, utils
from typing import Any, List
import argparse
import glrp
import json


def init_arguments() -> argparse.ArgumentParser:
    argument_context = argparse.ArgumentParser()
    argument_context.add_argument(
        "-o",
        "--optimized",
        dest="optimized",
        help="Skip table file generation and assume up to date",
        default=False,
        action="store_true",
    )
    argument_context.add_argument(
        "-t",
        "--tmp",
        dest="tmp_dir",
        help="Directory to store temporary/cached files",
        default=".",
    )
    argument_context.add_argument(
        "-d",
        "--debug",
        dest="debug",
        help="Assume running from a debugger",
        default=False,
        action="store_true",
    )
    argument_context.add_argument(
        "-x",
        dest="lang",
        help="Source code language",
        choices=('auto', 'c', 'c++', 'objc', 'objc++'),
        default='auto',
        action="store"
    )
    argument_context.add_argument(
        "--std",
        dest="std",
        help="Language standard to parse",
        choices=(
            'c89',
            'c99',
            'c11',
            'c17',
            'c++98',
            'c++03',
            'c++11',
            'c++14',
            'c++17',
            'c++20',
            'c++23',
        ),
        default='c++98',
        action="store"
    )
    argument_context.add_argument(
        "-D",
        dest="macro_file",
        action="append",
        help="Add the content of <macrofile> to the macros, one macro per line"
    )
    argument_context.add_argument(
        "input",
        help="Input source file",
        metavar="IN",
    )
    messages.init_arguments(argument_context)
    return argument_context


logger = None


def run(arguments: argparse.Namespace) -> List[Any]:
    import os
    import sys
    import logging

    global logger
    logger = messages.load_arguments(arguments)

    exception_type = Exception
    if arguments.debug:
        exception_type = SyntaxError
    try:
        mode = glrp.LOAD_OPTIMIZED if arguments.optimized else glrp.LOAD_CACHE
        p = parse.parser(arguments.lang,
                         os.path.splitext(arguments.input)[1], arguments.std)(logger, arguments.tmp_dir, mode)
        for macro_file in arguments.macro_file or []:
            with open(macro_file, 'r') as macro_file_content:
                macros = json.load(macro_file_content)
                for macro, macro_type in macros.items():
                    p.lexer.add_macro(macro, macro_type)
        result = p.parse(arguments.input, arguments.debug)
        if not result:
            sys.exit(1)
        elif logger.error_count > 0:
            sys.exit(logger.error_count)
        else:
            return result
    except (SyntaxError, exception_type) as exception:
        logging.exception(exception)
        sys.exit(255)
