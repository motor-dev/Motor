import os
from waflib import Options
from waflib.Logs import pprint
from motor_typing import TYPE_CHECKING


def setup(configuration_context):
    # type: (Configure.ConfigurationContext) -> None
    if 'windows' in configuration_context.env.VALID_PLATFORMS:
        configuration_context.start_msg_setup()
        if Options.options.dx_sdk:
            includes = [os.path.join(Options.options.dx_sdk, 'Include')]
            libdirs = []
            for arch in configuration_context.env.VALID_ARCHITECTURES:
                p = os.path.join(Options.options.dx_sdk, 'Lib', arch)
                if os.path.isdir(p):
                    libdirs.append(p)
        else:
            includes = []
            libdirs = []
        found = []
        if configuration_context.check_lib(
            'd3d12',
            var='dx12',
            libpath=libdirs,
            includepath=includes,
            includes=['d3d12.h'],
            functions=['D3D12CreateDevice']
        ):
            found.append('DirectX 12')
        if not found:
            configuration_context.end_msg('not found', color='YELLOW')
        else:
            configuration_context.end_msg(', '.join(found), color='GREEN')


if TYPE_CHECKING:
    from waflib import Configure