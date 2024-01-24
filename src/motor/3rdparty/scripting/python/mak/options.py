import waflib.Options


def options(options_context: waflib.Options.OptionsContext) -> None:
    gr = options_context.add_option_group('configure options')
    gr.add_option(
        '--python-versions',
        action='store',
        dest='python_versions',
        help='List of Python version to support in plugins',
        default='3.5,3.6,3.7,3.8,3.9,3.10,3.11,3.12'
    )
