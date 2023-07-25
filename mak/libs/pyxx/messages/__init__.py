import argparse
from .logger import Logger, diagnostic, warning, error, C0000, C0001, C0002
from motor_typing import TYPE_CHECKING


def init_arguments(argument_context: argparse.ArgumentParser) -> None:
    group = argument_context.add_argument_group('Diagnostics options')
    Logger.init_diagnostic_flags(group)


def load_arguments(argument_context: argparse.Namespace) -> Logger:
    logger = Logger(argument_context)
    return logger
