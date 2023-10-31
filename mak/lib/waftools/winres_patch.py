import os
import waflib.Configure
import waflib.Task
import waflib.Tools.winres
from typing import Any, List, Union


class winrc(waflib.Tools.winres.winrc):

    def exec_command(self, cmd: Union[str, List[str]], **kw: Any) -> int:
        if os.sep == '\\':
            if isinstance(cmd, list):
                cmd = [i.replace('\\', '/') for i in cmd]
        return waflib.Tools.winres.winrc.exec_command(self, cmd, **kw)


def configure(configuration_context: waflib.Configure.ConfigurationContext) -> None:
    configuration_context.load(['winres'])
    v = configuration_context.env
    if v.CC_NAME == 'msvc':
        v.WINRC_TGT_F = '/fo'
        v.WINRC_SRC_F = ''
    else:
        v.WINRC_TGT_F = '-o'
        v.WINRC_SRC_F = '-i'
