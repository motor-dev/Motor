import hashlib
import waflib.Errors
import waflib.Node
import waflib.TaskGen
from typing import List, Set, Tuple, Union


def unique(seq: List[str]) -> List[str]:
    seen = set()  # type: Set[str]
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


def gather_includes_defines(task_gen: waflib.TaskGen.task_gen) -> Tuple[List[str], List[str]]:
    defines = getattr(task_gen, 'defines', []) + getattr(task_gen, 'export_defines',
                                                         []) + getattr(task_gen, 'extra_defines', [])
    includes = getattr(task_gen, 'includes', []) + getattr(task_gen, 'export_includes',
                                                           []) + getattr(task_gen, 'extra_includes', [])
    seen = set([])
    use = getattr(task_gen, 'use', []) + getattr(task_gen, 'private_use', [])
    while use:
        name = use.pop()
        if name not in seen:
            seen.add(name)
            try:
                t = task_gen.bld.get_tgen_by_name(name)
            except waflib.Errors.WafError:
                pass
            else:
                use = use + getattr(t, 'use', [])
                includes += getattr(t, 'includes', [])
                includes += getattr(t, 'export_includes', [])
                includes += getattr(t, 'export_system_includes', [])
                includes += getattr(task_gen, 'extra_includes', [])
                defines = defines + getattr(t, 'defines', []) + getattr(t, 'export_defines',
                                                                        []) + getattr(task_gen, 'extra_defines', [])
    return unique(includes), unique(defines)


def path_from(path: Union[str, waflib.Node.Node], node: waflib.Node.Node) -> str:
    if isinstance(path, str):
        return path.replace('\\', '/')
    else:
        return path.path_from(node).replace('\\', '/')


def generate_guid(name: str) -> str:
    """This generates a dummy GUID for the sln file to use.  It is
    based on the MD5 signatures of the sln filename plus the name of
    the project.  It basically just needs to be unique, and not
    change with each invocation."""
    d = hashlib.md5(str(name).encode()).hexdigest().upper()
    # convert most of the signature to GUID form (discard the rest)
    d = "{" + d[:8] + "-" + d[8:12] + "-" + d[12:16] + "-" + d[16:20] + "-" + d[20:32] + "}"
    return d
