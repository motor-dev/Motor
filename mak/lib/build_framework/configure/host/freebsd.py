import os
import sys
import waflib.Configure
import waflib.Options
import waflib.Utils
from typing import List, Union, Tuple


def _add_ld_so(filename: str, paths: List[str]) -> None:
    f = open(filename, 'r')
    for line in f:
        line = line.strip()
        if not line:
            continue
        elif line.startswith('#'):
            continue
        elif line.startswith('include'):
            continue
        elif os.path.isdir(line):
            paths.append(line)


def configure_host_freebsd(configuration_context: waflib.Configure.ConfigurationContext) -> None:
    lib_paths = []  # type: List[str]
    if os.path.isfile('/etc/ld.so.conf'):
        _add_ld_so('/etc/ld.so.conf', lib_paths)
    if os.path.isdir('/etc/ld.so.conf.d'):
        for f in sorted(os.listdir('/etc/ld.so.conf.d')):
            _add_ld_so('/etc/ld.so.conf.d/' + f, lib_paths)
    configuration_context.env.ALL_ARCH_LIBPATHS = lib_paths
    try:
        p = waflib.Utils.subprocess.Popen(['/usr/bin/cc', '-v'], stdout=waflib.Utils.subprocess.PIPE,
                                          stderr=waflib.Utils.subprocess.PIPE)
        out, err = p.communicate()  # type: Tuple[Union[str, bytes], Union[str, bytes]]
    except OSError:
        pass
    else:
        if not isinstance(out, str):
            out = out.decode(sys.stdout.encoding)
        if not isinstance(err, str):
            err = err.decode(sys.stderr.encoding)
        for line in out.split('\n') + err.split('\n'):
            if line.startswith('Target: '):
                configuration_context.env.FREEBSD_HOST_TRIPLE = line[8:]
