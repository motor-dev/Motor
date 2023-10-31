import waflib.Options


def options(options_context: waflib.Options.OptionsContext) -> None:
    gr = options_context.add_option_group('configure options')
    gr.add_option(
        '--python-versions',
        action='store',
        dest='python_versions',
        help='List of Python version to support in plugins',
        default='2.6,2.7,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,3.10,3.11,3.12'
    )
