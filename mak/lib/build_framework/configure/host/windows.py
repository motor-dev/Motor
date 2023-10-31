import os
import tarfile
import tempfile
import waflib.Configure
import waflib.Errors
import waflib.Logs
from urllib import request

HOST_WIN32_TOOLS = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/host-win32.tgz'


def configure_host_windows(configuration_context: waflib.Configure.ConfigurationContext) -> None:
    path = configuration_context.bldnode.make_node('host/win32')
    if not os.path.isdir(path.abspath()):
        configuration_context.start_msg('setting up Win32 tools')
        path.parent.mkdir()
        try:
            pkg = request.urlopen(HOST_WIN32_TOOLS)
        except Exception as e:
            raise waflib.Errors.WafError('failed to download package "%s": %s' % (HOST_WIN32_TOOLS, e))
        with tempfile.TemporaryFile(mode='w+b') as archive_file:
            waflib.Logs.pprint('PINK', 'downloading...', sep=' ')
            archive_file.write(pkg.read())
            archive_file.seek(0)
            waflib.Logs.pprint('PINK', 'unpacking...', sep=' ')
            archive = tarfile.open(fileobj=archive_file, mode='r')
            archive.extractall(path.parent.abspath())
            configuration_context.end_msg('OK')

    environ = getattr(configuration_context, 'environ', os.environ)
    environ['PATH'] = os.pathsep.join([os.path.join(path.abspath(), 'bin'), environ['PATH']])
