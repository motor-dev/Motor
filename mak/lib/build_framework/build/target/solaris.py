import waflib.TaskGen
from ...options import BuildContext


@waflib.TaskGen.feature('cxxprogram')
def set_solaris_rpath_program(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'solaris' in task_gen.env.VALID_PLATFORMS:
        task_gen.env.RPATH = [
            ':'.join(
                ['$ORIGIN', '$ORIGIN/../lib/', '$ORIGIN/../lib/motor/'] +
                ['$ORIGIN/../lib/%s' % target for target in task_gen.env.TARGETS] +
                ['$ORIGIN/../lib/%s/motor' % target for target in task_gen.env.TARGETS]
            )
        ]


@waflib.TaskGen.feature('cxxshlib')
def set_solaris_rpath_cxxshlib(task_gen: waflib.TaskGen.task_gen) -> None:
    if 'solaris' in task_gen.env.VALID_PLATFORMS:
        if 'motor:kernel' in task_gen.features or 'motor:plugin' in task_gen.features:
            task_gen.env.RPATH = ['$ORIGIN:$ORIGIN/../']
        else:
            task_gen.env.RPATH = [':'.join(['$ORIGIN', '$ORIGIN/motor/'])]


def setup_build_solaris(_: BuildContext) -> None:
    pass
