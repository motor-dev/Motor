import os
import build_framework
import waflib.Options


def setup(setup_context: build_framework.SetupContext) -> None:
    if 'windows' in setup_context.env.VALID_PLATFORMS:
        build_framework.start_msg_setup(setup_context)
        if waflib.Options.options.dx_sdk:
            includes = [os.path.join(waflib.Options.options.dx_sdk, 'Include')]
            libdirs = []
            for arch in setup_context.env.VALID_ARCHITECTURES:
                p = os.path.join(waflib.Options.options.dx_sdk, 'Lib', arch)
                if os.path.isdir(p):
                    libdirs.append(p)
        else:
            includes = []
            libdirs = []
        found = []
        if build_framework.check_lib(
                setup_context,
                ['d3d12'],
                var='dx12',
                libpath=libdirs,
                includepath=includes,
                includes=['d3d12.h'],
                functions=['D3D12CreateDevice']
        ):
            found.append('DirectX 12')
        if not found:
            setup_context.end_msg('not found', color='YELLOW')
        else:
            setup_context.end_msg(', '.join(found), color='GREEN')
