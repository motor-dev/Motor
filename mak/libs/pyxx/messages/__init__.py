import argparse
from .logger import Logger, diagnostic, warning, error


def init_arguments(argument_context: argparse.ArgumentParser) -> None:
    Logger.init_diagnostic_flags(argument_context)


def load_arguments(argument_context: argparse.Namespace) -> Logger:
    return Logger(argument_context)
