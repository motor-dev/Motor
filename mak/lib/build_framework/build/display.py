import waflib.Build
import waflib.Logs
import waflib.Options
import waflib.Task
import waflib.Tools.ccroot

from typing import Optional

old_log_display = waflib.Task.Task.log_display


def _to_string(task: waflib.Task.Task) -> str:
    if task.outputs:
        tgt_str = '/' + task.outputs[0].name
    elif task.inputs:
        tgt_str = '/' + task.inputs[0].name
    else:
        tgt_str = ''
    task_name = task.__class__.__name__
    if task_name.endswith('_task'):
        task_name = task_name[:-5]
    return '{%s}%s%s%s' % (task_name, (20 - len(task_name)) * ' ', task.generator.target, tgt_str)


def _log_display(task: waflib.Task.Task, build_context: waflib.Build.BuildContext) -> None:
    if waflib.Options.options.silent:
        return
    s = task.display()
    if s:
        if build_context.logger:
            logger = build_context.logger
        else:
            logger = waflib.Logs.log
        logger.info(s, extra={'terminator': '', 'c1': '', 'c2': ''})


def _display(task: waflib.Task.Task) -> Optional[str]:
    bld = task.generator.bld
    col1 = waflib.Logs.colors(task.color)
    col2 = waflib.Logs.colors.NORMAL
    master = bld.producer

    if bld.progress_bar >= 1:
        bld.set_status_line(bld.progress_line(master.processed - master.ready.qsize(), master.total, col1, col2))
    if bld.progress_bar == 2:
        return None

    s = str(task)
    if not s:
        return None

    total = master.total
    n = len(str(total))
    fs = '[%%%dd/%%%dd] %%s%%s%%s%%s\n' % (n, n)
    kw = task.keyword()
    if kw:
        kw += ' '
    return fs % (master.processed - master.ready.qsize(), total, kw, col1, s, col2)


setattr(waflib.Task.Task, '__str__', _to_string)
setattr(waflib.Task.Task, 'display', _display)
setattr(waflib.Task.Task, 'log_display', _log_display)
setattr(waflib.Task.Task, 'keyword', (lambda self: ''))


def setup_display(_: waflib.Build.BuildContext) -> None:
    pass
