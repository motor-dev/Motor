import waflib.Options


def options_target_macos(option_context: waflib.Options.OptionsContext) -> None:
    gr = option_context.get_option_group('SDK paths and options')
    assert gr is not None
    gr.add_option(
        '--macosx-sdk-min',
        action='store',
        default='',
        dest='macosx_sdk_min',
        help='Minimum version of the MacOS X SDK to target'
    )
    gr.add_option(
        '--macosx-sdk-max',
        action='store',
        default='',
        dest='macosx_sdk_max',
        help='Maximum version of the MacOS X SDK to target'
    )
