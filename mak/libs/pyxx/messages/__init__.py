import argparse
from .logger import Logger
from motor_typing import TYPE_CHECKING


def init_arguments(argument_context: argparse.ArgumentParser) -> None:
    group = argument_context.add_argument_group('Diagnostics options')
    Logger.init_diagnostic_flags(group)


def load_arguments(argument_context: argparse.Namespace) -> Logger:
    logger = Logger(argument_context)
    return logger
