import sys
import waflib.Options
from typing import List, Tuple


def options(options_context: waflib.Options.OptionsContext) -> None:
    dx_sdks = []  # type: List[Tuple[str, str]]
    if sys.platform == "win32":
        import winreg
        try:
            sdks = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Wow6432node\\Microsoft\\DirectX\\')
        except OSError:
            sdks = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\DirectX\\')
        index = 0
        while 1:
            try:
                version = winreg.EnumKey(sdks, index)
            except OSError:
                break
            index = index + 1
            try:
                sdk_version = winreg.OpenKey(sdks, version)
                version, _ = winreg.QueryValueEx(sdk_version, 'InstalledVersion')
                path, _ = winreg.QueryValueEx(sdk_version, 'InstallPath')
                dx_sdks.append((version, str(path)))
            except OSError:
                pass
    dx_sdks.sort(key=lambda x: x[0])
    gr = options_context.get_option_group('SDK paths and options')
    assert gr is not None
    gr.add_option(
        '--directx-sdk',
        action='store',
        default=dx_sdks and dx_sdks[-1][1] or '',
        dest='dx_sdk',
        help='Location of the DirectX SDK'
    )
