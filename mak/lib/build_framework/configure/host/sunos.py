import os
import waflib.Configure


def configure_host_sunos(configuration_context: waflib.Configure.ConfigurationContext) -> None:
    os.environ['LD_NOVERSION'] = '1'
    environ = getattr(configuration_context, 'environ')
    if environ:
        environ['LD_NOVERSION'] = '1'
    try:
        for extra in os.listdir('/opt'):
            configuration_context.env.append_unique('EXTRA_PATH', os.path.join('/opt', extra, 'bin'))
    except OSError:
        pass
    try:
        for gcc_version in os.listdir('/usr/gcc/'):
            configuration_context.env.append_unique('EXTRA_PATH', os.path.join('/usr', 'gcc', gcc_version, 'bin'))
    except OSError:
        pass
