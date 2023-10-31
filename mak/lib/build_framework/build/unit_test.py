import waflib.Build
import waflib.TaskGen
import waflib.Task
import waflib.Options


class unit_test(waflib.Task.Task):
    color = 'PINK'

    def sig_vars(self) -> None:
        # re-run if the fail unittest flag has changed
        self.m.update(str(waflib.Options.options.fail_on_unittest).encode('utf-8'))

    def run(self) -> int:
        result = self.exec_command([self.inputs[0].abspath()])
        if waflib.Options.options.fail_on_unittest:
            return result
        else:
            return 0


@waflib.TaskGen.feature('motor:unit_test')
@waflib.TaskGen.after_method('apply_link')
@waflib.TaskGen.after_method('install_step')
def check_unit_test(task_gen: waflib.TaskGen.task_gen) -> None:
    if task_gen.env.RUN_UNIT_TESTS and False:
        postlink_task = getattr(task_gen, 'postlink_task')  # type: waflib.Task.Task
        task = task_gen.create_task('unit_test', [postlink_task.outputs[0]])
        task.set_run_after(postlink_task)


def setup_unit_test(_: waflib.Build.BuildContext) -> None:
    pass
