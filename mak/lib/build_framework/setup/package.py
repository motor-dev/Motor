import tarfile
import shutil
import stat
import os
import tempfile
import time
import waflib.Errors
import waflib.Logs
import waflib.Node
from ..options import SetupContext

from patch import fromfile, setdebug
from urllib import request
from urllib.error import HTTPError
from typing import Any, Callable, List, Optional, Tuple


def _remove_readonly(func: Callable[[str], None], path: str, _: Any) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
}


def pkg_unpack(
        setup_context: SetupContext,
        package_id_template: str,
        package_url: str,
        patch_list: Optional[List[waflib.Node.Node]] = None
) -> waflib.Node.Node:
    args = {}
    if setup_context.env.VALID_PLATFORMS:
        args['platform'] = setup_context.env.VALID_PLATFORMS[0]
    if setup_context.env.VALID_ARCHITECTURES:
        archs = (setup_context.env.VALID_ARCHITECTURES[0], 'multiarch')  # type: Tuple[str,...]
    else:
        archs = ('multiarch',)
    if setup_context.env.COMPILER_NAME:
        args['compiler'] = setup_context.env.COMPILER_NAME
    if setup_context.env.COMPILER_ABI:
        args['abi'] = setup_context.env.COMPILER_ABI
    found = False
    package = None
    error = None  # type: Optional[Exception]
    for arch in archs:
        args['arch'] = arch

        package_id = package_id_template % args
        if package_id in setup_context.package_env.PACKAGE_REPOS:
            pkg_node = setup_context.package_node.make_node(
                setup_context.package_env.PACKAGE_REPOS[package_id]
            )
            if pkg_node.isdir():
                return pkg_node

        for i in range(0, 3):
            try:
                package = request.urlopen(request.Request(package_url % args, headers=headers))
            except HTTPError as e:
                error = e
                if e.code == 404:
                    break
                time.sleep(2)
            except Exception as e:
                error = e
            else:
                found = True
                break
        else:
            raise waflib.Errors.WafError('failed to download package "%s": %s' % (package_url, error))
        if found:
            break
    else:
        raise waflib.Errors.WafError('failed to download package "%s": %s' % (package_url, error))

    assert package is not None
    try:
        shutil.rmtree(os.path.join(setup_context.package_node.abspath(), package_id), onerror=_remove_readonly)
    except OSError:
        pass

    with tempfile.TemporaryFile(mode='w+b') as archive_file:
        waflib.Logs.pprint('PINK', 'downloading...', sep=' ')
        archive_file.write(package.read())
        archive_file.seek(0)
        waflib.Logs.pprint('PINK', 'unpacking...', sep=' ')
        archive = tarfile.open(fileobj=archive_file, mode='r')
        info = archive.getmembers()[0]
        root_path = info.name
        archive.extractall(path=os.path.join(setup_context.package_node.abspath(), package_id))
        if patch_list:
            for patch in patch_list:
                waflib.Logs.pprint('PINK', 'patching %s...' % patch.name, sep=' ')
                patch_object = fromfile(patch.abspath())
                if patch_object is not False:
                    patch_object.apply(1,
                                       setup_context.package_node.make_node(
                                           os.path.join(package_id, root_path)).abspath())
                else:
                    waflib.Logs.pprint('RED', 'error!')
                    setdebug()
                    fromfile(patch.abspath())
    setup_context.package_env.PACKAGE_REPOS[package_id] = os.path.join(package_id, root_path)
    return setup_context.package_node.make_node(os.path.join(package_id, root_path))


def multiarch_setup_package(setup_context: SetupContext) -> None:
    setup_context.package_env = setup_context.all_envs['packages']
    setup_context.package_node = setup_context.bldnode.make_node('packages')
    setup_context.package_node.mkdir()
