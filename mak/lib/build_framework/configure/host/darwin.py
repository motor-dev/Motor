import os
import sys
import shlex
import waflib.Configure
import waflib.Options
import waflib.Utils
from typing import Tuple, Union


def configure_host_darwin(configuration_context: waflib.Configure.ConfigurationContext) -> None:
    environ = getattr(configuration_context, 'environ', os.environ)
    environ['PATH'] = '/System/Library/Frameworks/OpenCL.framework/Libraries:' + environ['PATH']
    configuration_context.env.OS_SDK_PATH = []
    for p in waflib.Options.options.xcode_sdks.split(',')[::-1]:
        if os.path.isdir(os.path.join(p, 'SDKs')):
            configuration_context.env.append_unique('OS_SDK_PATH', os.path.normpath(os.path.join(p, 'SDKs')))
        try:
            for platform in os.listdir(os.path.join(p, 'Platforms')):
                configuration_context.env.append_value('EXTRA_PATH', [
                    os.path.join(p, 'Platforms', platform, 'Developer', 'usr', 'bin')])
                s_path = os.path.normpath(os.path.join(p, 'Platforms', platform, 'Developer', 'SDKs'))
                if os.path.isdir(s_path):
                    configuration_context.env.append_unique('OS_SDK_PATH', s_path)
        except OSError:
            pass
        configuration_context.env.append_value('EXTRA_PATH',
                                               ['%s/Toolchains/XcodeDefault.xctoolchain/usr/bin' % p, '%s/usr/bin' % p])
    # find valid code signing identity
    process = waflib.Utils.subprocess.Popen(
        ['security', 'find-identity', '-p', 'codesigning', '-v'],
        stdout=waflib.Utils.subprocess.PIPE,
        stderr=waflib.Utils.subprocess.STDOUT
    )
    output, error = process.communicate()  # type: Tuple[Union[str, bytes], Union[str, bytes]]
    if not isinstance(output, str):
        output = output.decode(sys.stdout.encoding)
    for line in output.split('\n'):
        words = shlex.split(line.strip())
        if len(words) == 3:
            guid = words[1]
            identity = words[2]
            dev = identity.split(':')[0]
            configuration_context.env.append_unique('MAC_SIGNING_IDENTITIES', [(dev, guid, identity)])
