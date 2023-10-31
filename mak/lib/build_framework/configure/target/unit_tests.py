import waflib.Errors
import waflib.Task
import waflib.TaskGen
import waflib.Tools.c_config
from ...options import ConfigurationContext


class run_test_exe(waflib.Task.Task):
    color = 'PINK'

    def run(self) -> int:
        return self.exec_command([self.inputs[0].abspath()])


@waflib.TaskGen.feature('check_unit_test')
@waflib.TaskGen.after_method('apply_link')
def check_run_exe(task_gen: waflib.TaskGen.task_gen) -> None:
    link_task = getattr(task_gen, 'link_task')  # type: waflib.Task.Task
    task = task_gen.create_task('run_test_exe', [link_task.outputs[0]])
    task.set_run_after(link_task)


def setup_unit_tests(configuration_context: ConfigurationContext) -> None:
    configuration_context.env.BUILD_UNIT_TESTS = True
    try:
        waflib.Tools.c_config.check(
            configuration_context,
            msg='Checking if unit tests can be run on host',
            features=['check_unit_test', 'c', 'cprogram'],
            fragment='int main() { return 0; }'
        )
    except waflib.Errors.WafError:
        pass
    else:
        configuration_context.env.RUN_UNIT_TESTS = True
